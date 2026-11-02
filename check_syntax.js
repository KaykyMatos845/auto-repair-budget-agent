const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const scriptContent = html.split('<script type="text/babel">')[1].split('</script>')[0];
console.log('Script length:', scriptContent.length);

// Check syntax using Function constructor or node vm
try:
    new Function(scriptContent);
    console.log('Syntax OK!');
} catch (e) {
    console.log('Syntax Error:', e.message);
}
