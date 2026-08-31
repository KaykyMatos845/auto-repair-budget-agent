import urllib.request
import urllib.parse
import re

def search_ddg(query):
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    )
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Look for snippet text containing R$ prices
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        full_text = " ".join(snippets)
        
        print("DDG Snippets text:", full_text[:400])
        prices = re.findall(r'R\$\s*([\d\.\,]+)', full_text)
        print("Extracted prices from search:", prices)
        
        valid = []
        for p in prices:
            clean_str = p.replace('.', '').replace(',', '.')
            try:
                val = float(clean_str)
                if 50 <= val <= 25000:
                    valid.append(val)
            except:
                pass
                
        print("Valid numeric prices:", valid)
        if valid:
            valid.sort()
            return valid[len(valid)//2]
    except Exception as e:
        print("DDG Error:", e)
    return None

if __name__ == '__main__':
    search_ddg("farol dianteiro esquerdo onixusado mercado livre R$")
