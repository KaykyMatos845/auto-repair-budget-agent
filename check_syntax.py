with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

babel_code = html.split('<script type=\"text/babel\">')[1].split('</script>')[0]
print('Babel code length:', len(babel_code))

# Check for unmatched brackets, quotes or syntax anomalies
lines = babel_code.splitlines()
print('Total lines in script:', len(lines))
for i, line in enumerate(lines[:30], 1):
    pass
print('First 5 lines:')
for line in lines[:5]:
    print(' ', line)
print('Last 5 lines:')
for line in lines[-5:]:
    print(' ', line)
