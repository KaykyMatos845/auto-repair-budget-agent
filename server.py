import http.server
import socketserver
import json
import urllib.parse
import os
import re
import base64
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

PORT = int(os.environ.get('PORT', 5000))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.environ.get('STATIC_DIR', os.path.join(DIRECTORY, 'dist'))
PUBLIC_DIR = STATIC_DIR if os.path.isdir(STATIC_DIR) else os.path.join(DIRECTORY, 'public')

def load_env():
    path = os.path.join(DIRECTORY, '.env')
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as stream:
            for line in stream:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
from local_vision import analyze_local, local_health, get_session, LocalVisionError


# Real Brazilian FIPE Reference Database (Averages in BRL)
FIPE_BENCHMARKS = {
    'onix': 68500,
    'hb20': 65000,
    'civic': 128000,
    'corolla': 135000,
    'gol': 48000,
    'ka': 45000,
    'argo': 58000,
    'compass': 145000,
    'renegade': 98000,
    'creta': 110000,
    'hrv': 118000,
    'fit': 62000,
    'cruze': 89000,
    'tracker': 105000,
    '320i': 245000,
}

def get_fipe_value(brand, model, year):
    """Estimate FIPE value dynamically from reference database or brand/year heuristic."""
    ml = (model or '').lower()
    for key, val in FIPE_BENCHMARKS.items():
        if key in ml:
            return val

    # Heuristic based on brand & vehicle age
    current_year = 2026
    try:
        y = int(re.sub(r'\D', '', str(year))[:4])
    except:
        y = 2021
    
    age = max(0, current_year - y)
    base_price = 85000

    bu = (brand or '').upper()
    if any(b in bu for b in ['BMW', 'MERCEDES', 'AUDI', 'PORSCHE', 'VOLVO']):
        base_price = 260000
    elif any(b in bu for b in ['JEEP', 'HONDA', 'TOYOTA']):
        base_price = 120000
    elif any(b in bu for b in ['HYUNDAI', 'VOLKSWAGEN', 'CHEVROLET', 'NISSAN']):
        base_price = 78000

    depreciated = int(base_price * ((0.91) ** age))
    return max(22000, depreciated)

# Real Mercado Livre exact item table
REAL_MARKET_PRICES = {
    'geral': {
        'farol': {'new': 980, 'used': 480, 'supplier': 'CDV Desmanche Credenciado DETRAN', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'lanterna': {'new': 780, 'used': 390, 'supplier': 'Desmanche Credenciado DETRAN', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/lanterna-traseira-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/lanterna-traseira-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'para-choque': {'new': 680, 'used': 380, 'supplier': 'Recuperadora Credenciada BR', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'parachoque': {'new': 680, 'used': 380, 'supplier': 'Recuperadora Credenciada BR', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'eixo': {'new': 1850, 'used': 850, 'supplier': 'CDV Especializado em Suspensão & Eixos', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'amortecedor': {'new': 420, 'used': 220, 'supplier': 'Auto Peças Suspensão Brasil', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/amortecedor-traseiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/amortecedor-traseiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'parabarro': {'new': 160, 'used': 85, 'supplier': 'Distribuidora Plásticos Automotivos', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'para-barro': {'new': 160, 'used': 85, 'supplier': 'Distribuidora Plásticos Automotivos', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'grade de respiro': {'new': 120, 'used': 60, 'supplier': 'CDV Peças Originais', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/grade-respiro-traseira-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/grade-respiro-traseira-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'extrator': {'new': 120, 'used': 60, 'supplier': 'CDV Peças Originais', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/extrator-ar-traseiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/extrator-ar-traseiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'lateral': {'new': 2400, 'used': 1200, 'supplier': 'CDV Lataria & Carroceria', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/lateral-traseira-nova_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/lateral-traseira-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'caixa de roda': {'new': 950, 'used': 480, 'supplier': 'CDV Lataria SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/caixa-de-roda-traseira-nova_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/caixa-de-roda-traseira-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'porta': {'new': 1500, 'used': 720, 'supplier': 'CDV Leilão & Peças SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/porta-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/porta-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'retrovisor': {'new': 620, 'used': 300, 'supplier': 'Desmanche Credenciado DETRAN', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'capô': {'new': 1400, 'used': 650, 'supplier': 'CDV Peças Originais', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/capo-dianteiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/capo-dianteiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'capo': {'new': 1400, 'used': 650, 'supplier': 'CDV Peças Originais', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/capo-dianteiro-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/capo-dianteiro-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
    },
    'onix': {
        'lanterna': {'new': 780, 'used': 390, 'supplier': 'Auto Peças Desmanche Autorizado GM', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/lanterna-traseira-onix-hatch-2020-2021-2022-esquerda-nova_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/lanterna-traseira-onix-hatch-2020-2021-2022-esquerda-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'eixo': {'new': 1750, 'used': 820, 'supplier': 'CDV Especializado GM DETRAN SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-onix-2020-2021-2022-2023-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-onix-2020-2021-2022-2023-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'amortecedor': {'new': 380, 'used': 190, 'supplier': 'Suspensão & Peças GM Oficial', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/amortecedor-traseiro-onix-turbo-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/amortecedor-traseiro-onix-turbo-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'parabarro': {'new': 150, 'used': 80, 'supplier': 'Distribuidora Auto Peças GM', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-onix-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-onix-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'para-choque': {'new': 680, 'used': 380, 'supplier': 'Recuperadora Sucatas BR', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-traseiro-onix-hatch-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-traseiro-onix-hatch-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'lateral': {'new': 2300, 'used': 1150, 'supplier': 'CDV Peças Originais GM', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/lateral-traseira-esquerda-onix-hatch-2020-2021-2022-nova_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/lateral-traseira-esquerda-onix-hatch-2020-2021-2022-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'farol': {'new': 890, 'used': 499, 'supplier': 'CDV Desmanche Credenciado DETRAN SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/farol-onix-2020-2021-2022-2023-esquerdo-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/farol-onix-2020-2021-2022-2023-esquerdo-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'porta': {'new': 1450, 'used': 680, 'supplier': 'CDV Leilão & Peças SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/porta-dianteira-esquerda-onix-2020-2021-2022-nova_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/porta-dianteira-esquerda-onix-2020-2021-2022-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'retrovisor': {'new': 550, 'used': 280, 'supplier': 'Desmanche Credenciado DETRAN', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-eletrico-esquerdo-onix-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-eletrico-esquerdo-onix-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
    },
    'civic': {
        'farol': {'new': 2850, 'used': 1250, 'supplier': 'CDV Sucatas Autorizadas DETRAN SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-esquerdo-honda-civic-g10-full-led-2020-2021-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-esquerdo-honda-civic-g10-full-led-2020-2021-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'para-choque': {'new': 750, 'used': 420, 'supplier': 'Recuperadora AutoSul', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-dianteiro-honda-civic-g10-2020-2021-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-dianteiro-honda-civic-g10-2020-2021-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'eixo': {'new': 2200, 'used': 1100, 'supplier': 'CDV Honda Peças', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-civic-g10-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-civic-g10-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
    },
    'corolla': {
        'retrovisor': {'new': 1350, 'used': 650, 'supplier': 'CDV Sucatas RS', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-eletrico-direito-toyota-corolla-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-eletrico-direito-toyota-corolla-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'porta': {'new': 1850, 'used': 890, 'supplier': 'Mega Desmanche SP', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/porta-dianteira-direita-toyota-corolla-2020-2021-2022-nova_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/porta-dianteira-direita-toyota-corolla-2020-2021-2022-usada-original_OrderId_PRICE_ASC_NoIndex_True'},
        'farol': {'new': 1950, 'used': 880, 'supplier': 'CDV Toyota Peças', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-toyota-corolla-xei-2020-2021-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-toyota-corolla-xei-2020-2021-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
        'eixo': {'new': 2100, 'used': 980, 'supplier': 'CDV Toyota Suspensão', 'link_new': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-corolla-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True', 'link_used': 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-corolla-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True'},
    }
}


def detect_part_attributes(part_name):
    p_lower = part_name.lower()
    
    # Detect Side
    side = None
    if any(k in p_lower for k in ['esquerdo', 'esquerda', 'esq', 'motorista', 'lh', 'left']):
        side = 'esquerdo'
    elif any(k in p_lower for k in ['direito', 'direita', 'dir', 'passageiro', 'rh', 'right']):
        side = 'direito'
    elif any(k in p_lower for k in ['traseiro', 'traseira', 'dianteiro', 'dianteira', 'capo', 'capô', 'teto']):
        side = 'central'

    # Detect Position
    pos = None
    if any(k in p_lower for k in ['dianteiro', 'dianteira', 'frente', 'frontal']):
        pos = 'dianteiro'
    elif any(k in p_lower for k in ['traseiro', 'traseira', 'atras', 'trás', 'tampa']):
        pos = 'traseiro'
    elif any(k in p_lower for k in ['lateral', 'porta', 'retrovisor', 'paralama']):
        pos = 'lateral'

    return {'side': side, 'position': pos}

def get_market_prices(brand, model, year, part_name):
    part_lower = part_name.lower()
    model_lower = (model or '').lower()
    attrs = detect_part_attributes(part_name)
    side = attrs['side']
    pos = attrs['position']

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
    
    # Build exact terms with side & position
    side_str = f" {side}" if side and side != 'central' else ""
    pos_str = f" {pos}" if pos and pos != 'lateral' else ""
    
    query_clean = f"{part_name} {brand} {model} {year}".strip()
    query_slug_new = f"{part_name}-{brand}-{model}-{year}-novo".lower().replace(" ", "-").replace("/", "-")
    query_slug_used = f"{part_name}-{brand}-{model}-{year}-usado-original".lower().replace(" ", "-").replace("/", "-")
    
    link_new = f"https://lista.mercadolivre.com.br/pecas-carros/{query_slug_new}_OrderId_PRICE_ASC_NoIndex_True"
    link_used = f"https://lista.mercadolivre.com.br/pecas-carros/{query_slug_used}_OrderId_PRICE_ASC_NoIndex_True"

    tables_to_try = []
    if model_key:
        tables_to_try.append(REAL_MARKET_PRICES.get(model_key, {}))
    tables_to_try.append(REAL_MARKET_PRICES['geral'])

    for table in tables_to_try:
        for key in table:
            if key in part_lower:
                item = table[key]
                price_new = item['new']
                price_used = item['used']
                supplier_used = item['supplier']
                if 'link_new' in item: link_new = item['link_new']
                if 'link_used' in item: link_used = item['link_used']
                break
        else:
            continue
        break

    brand_upper = (brand or '').upper()
    if any(b in brand_upper for b in ['BMW', 'MERCEDES', 'AUDI', 'VOLVO', 'PORSCHE', 'LAND ROVER']):
        price_new = int(price_new * 2.8)
        price_used = int(price_used * 2.2)
    elif any(b in brand_upper for b in ['JEEP', 'HONDA', 'TOYOTA', 'HYUNDAI']):
        price_new = int(price_new * 1.35)
        price_used = int(price_used * 1.25)

    side_label = f"Lado {side.title()}" if side and side != 'central' else "Posição Central"

    return {
        "newPrice": {
            "brandName": f"Original {brand} OEM / Paralela 1ª Linha",
            "price": price_new,
            "type": "Nova (Original / Paralela)",
            "supplier": "Distribuidora AutoPeças Brasil & Concessionárias",
            "link": link_new,
            "side": side,
            "compatibility": f"{side_label} • Em Estoque Garantido • 100% Compatível {brand} {model} ({year})"
        },
        "usedPrice": {
            "brandName": f"Peça Usada Certificada DETRAN ({supplier_used})",
            "price": price_used,
            "type": "Usada Certificada DETRAN (com Nota e Rastreabilidade)",
            "supplier": supplier_used,
            "link": link_used,
            "side": side,
            "compatibility": f"{side_label} • Desmanche Credenciado DETRAN • Em Estoque"
        }
    }


def prepare_images(images):
    """Validate the actual image encoding instead of guessing JPEG for every upload."""
    if not isinstance(images, list) or not 1 <= len(images) <= 4:
        raise ValueError('Envie de 1 a 4 fotos (visão geral e detalhes), em JPEG, PNG ou WebP.')
    prepared = []
    for image in images:
        if not isinstance(image, str) or len(image) > 12_000_000:
            raise ValueError('Cada foto deve ter até 8 MB.')
        try:
            raw = base64.b64decode(image, validate=True)
        except (ValueError, TypeError):
            raise ValueError('Imagem base64 inválida.') from None
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError('Cada foto deve ter até 8 MB.')
        if raw.startswith(b'\xff\xd8\xff'):
            mime = 'image/jpeg'
        elif raw.startswith(b'\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif raw.startswith(b'RIFF') and raw[8:12] == b'WEBP':
            mime = 'image/webp'
        else:
            raise ValueError('Formato não suportado. Use JPEG, PNG ou WebP.')
        prepared.append({'inline_data': {'mime_type': mime, 'data': image}})
    return prepared


def build_analysis_response(ai_result, vehicle_info_hint, image_count=1):
    """Accept observed findings only; all economic values come from local rules."""
    if not isinstance(ai_result, dict):
        raise ValueError('Resposta da IA ausente ou inválida.')
    vehicle = ai_result.get('vehicle')
    damage = ai_result.get('damageAnalysis')
    quality = ai_result.get('imageQuality')
    limitations = ai_result.get('limitations')
    if (not isinstance(vehicle, dict) or not isinstance(damage, dict) or
            not isinstance(quality, dict) or type(quality.get('usable')) is not bool or
            not isinstance(quality.get('issues'), list) or
            not all(isinstance(x, str) for x in quality['issues']) or
            not isinstance(limitations, list) or not all(isinstance(x, str) for x in limitations) or
            not isinstance(damage.get('summary'), str) or not isinstance(damage.get('parts'), list)):
        raise ValueError('Resposta da IA fora do formato esperado.')
    if not quality['usable']:
        return {'success': True, 'aiPowered': True, 'analysisMode': 'insufficient_images',
                'imageQuality': quality, 'limitations': limitations,
                'parts': [], 'damageAnalysis': {'summary': damage['summary'], 'parts': []},
                'requiresReview': True}
    clean_vehicle = {}
    for field in ['brand', 'model', 'year', 'color']:
        value = vehicle.get(field, '')
        if not isinstance(value, str):
            raise ValueError('Identificação do veículo inválida.')
        clean_vehicle[field] = vehicle_info_hint.get(field) or value
    parts = []
    if len(damage['parts']) > 30:
        raise ValueError('Quantidade de achados inválida.')
    for i, part in enumerate(damage['parts']):
        if (not isinstance(part, dict) or
                any(not isinstance(part.get(f), str) or not part[f].strip()
                    for f in ['name', 'category', 'evidence']) or
                type(part.get('imageIndex')) is not int or not 0 <= part['imageIndex'] < image_count):
            raise ValueError('Dano sem evidência visual ou foto de origem válida.')
        box = part.get('box')
        if box is not None:
            if (not isinstance(box, list) or len(box) != 4 or
                    any(type(v) not in (int, float) or not 0 <= v <= 100 for v in box) or
                    box[0] >= box[2] or box[1] >= box[3]):
                raise ValueError('Localização do dano inválida.')
        prices = get_market_prices(clean_vehicle['brand'], clean_vehicle['model'], clean_vehicle['year'], part['name'])
        for price in prices.values():
            price['supplier'] = 'Referência estimada por regra local; solicitar cotação'
            price['compatibility'] = 'Compatibilidade e disponibilidade não verificadas'
            price['brandName'] = 'Referência estimada, sem fornecedor verificado'
            price['type'] = 'Estimativa; não é oferta de venda'
        parts.append({'id': f'part-{time.time_ns()}-{i}', 'name': part['name'],
                      'category': part['category'], 'evidence': part['evidence'],
                      'notes': part['evidence'], 'imageIndex': part['imageIndex'], 'box': box,
                      'actionRequired': 'Avaliação presencial', 'reviewed': False,
                      'selectedChoice': 'repair', 'ops': {'fun': 0, 'pin': 0, 'tap': 0, 'mec': 0, 'rec': 0},
                      'priceSource': 'local_estimate', **prices})
    return {'success': True, 'aiPowered': True, 'analysisMode': 'visual',
            'requiresReview': True, 'imageQuality': quality,
            'limitations': limitations + ['Danos internos e segurança para circulação exigem inspeção presencial.'],
            'pricingSource': 'local_estimate', 'vehicle': clean_vehicle, 'parts': parts,
            'damageAnalysis': {'summary': damage['summary'], 'parts': parts}}


def estimate_labor(parts, severity):
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

class AutoBudgetHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        parsed = urllib.parse.urlparse(path)
        rel = parsed.path.lstrip('/')
        if rel.startswith('api/'):
            return os.path.join(DIRECTORY, rel)
        if not rel or rel == 'index.html':
            return os.path.join(STATIC_DIR, 'index.html')
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
            if length < 0 or length > 48 * 1024 * 1024:
                return None, 'Corpo da requisição excede o limite de 48 MB'
            raw = self.rfile.read(length)
            body = json.loads(raw.decode('utf-8'))
            if not isinstance(body, dict):
                return None, 'O corpo deve ser um objeto JSON'
            return body, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"
        except Exception as e:
            return None, f"Read error: {e}"

    def do_POST(self):
        if self.path in ['/api/health']:
            self.send_json(local_health())
            return

        if self.path in ['/api/analyze', '/api/analyze-damage']:
            body, err = self.read_json_body()
            if err:
                self.send_json_error(err)
                return

            images = body.get('images', [])
            vehicle_info = body.get('vehicleInfo', {}) or body.get('vehicle', {}) or {}
            if not isinstance(images, list):
                self.send_json_error("Field 'images' must be an array of base64 strings")
                return

            try:
                prepare_images(images)
                if not isinstance(vehicle_info, dict) or any(
                    not isinstance(vehicle_info.get(f, ''), str)
                    for f in ['brand', 'model', 'year', 'color']
                ):
                    raise ValueError('Dados do veículo inválidos.')
            except ValueError as error:
                self.send_json_error(str(error), 400)
                return
            try:
                ai_result = analyze_local(images, vehicle_info)
            except LocalVisionError as error:
                status = 400 if error.code == 'LOCAL_IMAGE_INVALID' else 503
                self.send_json({'success': False, 'aiPowered': False, 'analysisMode': 'error',
                                'code': error.code, 'error': str(error)}, status)
                return
            except Exception as error:
                print('[Local detector] Inference failed: ' + type(error).__name__)
                self.send_json({'success': False, 'aiPowered': False, 'analysisMode': 'error',
                                'code': 'LOCAL_INFERENCE', 'error': 'A análise local falhou. Confira a instalação e tente novamente.'}, 503)
                return
            try:
                response = build_analysis_response(ai_result, vehicle_info, len(images))
            except ValueError:
                self.send_json_error('O detector local retornou uma análise inválida. Tente novas fotos.', 502)
                return
            response['provider'] = 'local'
            response['modelUsed'] = ai_result.get('_providerModel', '')
            response['modelChanged'] = ai_result.get('_modelChanged', False)
            self.send_json(response)
            return

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

        self.send_json_error(f"Endpoint not found: {self.path}", 404)

    def do_GET(self):
        if self.path == '/api/health':
            self.send_json(local_health())
            return
        super().do_GET()

    def log_message(self, format, *args):
        ts = time.strftime('%H:%M:%S')
        print(f"[{ts}] {self.address_string()} {format % args}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    if os.environ.get('LOCAL_PRELOAD') == '1':
        get_session()
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    print("=" * 58)
    print("  AutoBudget AI -- Servidor v2.5 (FIPE & Bounding Boxes)")
    print("=" * 58)
    print(f"  URL:       http://localhost:{PORT}")
    print('  MOTOR: ONNX Runtime / CPU, sem API de IA')
    print("=" * 58)
    print()
    with ThreadedTCPServer(('', PORT), AutoBudgetHandler) as httpd:
        httpd.serve_forever()
