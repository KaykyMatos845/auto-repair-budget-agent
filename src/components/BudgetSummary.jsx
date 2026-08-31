import React from 'react';
import { Calculator, FileText, Download, TrendingDown, ArrowRight, CheckCircle, Printer } from 'lucide-react';
import { calculateBudgetTotals, formatCurrency } from '../services/partsSearch';

export default function BudgetSummary({ parts, laborCosts, vehicle, onOpenPdf }) {
  const totals = calculateBudgetTotals(parts, laborCosts);

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '32px', border: '1px solid rgba(59, 130, 246, 0.3)', boxShadow: 'var(--shadow-glow)' }}>
      
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Calculator size={24} color="var(--accent-primary)" />
            6. Resumo Final do Orçamento de Reparo
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Comparativo de economia e total final para aprovação do cliente ou seguradora.
          </p>
        </div>

        <button onClick={onOpenPdf} className="btn-success" style={{ fontSize: '0.95rem', padding: '12px 24px' }}>
          <FileText size={18} /> Imprimir / Exportar Orçamento PDF
        </button>
      </div>

      {/* Savings Highlight Box */}
      {totals.savingsAmount > 0 && (
        <div style={{
          background: 'var(--gradient-used-badge)',
          borderRadius: 'var(--radius-md)',
          padding: '20px 24px',
          marginBottom: '24px',
          color: '#ffffff',
          boxShadow: 'var(--shadow-emerald)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.2)', padding: '10px', borderRadius: '50%' }}>
              <TrendingDown size={28} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: '800' }}>
                Economia Inteligente Aplicada: {formatCurrency(totals.savingsAmount)}
              </h3>
              <p style={{ fontSize: '0.85rem', opacity: 0.9 }}>
                Ao utilizar peças usadas/seminovas credenciadas no seu orçamento, você reduziu o custo em <strong>{totals.savingsPercent}%</strong> em comparação com peças 100% novas originais.
              </p>
            </div>
          </div>

          <div style={{ fontSize: '1.4rem', fontWeight: '800', background: 'rgba(0,0,0,0.2)', padding: '8px 18px', borderRadius: '8px' }}>
            -{totals.savingsPercent}% OFF
          </div>
        </div>
      )}

      {/* Scenarios Comparison Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        
        {/* Scenario 1: All New */}
        <div style={{ padding: '20px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', marginBottom: '4px' }}>
            Cenário 1: 100% Peças Novas OEM
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#60a5fa', marginBottom: '12px' }}>
            {formatCurrency(totals.totalNewScenario)}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>Peças Novas: {formatCurrency(totals.totalNewParts)}</div>
            <div>Mão de Obra: {formatCurrency(totals.totalLabor)}</div>
          </div>
        </div>

        {/* Scenario 2: All Used */}
        <div style={{ padding: '20px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', marginBottom: '4px' }}>
            Cenário 2: 100% Peças Usadas Credenciadas
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#34d399', marginBottom: '12px' }}>
            {formatCurrency(totals.totalUsedScenario)}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>Peças Usadas: {formatCurrency(totals.totalUsedParts)}</div>
            <div>Mão de Obra: {formatCurrency(totals.totalLabor)}</div>
          </div>
        </div>

        {/* Selected Budget Result */}
        <div style={{ padding: '20px', background: 'rgba(59, 130, 246, 0.12)', borderRadius: 'var(--radius-md)', border: '2px solid var(--accent-primary)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' }}>
            Orçamento Atual Selecionado
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#ffffff', marginBottom: '12px' }}>
            {formatCurrency(totals.totalSelectedBudget)}
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>Peças Escolhidas: {formatCurrency(totals.totalSelectedParts)}</div>
            <div>Mão de Obra Total: {formatCurrency(totals.totalLabor)}</div>
          </div>
        </div>

      </div>

      {/* Itemized Table */}
      <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '10px' }}>Item / Componente</th>
              <th style={{ padding: '10px' }}>Ação Recomendada</th>
              <th style={{ padding: '10px' }}>Escolha</th>
              <th style={{ padding: '10px', textAlign: 'right' }}>Valor Peça</th>
            </tr>
          </thead>
          <tbody>
            {parts.map((p) => {
              const selectedPrice = p.selectedChoice === 'new' 
                ? p.newPrice?.price 
                : p.selectedChoice === 'used' 
                ? p.usedPrice?.price 
                : 0;

              return (
                <tr key={p.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 10px', fontWeight: '600' }}>{p.name}</td>
                  <td style={{ padding: '12px 10px' }}>
                    <span className={p.actionRequired === 'Substituição' ? 'badge badge-replace' : 'badge badge-repair'}>
                      {p.actionRequired}
                    </span>
                  </td>
                  <td style={{ padding: '12px 10px' }}>
                    {p.selectedChoice === 'new' ? (
                      <span className="badge badge-new">Nova</span>
                    ) : p.selectedChoice === 'used' ? (
                      <span className="badge badge-used">Usada Credenciada</span>
                    ) : (
                      <span className="badge badge-repair">Recuperar</span>
                    )}
                  </td>
                  <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700' }}>
                    {formatCurrency(selectedPrice)}
                  </td>
                </tr>
              );
            })}

            {/* Services Rows */}
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)' }}>
              <td style={{ padding: '12px 10px', fontWeight: '600' }} colSpan="3">Serviço de Funilaria & Desamassamento ({laborCosts.bodyworkHours || 0}h)</td>
              <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700' }}>{formatCurrency(totals.bodyworkTotal)}</td>
            </tr>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)' }}>
              <td style={{ padding: '12px 10px', fontWeight: '600' }} colSpan="3">Serviço de Pintura & Estufa ({laborCosts.paintPanels || 0} peça(s))</td>
              <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700' }}>{formatCurrency(totals.paintTotal)}</td>
            </tr>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)' }}>
              <td style={{ padding: '12px 10px', fontWeight: '600' }} colSpan="3">Mecânica, Desmontagem & Montagem</td>
              <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700' }}>{formatCurrency(totals.mechanicTotal)}</td>
            </tr>

            {/* Total Row */}
            <tr style={{ fontSize: '1.05rem', fontWeight: '800', color: 'var(--accent-primary)' }}>
              <td style={{ padding: '16px 10px' }} colSpan="3">TOTAL GERAL ESTIMADO DO REPARO</td>
              <td style={{ padding: '16px 10px', textAlign: 'right' }}>{formatCurrency(totals.totalSelectedBudget)}</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  );
}
