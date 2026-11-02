import os

source_file = r"C:\Users\kayky.matos\.gemini\antigravity-ide\scratch\auto-repair-budget-agent\index.html"
dest_file = r"C:\Users\kayky.matos\Downloads\auto-repair-budget-agent\index.html"

with open(source_file, "r", encoding="utf-8") as f:
    text = f.read()

# Add bbox overlay css
bbox_css = """
    .img-box-container {
      position: relative;
      display: inline-block;
      overflow: hidden;
      border-radius: 12px;
      border: 2px solid var(--border-hi);
    }
    .bbox-overlay {
      position: absolute;
      border: 3px solid #f43f5e;
      background: rgba(244,63,94,0.25);
      border-radius: 6px;
      box-shadow: 0 0 14px rgba(244,63,94,0.7);
      pointer-events: none;
      transition: all .3s;
    }
    .bbox-label {
      position: absolute;
      top: -24px;
      left: -2px;
      background: #f43f5e;
      color: #fff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 4px 4px 4px 0;
      white-space: nowrap;
      text-transform: uppercase;
    }
"""

text = text.replace("</style>", bbox_css + "\n</style>")

# Add isTotalLoss check and banner
total_loss_jsx = """
  const fipeVal = vehicle.fipeValue || 68500;
  const fipePct = ((budgetSel / fipeVal) * 100).toFixed(1);
  const isTotalLoss = fipePct >= 75.0;
"""

text = text.replace("const budgetSel = totSelected + totalLabor;", "const budgetSel = totSelected + totalLabor;\n" + total_loss_jsx)

# Add WhatsApp button CSS & Handler
wa_css = """
    .btn-whatsapp {
      background: linear-gradient(135deg, #25D366, #128C7E);
      color: #fff;
      font-weight: 800;
      padding: 12px 24px;
      border-radius: var(--rs);
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      transition: all .22s;
      font-size: .87rem;
      text-transform: uppercase;
      box-shadow: 0 0 20px rgba(37,211,102,0.35);
    }
    .btn-whatsapp:hover { transform: translateY(-2px); filter: brightness(1.1); }
"""
text = text.replace("</style>", wa_css + "\n</style>")

# Add Perda Total Banner JSX
banner_jsx = """
          {isTotalLoss && (
            <div className="card" style={{ padding:'22px 26px', marginBottom:24, background:'var(--grad-danger)', color:'#fff', border:'2px solid #ff4d6d', boxShadow:'0 0 35px rgba(244,63,94,0.45)' }}>
              <div style={{ display:'flex', alignItems:'center', gap:16 }}>
                <div style={{ fontSize:'2.8rem' }}>🚨</div>
                <div>
                  <h2 style={{ fontSize:'1.35rem', fontWeight:900, textTransform:'uppercase', letterSpacing:'.03em' }}>
                    ALERTA DE PERDA TOTAL (Sinistro > 75% da Tabela FIPE)
                  </h2>
                  <p style={{ fontSize:'.9rem', opacity:0.95, marginTop:4, lineHeight:1.5 }}>
                    O orçamento atual de <strong>{fmt(budgetSel)}</strong> atinge <strong>{fipePct}%</strong> da Tabela FIPE do veículo ({fmt(fipeVal)}).
                    Segundo a regulamentação de sinistros, avarias superiores a 75% caracterizam <strong>Perda Total (PT)</strong>.
                  </p>
                </div>
              </div>
            </div>
          )}
"""

text = text.replace("{/* DAMAGE REPORT */}", banner_jsx + "\n{/* DAMAGE REPORT */}")

# Add WhatsApp button near PDF
wa_btn = """
  const shareWhatsApp = () => {
    const pList = parts.map((p,i) => {
      const v = p.selectedChoice==='new' ? p.newPrice?.price : p.selectedChoice==='used' ? p.usedPrice?.price : 0;
      return `${i+1}. ${p.name} - ${fmt(v)} (${p.selectedChoice==='used'?'Usada DETRAN':'Nova OEM'})`;
    }).join('\\n');

    const msg = `🏎️ *ORÇAMENTO DE REPAROS AUTOMOTIVOS*
📅 Data: ${new Date().toLocaleDateString('pt-BR')}
🚘 Veículo: ${vehicle.brand} ${vehicle.model} (${vehicle.year})
🏷️ Placa: ${vehicle.plate||'N/I'} | Cliente: ${vehicle.clientName||'Cliente'}
📊 Valor FIPE: ${fmt(fipeVal)} | Compromisso: ${fipePct}% da FIPE ${isTotalLoss?'🚨 (RISCO PERDA TOTAL)':''}

📋 *PEÇAS & COMPONENTES:*
${pList}

🔧 *MÃO DE OBRA & PINTURA:* ${fmt(totalLabor)}
🎉 *Economia peças usadas:* ${fmt(saving)} (${savingPct}% OFF)
💰 *TOTAL DO ORÇAMENTO:* *${fmt(budgetSel)}*

_AutoBudget AI v2.5 — Vistoria Computacional_`;

    window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, '_blank');
  };
"""

text = text.replace("const toggleChoice =", wa_btn + "\n  const toggleChoice =")

wa_btn_element = """
                <button className="btn-whatsapp" onClick={shareWhatsApp}>📲 Enviar por WhatsApp</button>
"""
text = text.replace('<button className="btn-emerald" onClick={() => setShowPdf(true)}>', wa_btn_element + '\n                <button className="btn-emerald" onClick={() => setShowPdf(true)}>')

with open(dest_file, "w", encoding="utf-8") as f:
    f.write(text)

print("PATCH V2.5 APPLIED SUCCESSFULLY!")
