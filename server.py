import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
import http.server
import socketserver
import json
import urllib.parse
import urllib.request
import urllib.error
import os
import re
import base64
import time
import threading

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(DIRECTORY, 'public')

# Load .env file if present
def load_env():
    env_path = os.path.join(DIRECTORY, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# ─── Real Market Price Table (Mercado Livre BR calibrated) ─────────────────────
REAL_MARKET_PRICES = {
    'geral': {
        'farol': {'new': 980, 'used': 480, 'supplier': 'CDV Desmanche Credenciado DETRAN'},
        'lanterna': {'new': 700, 'used': 340, 'supplier': 'Desmanche Credenciado DETRAN'},
        'para-choque': {'new': 650, 'used': 320, 'supplier': 'Recuperadora Credenciada BR'},
        'parachoque': {'new': 650, 'used': 320, 'supplier': 'Recuperadora Credenciada BR'},
        'porta': {'new': 1500, 'used': 720, 'supplier': 'CDV Leilão & Peças SP'},
        'retrovisor': {'new': 620, 'used': 300, 'supplier': 'Desmanche Credenciado DETRAN'},
        'capô': {'new': 1400, 'used': 650, 'supplier': 'CDV Peças Originais'},
        'capo': {'new': 1400, 'used': 650, 'supplier': 'CDV Peças Originais'},
        'paralama': {'new': 480, 'used': 240, 'supplier': 'Eco Auto Peças'},
        'vidro': {'new': 550, 'used': 270, 'supplier': 'Auto Vidros BR'},
        'grade': {'new': 420, 'used': 210, 'supplier': 'CDV Honda Peças'},
        'para-brisa': {'new': 850, 'used': 420, 'supplier': 'Auto Vidros Credenciados'},
        'parabrisa': {'new': 850, 'used': 420, 'supplier': 'Auto Vidros Credenciados'},
        'chassi': {'new': 3500, 'used': 1800, 'supplier': 'Desmanche Credenciado DETRAN'},
        'suspensao': {'new': 1200, 'used': 580, 'supplier': 'CDV Mecânica e Peças'},
        'suspensão': {'new': 1200, 'used': 580, 'supplier': 'CDV Mecânica e Peças'},
        'radiador': {'new': 900, 'used': 420, 'supplier': 'CDV Arrefecimento BR'},
        'longarina': {'new': 2200, 'used': 1100, 'supplier': 'Desmanche Estrutural DETRAN'},
        'travessa': {'new': 980, 'used': 480, 'supplier': 'CDV Desmanche SP'},
        'roda': {'new': 650, 'used': 280, 'supplier': 'CDV Rodas & Aro SP'},
        'pneu': {'new': 450, 'used': 120, 'supplier': 'Borracharia Credenciada BR'},
        'air bag': {'new': 2200, 'used': 950, 'supplier': 'CDV Segurança Automotiva'},
        'airbag': {'new': 2200, 'used': 950, 'supplier': 'CDV Segurança Automotiva'},
    },
    'onix': {
        'farol': {'new': 890, 'used': 499, 'supplier': 'CDV Desmanche Credenciado DETRAN SP'},
        'lanterna': {'new': 780, 'used': 390, 'supplier': 'Auto Peças Desmanche Autorizado GM'},
        'para-choque': {'new': 680, 'used': 380, 'supplier': 'Recuperadora Sucatas BR'},
        'parachoque': {'new': 680, 'used': 380, 'supplier': 'Recuperadora Sucatas BR'},
        'porta': {'new': 1450, 'used': 680, 'supplier': 'CDV Leilão & Peças SP'},
        'retrovisor': {'new': 550, 'used': 280, 'supplier': 'Desmanche Credenciado DETRAN'},
        'capô': {'new': 1250, 'used': 590, 'supplier': 'CDV Peças Originais GM'},
        'capo': {'new': 1250, 'used': 590, 'supplier': 'CDV Peças Originais GM'},
    },
    'civic': {
        'farol': {'new': 2850, 'used': 1250, 'supplier': 'CDV Sucatas Autorizadas DETRAN SP'},
        'para-choque': {'new': 750, 'used': 420, 'supplier': 'Recuperadora AutoSul'},
        'parachoque': {'new': 750, 'used': 420, 'supplier': 'Recuperadora AutoSul'},
        'grade': {'new': 580, 'used': 280, 'supplier': 'CDV Honda Peças'},
        'capô': {'new': 1850, 'used': 890, 'supplier': 'Leilão Peças BR'},
        'capo': {'new': 1850, 'used': 890, 'supplier': 'Leilão Peças BR'},
    },
    'corolla': {
        'retrovisor': {'new': 1350, 'used': 650, 'supplier': 'CDV Sucatas RS'},
        'porta': {'new': 1850, 'used': 890, 'supplier': 'Mega Desmanche SP'},
        'paralama': {'new': 480, 'used': 260, 'supplier': 'Eco Auto Peças'},
        'farol': {'new': 1950, 'used': 880, 'supplier': 'CDV Toyota Peças'},
    },
}

# ─── Price Lookup ───────────────────────────────────────────────────────────────
def get_market_prices(brand, model, year, part_name):
    query_base = f"{brand} {model} {year} {part_name}".strip()
    encoded_new = urllib.parse.quote(f"{query_base} novo")
    encoded_used = urllib.parse.quote(f"{query_base} usado original")
    ml_link_new = f"https://lista.mercadolivre.com.br/{encoded_new}"
    ml_link_used = f"https://lista.mercadolivre.com.br/{encoded_used}"

    part_lower = part_name.lower()
    model_lower = model.lower()

    # Determine model-specific table
    model_key = None
    if any(k in model_lower for k in ['onix', 'prisma', 'joy', 'tracker']):
        model_key = 'onix'
    elif any(k in model_lower for k in ['civic', 'fit', 'hr-v', 'hrv', 'city', 'cr-v']):
        model_key = 'civic'
    elif any(k in model_lower for k in ['corolla', 'hilux', 'yaris', 'etios']):
        model_key = 'corolla'

    price_new = 950
    price_used = 480
    supplier_used = "CDV / Desmanche Credenciado Oficial DETRAN"

    # Try model-specific first, then general table
    tables_to_try = []
    if model_key:
        tables_to_try.append(REAL_MARKET_PRICES.get(model_key, {}))
    tables_to_try.append(REAL_MARKET_PRICES['geral'])

    for table in tables_to_try:
        for key in table:
            if key in part_lower:
                price_new = table[key]['new']
                price_used = table[key]['used']
                supplier_used = table[key]['supplier']
                break
        else:
            continue
        break

    # Brand factor for premium brands
    brand_upper = brand.upper()
    if any(b in brand_upper for b in ['BMW', 'MERCEDES', 'AUDI', 'VOLVO', 'PORSCHE', 'LAND ROVER']):
        price_new = int(price_new * 2.8)
        price_used = int(price_used * 2.2)
    elif any(b in brand_upper for b in ['JEEP', 'HONDA', 'TOYOTA', 'HYUNDAI']):
        price_new = int(price_new * 1.35)
        price_used = int(price_used * 1.25)

    return {
        "newPrice": {
            "brandName": f"Original {brand} OEM / Paralela 1ª Linha",
            "price": price_new,
            "type": "Nova (Original / Paralela)",
            "supplier": "Distribuidora AutoPeças Brasil & Concessionárias",
            "availability": "Em estoque",
            "link": ml_link_new,
        },
        "usedPrice": {
            "brandName": f"Seminova Original {brand}",
            "price": price_used,
            "type": "Usada / Seminova (Desmanche Credenciado DETRAN)",
            "supplier": supplier_used,
            "availability": "Disponível com NF e Rastreabilidade DETRAN",
            "link": ml_link_used,
        }
    }

# ─── Gemini Vision API ──────────────────────────────────────────────────────────
def call_gemini_vision(base64_images, vehicle_hint=None):
    if not GEMINI_API_KEY:
        return None, "NO_API_KEY"

    hint_text = ""
    if vehicle_hint:
        parts = [v for v in [vehicle_hint.get('brand'), vehicle_hint.get('model'), vehicle_hint.get('year')] if v]
        if parts:
            hint_text = f"\n\nHint do usuário (pode estar errado — a foto tem prioridade): {' '.join(parts)}"

    prompt = f"""Você é um perito automotivo especialista em avaliação de sinistros e vistoria de veículos.
Analise CUIDADOSAMENTE a(s) foto(s) do veículo e identifique:
1. A MARCA, MODELO e ANO EXATO do veículo na imagem (observe o design, logotipo, grade, faróis, formato)
2. TODOS os danos visíveis com precisão técnica
3. Quais peças precisam de substituição ou recuperação

ATENÇÃO: Base sua análise exclusivamente no que você VÊ na foto.{hint_text}

Responda APENAS com JSON válido neste formato (sem markdown, sem texto fora do JSON):
{{
  "vehicle": {{
    "brand": "Marca exata (ex: Volkswagen, Hyundai, Chevrolet, Ford, Fiat)",
    "model": "Modelo completo (ex: HB20 Comfort, Gol Trend, Ka Hatch)",
    "year": "Ano estimado ou faixa (ex: 2018-2020)",
    "color": "Cor do veículo",
    "bodyType": "Hatch | Sedan | SUV | Pickup | Van",
    "confidenceScore": 0.90
  }},
  "damageAnalysis": {{
    "overallSeverity": "Leve | Média | Alta | Muito Alta | Perda Total",
    "impactZone": "Frontal | Lateral Esquerda | Lateral Direita | Traseira | Múltiplas Zonas | Capotamento",
    "summary": "Resumo técnico completo das avarias",
    "parts": [
      {{
        "name": "Nome técnico da peça (ex: Para-choque dianteiro esquerdo)",
        "category": "Lataria | Iluminação | Carroceria | Vidros | Mecânica | Elétrica | Acabamento",
        "actionRequired": "Substituição | Recuperação | Pintura | Alinhamento | Inspeção",
        "severity": "Leve | Médio | Alto | Crítico",
        "confidence": 0.95,
        "notes": "Descrição técnica detalhada do dano"
      }}
    ]
  }}
}}"""

    image_parts = [{"text": prompt}]
    for b64 in base64_images[:4]:  # Max 4 images
        image_parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": b64
            }
        })

    request_body = {
        "contents": [{"parts": image_parts}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048,
        }
    }

    # Candidate models in fallback order
    candidate_models = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-flash-latest']
    last_error = "NO_RESPONSE"

    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(request_body).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            response = urllib.request.urlopen(req, timeout=45)
            result = json.loads(response.read().decode('utf-8'))
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            # Strip markdown fences if present
            raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text.strip(), flags=re.MULTILINE)
            raw_text = re.sub(r'\s*```$', '', raw_text.strip(), flags=re.MULTILINE)
            parsed = json.loads(raw_text.strip())
            print(f"[Gemini API] Success using model: {model_name}")
            return parsed, None
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='ignore')
            print(f"[Gemini API] Model {model_name} HTTPError {e.code}: {body[:150]}")
            last_error = f"HTTP_{e.code}"
            continue
        except Exception as e:
            print(f"[Gemini API] Model {model_name} error: {e}")
            last_error = str(e)
            continue

    return None, last_error

# ─── Build full response from AI data or fallback ──────────────────────────────
def build_analysis_response(ai_result, vehicle_info_hint):
    """Build a full enriched response from Gemini result or smart fallback."""

    # If AI returned valid data, use it
    if ai_result and 'vehicle' in ai_result and 'damageAnalysis' in ai_result:
        vehicle = ai_result['vehicle']
        damage = ai_result['damageAnalysis']

        # Merge with any user-provided hints (user hint only fills if AI was uncertain)
        if not vehicle.get('brand') and vehicle_info_hint.get('brand'):
            vehicle['brand'] = vehicle_info_hint['brand']

        brand = vehicle.get('brand', 'Veículo')
        model = vehicle.get('model', 'Modelo Identificado')
        year = vehicle.get('year', 'Ano Identificado')

        enriched_parts = []
        for part in damage.get('parts', []):
            prices = get_market_prices(brand, model, year, part['name'])
            choice = 'repair' if part.get('actionRequired') in ['Recuperação', 'Pintura', 'Alinhamento'] else 'used'
            enriched_parts.append({
                "id": f"part-{int(time.time() * 1000)}-{len(enriched_parts)}",
                **part,
                **prices,
                "selectedChoice": choice
            })

        return {
            "success": True,
            "aiPowered": True,
            "vehicle": {
                "brand": brand,
                "model": model,
                "year": year,
                "color": vehicle.get('color', ''),
                "bodyType": vehicle.get('bodyType', ''),
                "detectedAutomatically": True,
                "confidenceScore": vehicle.get('confidenceScore', 0.9),
            },
            "damageAnalysis": {
                "overallSeverity": damage.get('overallSeverity', 'Média'),
                "impactZone": damage.get('impactZone', 'Frontal'),
                "summary": damage.get('summary', 'Análise de avarias realizada pela IA.'),
                "parts": enriched_parts,
                "laborCosts": estimate_labor(enriched_parts, damage.get('overallSeverity', 'Média')),
            }
        }

    # Fallback: use vehicle_info_hint (what the user typed) + generic damage
    brand = vehicle_info_hint.get('brand') or 'Veículo'
    model = vehicle_info_hint.get('model') or 'Analisado'
    year = vehicle_info_hint.get('year') or '2021'

    fallback_parts = [
        {"name": "Componente Frontal — Requer Avaliação Presencial", "category": "Carroceria", "actionRequired": "Substituição", "severity": "Médio", "confidence": 0.5, "notes": "Análise automática por foto não disponível. Configure a chave GEMINI_API_KEY para habilitar visão por IA."},
    ]
    enriched_parts = []
    for part in fallback_parts:
        prices = get_market_prices(brand, model, year, part['name'])
        enriched_parts.append({"id": f"fallback-{int(time.time())}", **part, **prices, "selectedChoice": "used"})

    return {
        "success": True,
        "aiPowered": False,
        "fallbackReason": "NO_API_KEY" if not GEMINI_API_KEY else "AI_ANALYSIS_FAILED",
        "vehicle": {
            "brand": brand,
            "model": model,
            "year": year,
            "detectedAutomatically": False,
            "confidenceScore": 0.0,
        },
        "damageAnalysis": {
            "overallSeverity": "Requer Análise Manual",
            "impactZone": "Desconhecida",
            "summary": "⚠️ Visão por IA indisponível. Configure GEMINI_API_KEY no arquivo .env para ativar a análise real por foto.",
            "parts": enriched_parts,
            "laborCosts": estimate_labor(enriched_parts, 'Média'),
        }
    }

def estimate_labor(parts, severity):
    """Estimate labor hours and costs based on part count and severity."""
    part_count = len(parts)
    base_hours = max(4, part_count * 2)
    severity_mult = {'Leve': 0.7, 'Média': 1.0, 'Alta': 1.4, 'Muito Alta': 1.8, 'Perda Total': 2.5}.get(severity, 1.0)
    hours = int(base_hours * severity_mult)
    paint_panels = max(1, sum(1 for p in parts if p.get('actionRequired') in ['Substituição', 'Recuperação', 'Pintura']))

    return {
        "bodyworkHours": min(hours, 40),
        "bodyworkRate": 95.0,
        "paintPanels": paint_panels,
        "paintRatePerPanel": 480.0,
        "mechanicMontage": 350.0,
    }

# ─── HTTP Handler ───────────────────────────────────────────────────────────────
class AutoBudgetHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        """Serve index.html from root and everything else from public/."""
        parsed = urllib.parse.urlparse(path)
        rel = parsed.path.lstrip('/')

        # API paths are handled separately
        if rel.startswith('api/'):
            return os.path.join(DIRECTORY, rel)

        # Root → index.html
        if not rel or rel == 'index.html':
            return os.path.join(DIRECTORY, 'index.html')

        # Everything else → public/ directory
        return os.path.join(PUBLIC_DIR, rel)

    def add_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.add_cors_headers()
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_json_error(self, message, status=400):
        self.send_json({"success": False, "error": message}, status)

    def read_json_body(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length == 0:
                return None, "Empty request body"
            raw = self.rfile.read(length)
            return json.loads(raw.decode('utf-8')), None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"
        except Exception as e:
            return None, f"Read error: {e}"

    def do_POST(self):
        # ── Health check ──────────────────────────────────────────────────────
        if self.path == '/api/health':
            self.send_json({
                "status": "ok",
                "geminiKeyConfigured": bool(GEMINI_API_KEY),
                "timestamp": time.time()
            })
            return

        # ── Analyze damage ────────────────────────────────────────────────────
        if self.path == '/api/analyze-damage':
            body, err = self.read_json_body()
            if err:
                self.send_json_error(err)
                return

            images = body.get('images', [])
            vehicle_info = body.get('vehicleInfo', {}) or {}

            if not isinstance(images, list):
                self.send_json_error("Field 'images' must be an array of base64 strings")
                return

            # Filter valid base64 strings
            valid_images = [img for img in images if isinstance(img, str) and len(img) > 100]

            ai_result = None
            ai_error = None
            if valid_images:
                ai_result, ai_error = call_gemini_vision(valid_images, vehicle_info)
                if ai_error:
                    print(f"[AI] Analysis failed: {ai_error}")

            response = build_analysis_response(ai_result, vehicle_info)
            self.send_json(response)
            return

        # ── Search parts ──────────────────────────────────────────────────────
        if self.path == '/api/search-parts':
            body, err = self.read_json_body()
            if err:
                self.send_json_error(err)
                return

            part_name = (body.get('partName') or '').strip()
            if not part_name:
                self.send_json_error("Field 'partName' is required and cannot be empty")
                return

            brand = (body.get('brand') or 'Veículo').strip()
            model = (body.get('model') or 'Genérico').strip()
            year = (body.get('year') or '2021').strip()

            prices = get_market_prices(brand, model, year, part_name)
            self.send_json({"success": True, "query": {"brand": brand, "model": model, "year": year, "partName": part_name}, "prices": prices})
            return

        # ── Fallback: static files ────────────────────────────────────────────
        super().do_POST()

    def do_GET(self):
        if self.path == '/api/health':
            self.send_json({
                "status": "ok",
                "geminiKeyConfigured": bool(GEMINI_API_KEY),
                "timestamp": time.time()
            })
            return
        super().do_GET()

    def log_message(self, format, *args):
        ts = time.strftime('%H:%M:%S')
        print(f"[{ts}] {self.address_string()} {format % args}")

# ─── Thread-safe Server ─────────────────────────────────────────────────────────
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    key_status = f"Configurada ({GEMINI_API_KEY[:8]}...)" if GEMINI_API_KEY else "NAO configurada - crie o arquivo .env"
    print("=" * 58)
    print("  AutoBudget AI -- Servidor v2.0")
    print("=" * 58)
    print(f"  URL:       http://localhost:{PORT}")
    print(f"  GEMINI KEY: {key_status}")
    print("=" * 58)
    print()
    with ThreadedTCPServer(('', PORT), AutoBudgetHandler) as httpd:
        httpd.serve_forever()
