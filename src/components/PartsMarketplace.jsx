import React from 'react';
import { ShoppingCart, ExternalLink, Check, Tag, ShieldCheck, Sparkles, TrendingDown } from 'lucide-react';
import { formatCurrency } from '../services/partsSearch';

export default function PartsMarketplace({ parts, setParts }) {
  const handleSelectOption = (partId, choice) => {
    setParts((prev) =>
      prev.map((item) => (item.id === partId ? { ...item, selectedChoice: choice } : item))
    );
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Section Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShoppingCart size={20} color="var(--accent-emerald)" />
            4. Cotação de Mercado: Peças Novas vs. Peças Usadas (Desmanche Credenciado)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            O agente pesquisou o mercado em tempo real. Escolha para cada item a opção desejada para compor o orçamento final.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.8rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#60a5fa' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }}></span> Nova
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span> Usada/Seminova
          </span>
        </div>
      </div>

      {/* Parts Marketplace Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {parts.map((part) => {
          const isRepairOnly = part.selectedChoice === 'repair' || part.actionRequired === 'Recuperação';
          const newP = part.newPrice?.price || 0;
          const usedP = part.usedPrice?.price || 0;
          const diff = Math.max(0, newP - usedP);
          const percentSaved = newP > 0 ? ((diff / newP) * 100).toFixed(0) : 0;

          return (
            <div
              key={part.id}
              style={{
                background: 'rgba(15, 23, 42, 0.75)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                padding: '18px 20px',
              }}
            >
              {/* Part Title & Status Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-main)' }}>
                    {part.name}
                  </h3>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                    Categoria: {part.category} • Recomendação IA: {part.actionRequired}
                  </span>
                </div>

                {!isRepairOnly && diff > 0 && (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '6px', 
                    padding: '4px 10px', 
                    background: 'rgba(16, 185, 129, 0.12)', 
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.78rem',
                    color: '#34d399',
                    fontWeight: '700'
                  }}>
                    <TrendingDown size={14} /> Economia de {formatCurrency(diff)} ({percentSaved}% OFF na Usada)
                  </div>
                )}
              </div>

              {/* Special View for Repair items */}
              {isRepairOnly ? (
                <div style={{ 
                  padding: '14px 18px', 
                  background: 'rgba(245, 158, 11, 0.08)', 
                  border: '1px solid rgba(245, 158, 11, 0.25)', 
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <div style={{ fontSize: '0.85rem', color: 'var(--accent-amber)' }}>
                    🛠️ <strong>Item para Funilaria / Recuperação:</strong> A peça original do veículo será recuperada. O valor do reparo já está incluso na mão de obra de funilaria/pintura.
                  </div>
                  <button
                    onClick={() => handleSelectOption(part.id, 'used')}
                    className="btn-secondary"
                    style={{ fontSize: '0.78rem', padding: '6px 12px' }}
                  >
                    Trocar por Peça de Mercado
                  </button>
                </div>
              ) : (
                /* Comparison Grid: NEW vs USED */
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
                  
                  {/* Option 1: PEÇA NOVA */}
                  <div
                    onClick={() => handleSelectOption(part.id, 'new')}
                    style={{
                      padding: '16px',
                      borderRadius: 'var(--radius-sm)',
                      background: part.selectedChoice === 'new' ? 'rgba(59, 130, 246, 0.12)' : 'rgba(30, 41, 59, 0.4)',
                      border: part.selectedChoice === 'new' ? '2px solid var(--accent-primary)' : '1px solid var(--border-color)',
                      cursor: 'pointer',
                      transition: 'var(--transition-fast)',
                      position: 'relative'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span className="badge badge-new">Peça Nova</span>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        border: part.selectedChoice === 'new' ? '6px solid var(--accent-primary)' : '2px solid var(--text-dim)',
                        background: '#fff'
                      }}></div>
                    </div>

                    <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#60a5fa', marginBottom: '4px' }}>
                      {formatCurrency(newP)}
                    </div>

                    <p style={{ fontSize: '0.82rem', fontWeight: '600', color: 'var(--text-main)', marginBottom: '4px' }}>
                      {part.newPrice?.brandName || 'Original OEM'}
                    </p>

                    <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
                      Fornecedor: {part.newPrice?.supplier || 'Concessionária / Autopeças'}
                    </p>

                    {part.newPrice?.link && part.newPrice.link !== '#' && (
                      <a
                        href={part.newPrice.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.75rem',
                          color: 'var(--accent-primary)',
                          textDecoration: 'none',
                          fontWeight: '600'
                        }}
                      >
                        Ver Cotação no Mercado Livre <ExternalLink size={12} />
                      </a>
                    )}
                  </div>

                  {/* Option 2: PEÇA USADA / SEMINOVA */}
                  <div
                    onClick={() => handleSelectOption(part.id, 'used')}
                    style={{
                      padding: '16px',
                      borderRadius: 'var(--radius-sm)',
                      background: part.selectedChoice === 'used' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(30, 41, 59, 0.4)',
                      border: part.selectedChoice === 'used' ? '2px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                      cursor: 'pointer',
                      transition: 'var(--transition-fast)',
                      position: 'relative'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span className="badge badge-used">
                        <ShieldCheck size={12} /> Peça Usada Credenciada
                      </span>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        border: part.selectedChoice === 'used' ? '6px solid var(--accent-emerald)' : '2px solid var(--text-dim)',
                        background: '#fff'
                      }}></div>
                    </div>

                    <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#34d399', marginBottom: '4px' }}>
                      {formatCurrency(usedP)}
                    </div>

                    <p style={{ fontSize: '0.82rem', fontWeight: '600', color: 'var(--text-main)', marginBottom: '4px' }}>
                      {part.usedPrice?.brandName || 'Original Seminova com Nota Fiscal'}
                    </p>

                    <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
                      Origem: {part.usedPrice?.supplier || 'Desmanche Credenciado Detran com NF'}
                    </p>

                    {part.usedPrice?.link && part.usedPrice.link !== '#' && (
                      <a
                        href={part.usedPrice.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.75rem',
                          color: 'var(--accent-emerald)',
                          textDecoration: 'none',
                          fontWeight: '600'
                        }}
                      >
                        Ver no Desmanche Credenciado ML <ExternalLink size={12} />
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
  );
}
