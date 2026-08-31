import React from 'react';
import { Car, Sparkles, RefreshCw, FileCheck2 } from 'lucide-react';

export default function Header({ onReset, currentStep }) {
  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '28px', borderTop: '2px solid var(--accent-primary)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand Logo & Name */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            background: 'var(--gradient-brand)',
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-glow)'
          }}>
            <Car size={26} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.4rem', fontWeight: '800' }}>
                AutoBudget <span className="gradient-text">AI</span>
              </h1>
              <span className="badge badge-new" style={{ fontSize: '0.65rem' }}>
                <Sparkles size={12} /> Agente Vistoriador
              </span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Orçamento de Reparos com Análise por Fotos e Cotação de Peças Novas vs. Usadas
            </p>
          </div>
        </div>

        {/* Status & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px', 
            padding: '6px 14px', 
            borderRadius: 'var(--radius-full)', 
            background: 'rgba(16, 185, 129, 0.1)', 
            border: '1px solid rgba(16, 185, 129, 0.25)',
            fontSize: '0.8rem',
            color: '#34d399',
            fontWeight: '600'
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} className="pulse-glow"></span>
            Mercado em Tempo Real (ML & Desmanches)
          </div>

          <button onClick={onReset} className="btn-secondary" style={{ fontSize: '0.85rem' }}>
            <RefreshCw size={15} /> Novo Orçamento
          </button>
        </div>

      </div>
    </header>
  );
}
