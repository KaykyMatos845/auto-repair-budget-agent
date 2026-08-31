with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

code = html.split('<script type=\"text/babel\">')[1].split('</script>')[0]

# Check for JSX syntax issues or missing variables
import re
print('Code length:', len(code))

# Check for export keywords inside babel script
exports = [line for line in code.splitlines() if 'export' in line]
print('Export lines count:', len(exports))
for e in exports:
    print(' EXPORT:', e)
