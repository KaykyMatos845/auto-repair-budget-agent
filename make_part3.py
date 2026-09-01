p3_code = """
function App() {
  const [images, setImages] = useState([]);
  const [vehicle, setVehicle] = useState({ brand:'', model:'', year:'', plate:'', color:'', clientName:'', fipeValue: 68500 });
  const [parts, setParts] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [labor, setLabor] = useState({ bodyworkHours:7, bodyworkRate:95, paintPanels:2, paintRatePerPanel:480, mechanicMontage:350 });
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  const [apiKey, setApiKey] = useState(null);
  const [showPdf, setShowPdf] = useState(false);
  const [osStatus, setOsStatus] = useState('📋 Em Vistoria');
  const [osList, setOsList] = useState(() => {
    try { return JSON.parse(localStorage.getItem('autobudget_os_list')||'[]'); } catch { return []; }
  });
  const fileRef = useRef();

  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(d => setApiKey(d.geminiKeyConfigured))
      .catch(() => setApiKey(false));
  }, []);

  const setVField = (f, v) => setVehicle(prev => ({ ...prev, [f]: v }));

  const processFiles = async (files) => {
    const validFiles = Array.from(files).filter(f => f.type.startsWith('image/'));
    if (!validFiles.length) return;
    setVehicle({ brand:'', model:'', year:'', plate:'', color:'', clientName:'', fipeValue: 68500 });
    setAnalysis(null);
    setParts([]);

    const processed = await Promise.all(validFiles.map(async file => {
      const blobUrl = URL.createObjectURL(file);
      const reader = new FileReader();
      const base64 = await new Promise((res, rej) => {
        reader.onloadend = () => res(reader.result.replace(/^data:[^;]+;base64,/, ''));
        reader.onerror = rej;
        reader.readAsDataURL(file);
      });
      return { blobUrl, base64, name: file.name };
    }));
    setImages(processed);
  };

  const analyze = async () => {
    if (!images.length) return;
    setLoading(true);
    setLoadingMsg('🔍 Processando foto...');

    try {
      const base64s = images.map(i => i.base64);
      setLoadingMsg('🤖 Gemini 3.6 Flash mapeando danos e coordenadas...');

      const res = await fetch('/api/analyze-damage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ images: base64s, vehicleInfo: vehicle })
      });

      if (!res.ok) throw new Error(Server error: );
      const data = await res.json();

      setVehicle(prev => ({
        brand: data.vehicle.brand || prev.brand,
        model: data.vehicle.model || prev.model,
        year: data.vehicle.year || prev.year,
        color: data.vehicle.color || prev.color,
        plate: data.vehicle.plate || prev.plate,
        clientName: data.vehicle.clientName || prev.clientName,
        fipeValue: data.vehicle.fipeValue || 68500,
      }));
      setAnalysis(data);
      setParts(data.damageAnalysis?.parts || []);
      if (data.damageAnalysis?.laborCosts) setLabor(data.damageAnalysis.laborCosts);

    } catch(e) {
      alert(Erro na análise: );
    } finally {
      setLoading(false);
      setLoadingMsg('');
    }
  };

  const loadSample = (sample) => {
    setImages([{ blobUrl: sample.img, base64: '', name: 'sample' }]);
    setVehicle({ ...sample.vehicle });
    setAnalysis({ aiPowered: false, damageAnalysis: { overallSeverity: 'Média', impactZone: 'Frontal', summary: 'Caso de demonstração pré-carregado.' } });
    setParts(sample.parts);
    setLabor(sample.labor);
  };

  const toggleChoice = (id, choice) => setParts(prev => prev.map(p => p.id === id ? { ...p, selectedChoice: choice } : p));

  const bwTotal = (labor.bodyworkHours||0) * (labor.bodyworkRate||0);
  const ptTotal = (labor.paintPanels||0) * (labor.paintRatePerPanel||0);
  const mcTotal = (labor.mechanicMontage||0);
  const totalLabor = bwTotal + ptTotal + mcTotal;

  let totNew = 0, totSelected = 0;
  parts.forEach(p => {
    totNew += p.newPrice?.price || 0;
    if (p.selectedChoice === 'new') totSelected += p.newPrice?.price || 0;
    else if (p.selectedChoice === 'used') totSelected += p.usedPrice?.price || 0;
  });

  const budgetNew = totNew + totalLabor;
  const budgetSel = totSelected + totalLabor;
  const saving = Math.max(0, budgetNew - budgetSel);
  const savingPct = budgetNew > 0 ? ((saving / budgetNew) * 100).toFixed(1) : 0;

  const fipeVal = vehicle.fipeValue || 68500;
  const fipePct = ((budgetSel / fipeVal) * 100).toFixed(1);
  const isTotalLoss = fipePct >= 75.0;

  const saveOS = () => {
    const newOs = {
      id: OS-,
      date: new Date().toLocaleDateString('pt-BR'),
      vehicle: ${vehicle.brand}  (),
      plate: vehicle.plate || 'Sem placa',
      client: vehicle.clientName || 'Cliente',
      status: osStatus,
      total: budgetSel,
      partsCount: parts.length
    };
    const updated = [newOs, ...osList.slice(0, 19)];
    setOsList(updated);
    localStorage.setItem('autobudget_os_list', JSON.stringify(updated));
    alert(✅ Ordem de Serviço  salva no histórico!);
  };

  const shareWhatsApp = () => {
    const pList = parts.map((p,i) => {
      const v = p.selectedChoice==='new' ? p.newPrice?.price : p.selectedChoice==='used' ? p.usedPrice?.price : 0;
      return ${i+1}.  -  ();
    }).join('\\n');

    const msg = 🏎️ *ORÇAMENTO DE REPAROS AUTOMOTIVOS*\\n📅 Data: \\n🚘 Veículo:   ()\\n🏷️ Placa:  | Cliente: \\n📊 Valor FIPE:  | Compromisso: % da FIPE \\n\\n📋 *PEÇAS & COMPONENTES:*\\n\\n\\n🔧 *MÃO DE OBRA & PINTURA:* \\n🎉 *Economia peças usadas:*  (% OFF)\\n💰 *TOTAL DO ORÇAMENTO:* **\\n\\nStatus OS: \\n_AutoBudget AI v2.5 — Vistoria Computacional_;

    window.open(https://wa.me/?text=, '_blank');
  };

  return (
    <div className="wrap">

      <header className="card" style={{ padding:'18px 26px', marginBottom:26, borderTop:'3px solid var(--gold)', display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:14 }}>
        <div style={{ display:'flex', alignItems:'center', gap:14 }}>
          <div style={{ background:'var(--grad-gold)', width:48, height:48, borderRadius:13, display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.5rem', boxShadow:'0 0 20px rgba(245,158,11,0.4)' }}>🏎️</div>
          <div>
            <h1 style={{ fontSize:'1.45rem', fontWeight:900 }}>AutoBudget <span className="grad-text">AI v2.5</span></h1>
            <p style={{ color:'var(--muted)', fontSize:'.83rem' }}>Vistoria Computacional • FIPE • Perda Total (>75%) • Links Diretos Mercado Livre</p>
          </div>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:10, flexWrap:'wrap' }}>
          {apiKey === true && <span className="badge badge-ai">🤖 Gemini 3.6 Flash</span>}
          <span className="badge badge-used"><span style={{ width:7, height:7, borderRadius:'50%', background:'var(--emerald)', display:'inline-block' }}></span> Mercado Livre Live</span>
          <button className="btn-ghost" onClick={() => { setImages([]); setAnalysis(null); setParts([]); }}>↺ Nova Vistoria</button>
        </div>
      </header>

      <div className="card" style={{ padding:'20px 24px', marginBottom:24 }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:14 }}>
          <h3 style={{ fontSize:'1rem', fontWeight:800, color:'var(--gold)', display:'flex', alignItems:'center', gap:8 }}>
            ⚡ Casos de Vistoria de Demonstração
          </h3>
          <span style={{ fontSize:'.78rem', color:'var(--dim)' }}>Clique para testar com foto e Bounding Boxes</span>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))', gap:14 }}>
          {SAMPLES.map(s => (
            <div key={s.id} className="sel-card" onClick={() => loadSample(s)} style={{ display:'flex', alignItems:'center', gap:13, padding:'13px 15px', background:'rgba(10,14,24,0.8)', borderRadius:10, border:'1px solid var(--border)', cursor:'pointer' }}>
              <img src={s.img} alt={s.label} style={{ width:72, height:72, objectFit:'cover', borderRadius:9, border:'1px solid rgba(255,255,255,0.08)', flexShrink:0 }} />
              <div>
                <div style={{ fontSize:'.88rem', fontWeight:800, color:'#fff' }}>{s.label}</div>
                <div style={{ fontSize:'.75rem', color:'var(--muted)', marginTop:3 }}>{s.sub}</div>
                <div style={{ fontSize:'.73rem', color:'var(--gold)', fontWeight:700, marginTop:6 }}>Carregar Vistoria →</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ padding:'24px', marginBottom:24 }}>
        <h2 style={{ fontSize:'1.1rem', fontWeight:800, marginBottom:6 }}>📸 1. Fotos da Vistoria do Veículo</h2>
        <p style={{ fontSize:'.84rem', color:'var(--muted)', marginBottom:18 }}>
          Envie fotos das avarias. A IA identificará o modelo, todas as peças danificadas e desenhará as <strong>Bounding Boxes nas fotos</strong>.
        </p>

        <div className="upload-zone" onClick={() => fileRef.current?.click()}>
          <input ref={fileRef} type="file" multiple accept="image/*" style={{ display:'none' }} onChange={e => processFiles(e.target.files)} />
          <div style={{ fontSize:'2.5rem', marginBottom:10 }}>📸</div>
          <div style={{ fontWeight:700, color:'var(--gold)', fontSize:'1rem', marginBottom:4 }}>Clique ou arraste fotos aqui</div>
          <div style={{ fontSize:'.82rem', color:'var(--muted)' }}>JPG, PNG, WEBP — Suporta múltiplas imagens</div>
        </div>

        {images.length > 0 && (
          <div style={{ marginTop:18 }}>
            <div style={{ display:'flex', gap:14, flexWrap:'wrap', marginBottom:16 }}>
              {images.map((img, i) => (
                <div key={i} className="img-box-container">
                  <img src={img.blobUrl} alt={img.name} style={{ width:280, height:180, objectFit:'cover', display:'block' }} />
                  {/* Bounding Box Overlays */}
                  {parts.map((p, idx) => {
                    if (!p.box) return null;
                    const [ymin, xmin, ymax, xmax] = p.box;
                    return (
                      <div key={idx} className="bbox-overlay" style={{
                        top: ${ymin}%,
                        left: ${xmin}%,
                        width: ${Math.max(18, xmax - xmin)}%,
                        height: ${Math.max(18, ymax - ymin)}%,
                      }}>
                        <div className="bbox-label">{p.name.split(' ')[0]}</div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>

            <button className="btn-gold" onClick={analyze} disabled={loading}>
              {loading ? (
                <><div className="spinner"/><span>{loadingMsg || 'Analisando...'}</span></>
              ) : (
                '⚡ ANALISAR FOTOS COM GEMINI VISION'
              )}
            </button>
          </div>
        )}
      </div>

      <div className="card" style={{ padding:'24px', marginBottom:24 }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16, flexWrap:'wrap', gap:10 }}>
          <h2 style={{ fontSize:'1.1rem', fontWeight:800, color:'var(--gold)' }}>🚘 2. Ficha do Veículo & Tabela FIPE</h2>
          <span className="badge badge-used">📊 FIPE Ref: {fmt(fipeVal)}</span>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(165px, 1fr))', gap:13 }}>
          {[['brand','Marca'],['model','Modelo / Versão'],['year','Ano'],['plate','Placa'],['color','Cor'],['clientName','Cliente']].map(([f,lbl]) => (
            <div key={f}>
              <label>{lbl}:</label>
              <input className="inp" value={vehicle[f]||''} onChange={e => setVField(f, e.target.value)} placeholder={lbl} />
            </div>
          ))}
          <div>
            <label>Valor Tabela FIPE (R$):</label>
            <input type="number" className="inp" value={vehicle.fipeValue||68500} onChange={e => setVField('fipeValue', parseFloat(e.target.value)||0)} />
          </div>
        </div>
      </div>

      {parts.length > 0 && (
        <div className="fade-up">

          {/* PERDA TOTAL ALERT */}
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

          <div className="card" style={{ padding:'24px', marginBottom:24 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12, flexWrap:'wrap', gap:10 }}>
              <h2 style={{ fontSize:'1.1rem', fontWeight:800 }}>🔍 3. Mapeamento de Avarias & Bounding Boxes</h2>
              <span className="badge badge-replace">Compromisso FIPE: {fipePct}%</span>
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {parts.map((p, i) => (
                <div key={p.id} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'13px 17px', background:'rgba(10,14,24,.85)', borderRadius:9, border:'1px solid var(--border)', flexWrap:'wrap', gap:9 }}>
                  <div>
                    <strong style={{ fontSize:'.93rem' }}>{i+1}. {p.name}</strong>
                    <span style={{ fontSize:'.76rem', color:'var(--muted)', marginLeft:10 }}>({p.category})</span>
                    {p.notes && <div style={{ fontSize:'.75rem', color:'var(--dim)', marginTop:3 }}>{p.notes}</div>}
                  </div>
                  <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                    <span className={p.actionRequired==='Substituição' ? 'badge badge-replace' : 'badge badge-repair'}>{p.actionRequired}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card" style={{ padding:'24px', marginBottom:24 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20, flexWrap:'wrap', gap:12 }}>
              <div>
                <h2 style={{ fontSize:'1.15rem', fontWeight:800 }}>🛒 4. Cotação Mercado Livre (Links Diretos para Anúncios)</h2>
                <p style={{ fontSize:'.84rem', color:'var(--muted)' }}>Links exatos para o produto selecionado no Mercado Livre Brasil:</p>
              </div>
            </div>

            <div style={{ display:'flex', flexDirection:'column', gap:20 }}>
              {parts.map(p => {
                const isRepair = p.selectedChoice === 'repair' || p.actionRequired === 'Recuperação' || p.actionRequired === 'Pintura';
                const np = p.newPrice?.price || 0;
                const up = p.usedPrice?.price || 0;

                return (
                  <div key={p.id} style={{ background:'rgba(10,14,24,.9)', padding:20, borderRadius:13, border:'1px solid var(--border)' }}>
                    <h3 style={{ fontSize:'1rem', fontWeight:800, marginBottom:12 }}>{p.name}</h3>

                    {isRepair ? (
                      <div style={{ padding:'12px 16px', background:'rgba(245,158,11,.1)', border:'1px solid rgba(245,158,11,.3)', color:'#fbbf24', borderRadius:8, fontSize:'.86rem' }}>
                        🛠️ Serviço de Funilaria — incluso no custo de mão de obra.
                      </div>
                    ) : (
                      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))', gap:13 }}>
                        <div className="sel-card" onClick={() => toggleChoice(p.id, 'new')} style={{ padding:16, borderRadius:10, background: p.selectedChoice==='new' ? 'rgba(139,92,246,.18)' : 'rgba(20,28,46,.5)', border: p.selectedChoice==='new' ? '2px solid var(--violet)' : '1px solid var(--border)', cursor:'pointer' }}>
                          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:8 }}><span className="badge badge-new">Nova OEM</span></div>
                          <div style={{ fontSize:'1.25rem', fontWeight:900, color:'#c084fc' }}>{fmt(np)}</div>
                          <div style={{ fontSize:'.81rem', color:'#cbd5e1', marginTop:5 }}>{p.newPrice?.brandName}</div>
                          {p.newPrice?.link && (
                            <a href={p.newPrice.link} target="_blank" onClick={e => e.stopPropagation()} style={{ fontSize:'.77rem', color:'#c084fc', marginTop:8, display:'inline-block', fontWeight:700 }}>
                              Ver Anúncio no Mercado Livre ↗
                            </a>
                          )}
                        </div>

                        <div className="sel-card" onClick={() => toggleChoice(p.id, 'used')} style={{ padding:16, borderRadius:10, background: p.selectedChoice==='used' ? 'rgba(16,185,129,.18)' : 'rgba(20,28,46,.5)', border: p.selectedChoice==='used' ? '2px solid var(--emerald)' : '1px solid var(--border)', cursor:'pointer' }}>
                          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:8 }}><span className="badge badge-used">Usada DETRAN</span></div>
                          <div style={{ fontSize:'1.25rem', fontWeight:900, color:'#34d399' }}>{fmt(up)}</div>
                          <div style={{ fontSize:'.81rem', color:'#cbd5e1', marginTop:5 }}>{p.usedPrice?.brandName}</div>
                          {p.usedPrice?.link && (
                            <a href={p.usedPrice.link} target="_blank" onClick={e => e.stopPropagation()} style={{ fontSize:'.77rem', color:'#34d399', marginTop:8, display:'inline-block', fontWeight:700 }}>
                              Ver Anúncio no Mercado Livre ↗
                            </a>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="card" style={{ padding:'24px', marginBottom:24 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:18, flexWrap:'wrap', gap:10 }}>
              <h2 style={{ fontSize:'1.1rem', fontWeight:800, color:'var(--gold)' }}>🔧 5. Mão de Obra e Status da Ordem de Serviço (OS)</h2>
              <div>
                <label style={{ display:'inline', marginRight:8 }}>Status OS:</label>
                <select className="inp" style={{ width:'auto', display:'inline-block' }} value={osStatus} onChange={e => setOsStatus(e.target.value)}>
                  <option value="📋 Em Vistoria">📋 Em Vistoria</option>
                  <option value="📦 Aguardando Peças">📦 Aguardando Peças</option>
                  <option value="🛠️ Em Funilaria">🛠️ Em Funilaria</option>
                  <option value="✅ Concluído">✅ Concluído</option>
                </select>
              </div>
            </div>

            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(200px, 1fr))', gap:14, marginBottom:16 }}>
              {[['bodyworkHours','Horas Funilaria'],['bodyworkRate','Taxa/hora (R$)'],['paintPanels','Painéis Pintura'],['paintRatePerPanel','Pintura/Peça (R$)'],['mechanicMontage','Montagem (R$)']].map(([k,lbl]) => (
                <div key={k}>
                  <label>{lbl}:</label>
                  <input type="number" className="inp" value={labor[k]||0} onChange={e => setLabor(prev => ({ ...prev, [k]: parseFloat(e.target.value)||0 }))} />
                </div>
              ))}
            </div>

            <button className="btn-ghost" onClick={saveOS}>💾 Salvar Ordem de Serviço no Histórico</button>
          </div>

          <div className="card" style={{ padding:'28px', marginBottom:32, border:'2px solid var(--gold)', boxShadow:'var(--shadow-gold)' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:22, flexWrap:'wrap', gap:14 }}>
              <div>
                <h2 style={{ fontSize:'1.35rem', fontWeight:900 }}>💰 Resumo Total do Orçamento</h2>
                <p style={{ fontSize:'.84rem', color:'var(--muted)' }}>Valor final com opção de exportação em PDF e compartilhamento por WhatsApp.</p>
              </div>
              <div style={{ display:'flex', gap:12, flexWrap:'wrap' }}>
                <button className="btn-whatsapp" onClick={shareWhatsApp}>📲 Enviar por WhatsApp</button>
                <button className="btn-emerald" onClick={() => setShowPdf(true)}>📄 Imprimir / Salvar PDF</button>
              </div>
            </div>

            {saving > 0 && (
              <div style={{ background:'var(--grad-emerald)', padding:'14px 20px', borderRadius:10, marginBottom:20, color:'#fff', fontWeight:800, fontSize:'1rem' }}>
                🎉 Economia de {fmt(saving)} ({savingPct}% OFF) com peças usadas credenciadas!
              </div>
            )}

            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:16, marginBottom:20 }}>
              <div style={{ padding:18, background:'rgba(10,14,24,.85)', borderRadius:11, border:'1px solid var(--border)' }}>
                <div style={{ fontSize:'.77rem', color:'var(--muted)', fontWeight:700 }}>100% PEÇAS NOVAS OEM</div>
                <div style={{ fontSize:'1.4rem', fontWeight:900, color:'#c084fc', marginTop:4 }}>{fmt(budgetNew)}</div>
              </div>
              <div style={{ padding:18, background:'rgba(245,158,11,.1)', borderRadius:11, border:'2px solid var(--gold)' }}>
                <div style={{ fontSize:'.77rem', color:'var(--gold)', fontWeight:800 }}>ORÇAMENTO SELECIONADO</div>
                <div style={{ fontSize:'1.7rem', fontWeight:900, color:'#fff', marginTop:4 }}>{fmt(budgetSel)}</div>
              </div>
            </div>
          </div>

          {osList.length > 0 && (
            <div className="card" style={{ padding:'24px', marginBottom:32 }}>
              <h2 style={{ fontSize:'1.1rem', fontWeight:800, color:'var(--gold)', marginBottom:16 }}>📂 Histórico de Ordens de Serviço Salvas</h2>
              <div style={{ overflowX:'auto' }}>
                <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom:'1px solid var(--border)', color:'var(--muted)', textAlign:'left' }}>
                      <th style={{ padding:8 }}>Nº OS</th><th style={{ padding:8 }}>Data</th><th style={{ padding:8 }}>Veículo</th><th style={{ padding:8 }}>Cliente</th><th style={{ padding:8 }}>Status</th><th style={{ padding:8, textAlign:'right' }}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {osList.map(os => (
                      <tr key={os.id} style={{ borderBottom:'1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding:8, fontWeight:700, color:'var(--gold)' }}>{os.id}</td>
                        <td style={{ padding:8 }}>{os.date}</td>
                        <td style={{ padding:8 }}>{os.vehicle} ({os.plate})</td>
                        <td style={{ padding:8 }}>{os.client}</td>
                        <td style={{ padding:8 }}><span className="badge badge-used">{os.status}</span></td>
                        <td style={{ padding:8, textAlign:'right', fontWeight:700 }}>{fmt(os.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {showPdf && (
        <div style={{ position:'fixed', inset:0, background:'rgba(0,0,0,.88)', zIndex:9999, display:'flex', alignItems:'center', justifyContent:'center', padding:20 }}>
          <div style={{ background:'#fff', color:'#0f172a', width:'100%', maxWidth:820, maxHeight:'90vh', overflowY:'auto', borderRadius:14, padding:36 }}>
            <div className="no-print" style={{ display:'flex', gap:10, marginBottom:22 }}>
              <button className="btn-gold" onClick={() => window.print()}>🖨️ Imprimir / Salvar PDF</button>
              <button className="btn-ghost" style={{ color:'#334155' }} onClick={() => setShowPdf(false)}>✕ Fechar</button>
            </div>
            <div id="pdf-area">
              <div style={{ borderBottom:'2px solid #e2e8f0', paddingBottom:16, marginBottom:20, display:'flex', justifyContent:'space-between' }}>
                <div>
                  <h1 style={{ fontSize:'1.3rem', color:'#0f172a', fontWeight:900 }}>LAUDO & ORÇAMENTO DE REPAROS AUTOMOTIVOS</h1>
                  <p style={{ fontSize:'.83rem', color:'#64748b' }}>AutoBudget AI v2.5 • Visão Computacional com Tabela FIPE</p>
                </div>
                <div style={{ textAlign:'right', fontSize:'.83rem', color:'#64748b' }}>
                  <div>Data: {new Date().toLocaleDateString('pt-BR')}</div>
                  <div>Nº OS: #{Math.floor(100000 + Math.random()*900000)}</div>
                </div>
              </div>

              {isTotalLoss && (
                <div style={{ background:'#fef2f2', border:'2px solid #ef4444', color:'#991b1b', padding:'12px 16px', borderRadius:8, fontWeight:800, marginBottom:16, fontSize:'.9rem' }}>
                  🚨 ALERTA PERDA TOTAL: Custo do Reparo ({fmt(budgetSel)}) atinge {fipePct}% da Tabela FIPE ({fmt(fipeVal)}).
                </div>
              )}

              <div style={{ background:'#f8fafc', padding:'12px 16px', borderRadius:7, marginBottom:18, fontSize:'.88rem' }}>
                <strong>Veículo:</strong> {vehicle.brand} {vehicle.model} ({vehicle.year}) &nbsp;•&nbsp;
                <strong>Placa:</strong> {vehicle.plate||'N/I'} &nbsp;•&nbsp;
                <strong>FIPE:</strong> {fmt(fipeVal)} ({fipePct}%)
              </div>

              <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'.84rem', marginBottom:22 }}>
                <thead>
                  <tr style={{ background:'#f1f5f9', textAlign:'left' }}>
                    <th style={{ padding:'9px 10px' }}>Item</th><th style={{ padding:'9px 10px' }}>Diagnóstico</th><th style={{ padding:'9px 10px', textAlign:'right' }}>Valor R$</th>
                  </tr>
                </thead>
                <tbody>
                  {parts.map(p => {
                    const v = p.selectedChoice==='new' ? p.newPrice?.price : p.selectedChoice==='used' ? p.usedPrice?.price : 0;
                    return (
                      <tr key={p.id} style={{ borderBottom:'1px solid #e2e8f0' }}>
                        <td style={{ padding:'9px 10px', fontWeight:600 }}>{p.name}</td>
                        <td style={{ padding:'9px 10px' }}>{p.actionRequired}</td>
                        <td style={{ padding:'9px 10px', textAlign:'right', fontWeight:700 }}>{fmt(v)}</td>
                      </tr>
                    );
                  })}
                  <tr style={{ background:'#fafafa' }}>
                    <td colSpan={2} style={{ padding:'9px 10px', fontWeight:600 }}>Mão de Obra Funilaria, Pintura & Montagem</td>
                    <td style={{ padding:'9px 10px', textAlign:'right', fontWeight:700 }}>{fmt(totalLabor)}</td>
                  </tr>
                </tbody>
              </table>

              <div style={{ textAlign:'right', fontSize:'1.4rem', fontWeight:900, borderTop:'2px solid #cbd5e1', paddingTop:12 }}>
                TOTAL: {fmt(budgetSel)}
              </div>
            </div>
          </div>
        </div>
      )}

      <footer style={{ textAlign:'center', padding:'30px 0 20px', fontSize:'.78rem', color:'var(--dim)' }}>
        AutoBudget AI v2.5 © 2026 — Agente de Vistoria, Tabela FIPE e Orçamento Automotivo
      </footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
</script>
</body>
</html>
"""

with open("part3.py", "w", encoding="utf-8") as f:
    f.write('part3 = """' + p3_code + '"""')
print("Wrote part3")
