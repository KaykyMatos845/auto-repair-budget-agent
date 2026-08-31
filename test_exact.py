import urllib.request, urllib.parse, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

def resolve_exact_ml_item(brand, model, part_name, condition):
    query = f'mercadolivre produto MLB {brand} {model} {part_name} {condition}'
    encoded = urllib.parse.quote(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded}'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=6)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract product links (produto.mercadolivre.com.br/MLB-...)
        found = re.findall(r'href=[\"\']([^\"\']*produto\.mercadolivre\.com\.br[^\"]*MLB[^\"]*)[\"\']', html)
        if not found:
            found = re.findall(r'(https%3A%2F%2Fproduto\.mercadolivre\.com\.br%2F[^\s\"\'&]*MLB[^\s\"\'&]*)', html)
        if found:
            raw = found[0]
            clean = urllib.parse.unquote(raw)
            if 'uddg=' in clean:
                clean = clean.split('uddg=')[1].split('&')[0]
            clean = clean.split('?')[0].split('#')[0]
            return clean
    except Exception as e:
        print('Search Error:', e)
    
    # Fallback to targeted search URL
    q_fallback = urllib.parse.quote(f'{brand} {model} {part_name} {condition}')
    return f'https://lista.mercadolivre.com.br/{q_fallback}'

test_cases = [
    ('Chevrolet', 'Onix', 'Farol', 'novo'),
    ('Chevrolet', 'Onix', 'Farol', 'usado'),
    ('Honda', 'Civic', 'Para-choque', 'novo'),
    ('Honda', 'Civic', 'Para-choque', 'usado'),
    ('Toyota', 'Corolla', 'Retrovisor', 'novo'),
    ('Toyota', 'Corolla', 'Retrovisor', 'usado'),
]

for b, m, p, c in test_cases:
    link = resolve_exact_ml_item(b, m, p, c)
    print(f'[{c.upper():<5}] {b} {m} {p} => {link}')
