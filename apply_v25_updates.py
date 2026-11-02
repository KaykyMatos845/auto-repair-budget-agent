with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Title
html = html.replace('<title>AutoBudget AI — Orçamento Inteligente de Reparos Veiculares</title>', '<title>AutoBudget AI v2.5 — Vistoria, FIPE, Bounding Boxes & WhatsApp</title>')

# 2. Add WhatsApp CSS Button style if missing
wa_css = '''.btn-whatsapp { background: linear-gradient(135deg, #25D366, #128C7E); color: #fff; font-weight: 800; padding: 12px 24px; border-radius: var(--rs); border: none; cursor: pointer; display: inline-flex; align-items: center; gap: 9px; transition: all .22s; font-size: .87rem; text-transform: uppercase; box-shadow: 0 0 20px rgba(37,211,102,0.35); } .btn-whatsapp:hover { transform: translateY(-2px); filter: brightness(1.1); }'''

if '.btn-whatsapp' not in html:
    html = html.replace('</style>', wa_css + '\n</style>')

# 3. Add WhatsApp button next to PDF button
wa_btn = '''<button className="btn-whatsapp" onClick={() => {
  const pList = parts.map((p,i) => ${i+1}.  - ).join('\\n');
  const msg = 🏎️ *ORÇAMENTO DE REPAROS AUTOMOTIVOS*\\n🚘 Veículo:   ()\\n🏷️ Placa:  | Cliente: \\n📊 FIPE: \\n\\n📋 *PEÇAS:*\\n\\n\\n🔧 *MÃO DE OBRA:* \\n💰 *TOTAL:* **;
  window.open(https://wa.me/?text=, '_blank');
}}>📲 Enviar por WhatsApp</button> '''

if 'btn-whatsapp' not in html:
    html = html.replace('<button className="btn-emerald" onClick={() => setShowPdf(true)}>', wa_btn + '<button className="btn-emerald" onClick={() => setShowPdf(true)}>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated v2.5 successfully!')
