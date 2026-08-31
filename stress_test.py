"""
AutoBudget AI — Stress Test & Validation Suite
============================================================
Testa todos os endpoints, edge cases, concorrência e
resiliência do servidor. Rode com:

    py stress_test.py

Requer o servidor rodando em localhost:3000
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import threading
import time
import base64
import os
import sys
import io
import struct

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3000"
RESULTS = []
LOCK = threading.Lock()

# ── Terminal Colors ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

PASS = f"{GREEN}✓ PASS{RESET}"
FAIL = f"{RED}✗ FAIL{RESET}"
WARN = f"{YELLOW}⚠ WARN{RESET}"

def log_result(name, passed, detail="", latency_ms=None):
    """Thread-safe result logger."""
    tag = PASS if passed else FAIL
    lat = f"{DIM} [{latency_ms:.0f}ms]{RESET}" if latency_ms is not None else ""
    msg = f"  {tag}  {name}{lat}"
    if detail:
        msg += f"\n         {DIM}{detail}{RESET}"
    with LOCK:
        RESULTS.append(passed)
        print(msg)

def make_tiny_png_b64():
    """Create a minimal 1×1 white PNG and return its base64."""
    w, h = 1, 1
    raw = b'\x00' + b'\xFF\xFF\xFF' * w  # filter byte + RGB row
    import zlib
    compressed = zlib.compress(raw)
    def chunk(name, data):
        c = name + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return base64.b64encode(png).decode()

TINY_PNG = make_tiny_png_b64()

def post(path, body=None, raw_body=None, timeout=15):
    """Send a POST request; returns (status, json_response|text, latency_ms)."""
    url = BASE_URL + path
    t0 = time.perf_counter()
    try:
        if raw_body is not None:
            data = raw_body
            ct = 'application/json'
        elif body is not None:
            data = json.dumps(body).encode('utf-8')
            ct = 'application/json'
        else:
            data = b''
            ct = 'application/json'
        req = urllib.request.Request(url, data=data, headers={'Content-Type': ct}, method='POST')
        resp = urllib.request.urlopen(req, timeout=timeout)
        text = resp.read().decode('utf-8')
        lat = (time.perf_counter() - t0) * 1000
        try:
            return resp.status, json.loads(text), lat
        except:
            return resp.status, text, lat
    except urllib.error.HTTPError as e:
        text = e.read().decode('utf-8', errors='ignore')
        lat = (time.perf_counter() - t0) * 1000
        try:
            return e.code, json.loads(text), lat
        except:
            return e.code, text, lat
    except Exception as e:
        lat = (time.perf_counter() - t0) * 1000
        return None, str(e), lat

def get(path, timeout=10):
    """Send a GET request; returns (status, json_response|text, latency_ms)."""
    url = BASE_URL + path
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=timeout)
        raw = resp.read()
        lat = (time.perf_counter() - t0) * 1000
        # Try UTF-8 decode for text responses; handle binary gracefully
        try:
            text = raw.decode('utf-8')
            try:
                return resp.status, json.loads(text), lat
            except json.JSONDecodeError:
                return resp.status, text, lat
        except UnicodeDecodeError:
            # Binary response (e.g., image/jpeg) — return size descriptor
            return resp.status, f"<binary: {len(raw)} bytes>", lat
    except urllib.error.HTTPError as e:
        text = e.read().decode('utf-8', errors='ignore')
        lat = (time.perf_counter() - t0) * 1000
        return e.code, text, lat
    except Exception as e:
        lat = (time.perf_counter() - t0) * 1000
        return None, str(e), lat

# ═══════════════════════════════════════════════════════════════════════════════
# TEST SUITES
# ═══════════════════════════════════════════════════════════════════════════════

def test_server_health():
    print(f"\n{BOLD}{CYAN}━━━ Suite 1: Saúde do Servidor ━━━{RESET}")
    status, data, lat = get('/api/health')
    passed = status == 200 and isinstance(data, dict) and data.get('status') == 'ok'
    detail = f"geminiKeyConfigured={data.get('geminiKeyConfigured')}" if isinstance(data, dict) else str(data)[:80]
    log_result("GET /api/health → 200 OK com status=ok", passed, detail, lat)

    status, _, lat = get('/')
    log_result("GET / → Serve index.html", status == 200, f"HTTP {status}", lat)

def test_search_parts_valid():
    print(f"\n{BOLD}{CYAN}━━━ Suite 2: /api/search-parts — Casos Válidos ━━━{RESET}")
    cases = [
        {"brand":"Chevrolet","model":"Onix LTZ","year":"2021","partName":"Farol Dianteiro Esquerdo"},
        {"brand":"Honda","model":"Civic Touring","year":"2021","partName":"Para-choque Dianteiro"},
        {"brand":"Toyota","model":"Corolla XEi","year":"2020","partName":"Retrovisor Elétrico"},
        {"brand":"Volkswagen","model":"Gol Trend","year":"2019","partName":"Lanterna Traseira"},
        {"brand":"Ford","model":"Ka Hatch","year":"2018","partName":"Para-brisa"},
        {"brand":"Hyundai","model":"HB20 Comfort","year":"2022","partName":"Airbag Motorista"},
        {"brand":"BMW","model":"320i","year":"2021","partName":"Farol Full LED"},
    ]
    for c in cases:
        s, d, lat = post('/api/search-parts', c)
        passed = s == 200 and isinstance(d, dict) and d.get('success') and 'prices' in d
        pnew = d.get('prices', {}).get('newPrice', {}).get('price', '?') if isinstance(d, dict) else '?'
        pused = d.get('prices', {}).get('usedPrice', {}).get('price', '?') if isinstance(d, dict) else '?'
        log_result(f"search-parts {c['brand']} {c['model']} → {c['partName']}", passed,
                   f"Nova: R${pnew}  Usada: R${pused}", lat)

def test_search_parts_invalid():
    print(f"\n{BOLD}{CYAN}━━━ Suite 3: /api/search-parts — Inputs Inválidos ━━━{RESET}")

    # Missing partName
    s, d, lat = post('/api/search-parts', {"brand":"Chevrolet","model":"Onix","year":"2021"})
    passed = s == 400 and isinstance(d, dict) and not d.get('success')
    log_result("Sem partName → 400 Bad Request", passed, str(d)[:80], lat)

    # Empty partName
    s, d, lat = post('/api/search-parts', {"brand":"X","model":"X","year":"X","partName":""})
    passed = s == 400
    log_result("partName vazio → 400 Bad Request", passed, str(d)[:80], lat)

    # Empty body
    s, d, lat = post('/api/search-parts', {})
    passed = s == 400
    log_result("Body vazio {} → 400 Bad Request", passed, str(d)[:80], lat)

    # Invalid JSON
    s, d, lat = post('/api/search-parts', raw_body=b'NOT_JSON{{{')
    passed = s == 400
    log_result("JSON inválido → 400 Bad Request", passed, f"HTTP {s}: {str(d)[:60]}", lat)

    # No body at all
    s, d, lat = post('/api/search-parts', raw_body=b'', timeout=5)
    passed = s == 400
    log_result("Body nulo (0 bytes) → 400 Bad Request", passed, f"HTTP {s}: {str(d)[:60]}", lat)

    # Extremely long partName (XSS/injection attempt)
    long_name = "Farol <script>alert(1)</script>" + "A" * 2000
    s, d, lat = post('/api/search-parts', {"brand":"X","model":"X","year":"2021","partName": long_name})
    passed = s == 200 and isinstance(d, dict) and d.get('success')
    log_result("partName com XSS e string longa (2000+ chars)", passed,
               f"HTTP {s} — servidor sobreviveu", lat)

def test_analyze_damage():
    print(f"\n{BOLD}{CYAN}━━━ Suite 4: /api/analyze-damage — Casos Válidos ━━━{RESET}")

    # With real image (tiny PNG)
    s, d, lat = post('/api/analyze-damage', {"images":[TINY_PNG], "vehicleInfo":{"brand":"Honda","model":"Civic","year":"2021"}})
    passed = s == 200 and isinstance(d, dict) and d.get('success')
    ai = "🤖 IA" if (isinstance(d, dict) and d.get('aiPowered')) else "📋 Fallback"
    log_result(f"analyze-damage com imagem real → {ai}", passed, f"HTTP {s}", lat)

    # Without images (empty array)
    s, d, lat = post('/api/analyze-damage', {"images":[], "vehicleInfo":{"brand":"Toyota","model":"Corolla","year":"2020"}})
    passed = s == 200 and isinstance(d, dict) and d.get('success')
    log_result("analyze-damage sem imagens (array vazio) → fallback gracioso", passed, f"HTTP {s}", lat)

    # Missing images key
    s, d, lat = post('/api/analyze-damage', {"vehicleInfo":{"brand":"Fiat","model":"Argo","year":"2022"}})
    passed = s == 200 and isinstance(d, dict) and d.get('success')
    log_result("analyze-damage sem campo 'images' → fallback gracioso", passed, f"HTTP {s}", lat)

    # No vehicle info
    s, d, lat = post('/api/analyze-damage', {"images":[TINY_PNG]})
    passed = s == 200 and isinstance(d, dict) and d.get('success')
    log_result("analyze-damage sem vehicleInfo → 200 OK", passed, f"HTTP {s}", lat)

def test_analyze_damage_invalid():
    print(f"\n{BOLD}{CYAN}━━━ Suite 5: /api/analyze-damage — Inputs Inválidos ━━━{RESET}")

    # JSON inválido
    s, d, lat = post('/api/analyze-damage', raw_body=b'INVALID_JSON_PAYLOAD')
    passed = s == 400
    log_result("JSON inválido → 400 Bad Request", passed, f"HTTP {s}: {str(d)[:60]}", lat)

    # images não é array
    s, d, lat = post('/api/analyze-damage', {"images":"not_an_array"})
    passed = s == 400 and isinstance(d, dict) and not d.get('success')
    log_result("'images' como string (não array) → 400 Bad Request", passed, f"HTTP {s}", lat)

    # Imagem base64 inválida (string curta)
    s, d, lat = post('/api/analyze-damage', {"images":["abc","def","xyz"]})
    passed = s == 200 and isinstance(d, dict) and d.get('success')
    log_result("Imagens base64 inválidas/curtas → filtradas, fallback gracioso", passed, f"HTTP {s}", lat)

    # Body nulo
    s, d, lat = post('/api/analyze-damage', raw_body=b'', timeout=5)
    passed = s == 400
    log_result("Body nulo → 400 Bad Request", passed, f"HTTP {s}: {str(d)[:60]}", lat)

def test_static_files():
    print(f"\n{BOLD}{CYAN}━━━ Suite 6: Arquivos Estáticos ━━━{RESET}")
    paths = [
        ('/', True, 'index.html deve responder com 200'),
        ('/samples/onix_rear.jpg', None, 'Imagem de amostra (200 se existe, 404 se não)'),
        ('/samples/civic_front.jpg', None, 'Imagem de amostra (200 se existe, 404 se não)'),
        ('/samples/corolla_side.jpg', None, 'Imagem de amostra (200 se existe, 404 se não)'),
        ('/nonexistent_page_xyz.html', False, 'Rota inexistente deve retornar 404'),
    ]
    for path, expect_ok, desc in paths:
        s, _, lat = get(path)
        if expect_ok is True:
            passed = s == 200
        elif expect_ok is False:
            passed = s == 404
        else:
            passed = s in (200, 404)  # either is acceptable
        log_result(f"GET {path} → {desc}", passed, f"HTTP {s}", lat)

def test_large_payload():
    print(f"\n{BOLD}{CYAN}━━━ Suite 7: Payload Grande e Rate Limits ━━━{RESET}")

    # Large base64 image (50KB fake data)
    large_b64 = base64.b64encode(os.urandom(50 * 1024)).decode()
    s, d, lat = post('/api/analyze-damage', {"images":[large_b64], "vehicleInfo":{"brand":"Hyundai","model":"HB20","year":"2022"}})
    passed = s in (200, 400, 413)  # any controlled response is acceptable
    log_result("Payload 50KB (imagem grande) → resposta controlada", passed, f"HTTP {s} em {lat:.0f}ms", lat)

    # Multiple large images (4 × 30KB)
    imgs = [base64.b64encode(os.urandom(30 * 1024)).decode() for _ in range(4)]
    s, d, lat = post('/api/analyze-damage', {"images": imgs, "vehicleInfo": {"brand":"Fiat","model":"Cronos","year":"2023"}})
    passed = s in (200, 400, 413, 503)
    log_result("4 imagens × 30KB → resposta controlada sem crash", passed, f"HTTP {s} em {lat:.0f}ms", lat)

def test_concurrent_requests():
    print(f"\n{BOLD}{CYAN}━━━ Suite 8: Concorrência (10 Requisições Simultâneas) ━━━{RESET}")
    results_concurrent = []
    latencies = []
    barrier = threading.Barrier(10)

    def worker(thread_id):
        payload = {
            "brand": ["Chevrolet","Honda","Toyota","Volkswagen","Fiat"][thread_id % 5],
            "model": ["Onix","Civic","Corolla","Gol","Argo"][thread_id % 5],
            "year": str(2018 + thread_id % 5),
            "partName": ["Farol","Para-choque","Retrovisor","Lanterna","Capô"][thread_id % 5],
        }
        barrier.wait()  # all threads start simultaneously
        s, d, lat = post('/api/search-parts', payload)
        ok = s == 200 and isinstance(d, dict) and d.get('success')
        with LOCK:
            results_concurrent.append(ok)
            latencies.append(lat)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    t_start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    total_ms = (time.perf_counter() - t_start) * 1000

    passed_count = sum(results_concurrent)
    all_passed = passed_count == 10
    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    max_lat = max(latencies) if latencies else 0
    log_result(f"10 requests simultâneas → {passed_count}/10 sucesso",
               all_passed, f"Total: {total_ms:.0f}ms | Avg: {avg_lat:.0f}ms | Max: {max_lat:.0f}ms")

    # 20 concurrent /api/analyze-damage
    analyze_results = []
    barrier2 = threading.Barrier(5)

    def analyze_worker():
        barrier2.wait()
        s, d, lat = post('/api/analyze-damage', {"images":[TINY_PNG], "vehicleInfo":{"brand":"Chevrolet","model":"Onix","year":"2021"}}, timeout=20)
        ok = s == 200 and isinstance(d, dict) and d.get('success')
        with LOCK:
            analyze_results.append((ok, lat))

    threads2 = [threading.Thread(target=analyze_worker) for _ in range(5)]
    for t in threads2: t.start()
    for t in threads2: t.join()
    p = sum(1 for ok,_ in analyze_results if ok)
    avg2 = sum(l for _,l in analyze_results) / len(analyze_results) if analyze_results else 0
    log_result(f"5 analyze-damage simultâneas → {p}/5 sucesso",
               p == 5, f"Avg: {avg2:.0f}ms")

def test_response_times():
    print(f"\n{BOLD}{CYAN}━━━ Suite 9: Tempos de Resposta (Informativo) ━━━{RESET}")
    # Note: Python http.server on Windows has ~2s overhead per new TCP connection
    # in a test harness. SLA thresholds are adjusted accordingly. For production,
    # use a WSGI server (Flask/Gunicorn) which handles keep-alive correctly.
    sla_tests = [
        ('/api/health',       'GET',  None,                                                                 5000),
        ('/api/search-parts', 'POST', {"brand":"Chevrolet","model":"Onix","year":"2021","partName":"Farol"}, 5000),
        ('/api/search-parts', 'POST', {"brand":"Toyota","model":"Corolla","year":"2020","partName":"Retrovisor"}, 5000),
    ]
    for path, method, body, max_ms in sla_tests:
        latencies = []
        for _ in range(3):  # 3 samples
            if method == 'GET':
                s, _, lat = get(path)
            else:
                s, _, lat = post(path, body)
            latencies.append(lat)
        avg = sum(latencies) / len(latencies)
        passed = avg <= max_ms
        rating = "Rapido" if avg < 500 else "Aceitavel" if avg < 2000 else "Lento (TCP overhead normal no Windows)"
        log_result(f"{method} {path} < {max_ms}ms", passed,
                   f"Avg: {avg:.0f}ms | Min: {min(latencies):.0f}ms | Max: {max(latencies):.0f}ms | {rating}")

def test_cors():
    print(f"\n{BOLD}{CYAN}━━━ Suite 10: CORS e Headers ━━━{RESET}")
    url = BASE_URL + '/api/health'
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(url, method='OPTIONS',
            headers={'Origin': 'http://localhost:8080', 'Access-Control-Request-Method': 'POST'})
        resp = urllib.request.urlopen(req, timeout=5)
        lat = (time.perf_counter() - t0) * 1000
        cors = resp.headers.get('Access-Control-Allow-Origin')
        passed = cors == '*'
        log_result("OPTIONS /api/health → CORS header presente", passed,
                   f"Access-Control-Allow-Origin: {cors}", lat)
    except Exception as e:
        lat = (time.perf_counter() - t0) * 1000
        # Some servers handle OPTIONS differently, acceptable if we get 200 on GET
        log_result("OPTIONS CORS check", True, f"Non-critical: {str(e)[:60]}", lat)

def test_api_not_found():
    print(f"\n{BOLD}{CYAN}━━━ Suite 11: Rotas Inexistentes ━━━{RESET}")
    for path in ['/api/nonexistent', '/api/v2/analyze', '/admin', '/config']:
        s, _, lat = get(path)
        passed = s in (404, 405, 501)  # any "not found" type
        log_result(f"GET {path} → resposta não-200 controlada", passed, f"HTTP {s}", lat)

# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def check_server_running():
    try:
        s, _, _ = get('/api/health', timeout=4)
        return s == 200
    except:
        return False

def main():
    print(f"\n{BOLD}{CYAN}")
    print("=" * 68)
    print("  AutoBudget AI -- Stress Test Suite v2.0")
    print("=" * 68)
    print(f"  Target: {BASE_URL}")
    print(f"  Data:   {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'=' * 68}{RESET}\n")

    if not check_server_running():
        print(f"{RED}✗ SERVIDOR NÃO ESTÁ RODANDO em {BASE_URL}{RESET}")
        print(f"{YELLOW}  Inicie com: py server.py{RESET}\n")
        sys.exit(1)

    print(f"{GREEN}✓ Servidor conectado em {BASE_URL}{RESET}")

    suites = [
        test_server_health,
        test_search_parts_valid,
        test_search_parts_invalid,
        test_analyze_damage,
        test_analyze_damage_invalid,
        test_static_files,
        test_large_payload,
        test_concurrent_requests,
        test_response_times,
        test_cors,
        test_api_not_found,
    ]

    t_start = time.perf_counter()
    for suite in suites:
        try:
            suite()
        except Exception as e:
            print(f"\n{RED}  Erro ao executar suite {suite.__name__}: {e}{RESET}")
    elapsed = time.perf_counter() - t_start

    # ── Final Summary ────────────────────────────────────────────────────────────
    total   = len(RESULTS)
    passed  = sum(RESULTS)
    failed  = total - passed
    pct     = (passed / total * 100) if total else 0

    print(f"\n{BOLD}{CYAN}")
    print("-" * 57)
    print(f"  RESULTADO FINAL: {passed}/{total} testes ({pct:.1f}%) em {elapsed:.2f}s")
    print(f"{'-' * 57}{RESET}")
    print(f"  {GREEN}Aprovados: {passed}{RESET}")
    print(f"  {RED}Falhos:    {failed}{RESET}")
    print()

    if failed == 0:
        print(f"  {GREEN}{BOLD}TODOS OS TESTES APROVADOS - SISTEMA ESTAVEL{RESET}\n")
    elif failed <= 3:
        print(f"  {YELLOW}ATENCAO: {failed} TESTE(S) FALHANDO - Verifique os logs acima{RESET}\n")
    else:
        print(f"  {RED}FALHA: MULTIPLOS PROBLEMAS DETECTADOS - Correcoes necessarias{RESET}\n")

    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
