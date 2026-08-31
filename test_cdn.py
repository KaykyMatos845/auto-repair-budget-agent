import urllib.request

cdns = [
    'https://unpkg.com/react@18/umd/react.development.js',
    'https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js',
    'https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js',
    'https://unpkg.com/@babel/standalone/babel.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.10/babel.min.js',
]

for url in cdns:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=5)
        print(f'{url[:45]}... -> {resp.status} ({len(resp.read())} bytes)')
    except Exception as e:
        print(f'{url[:45]}... -> ERROR: {e}')
