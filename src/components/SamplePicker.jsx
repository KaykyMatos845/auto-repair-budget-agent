import React from 'react';
import { sampleCases } from '../data/mockData';
import { Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

export default function SamplePicker({ onSelectSample }) {
  return (
    <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '24px', background: 'rgba(30, 41, 59, 0.4)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={18} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>Demonstração Instantânea com Casos Reais</h3>
        </div>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Clique para testar a IA imediatamente</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        {sampleCases.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelectSample(item)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              padding: '12px 16px',
              background: 'rgba(15, 23, 42, 0.6)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-color)',
              cursor: 'pointer',
              transition: 'var(--transition-fast)',
            }}
            className="sample-card-hover"
            onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
          >
            <img
              src={item.image}
              alt={item.title}
              style={{
                width: '74px',
                height: '74px',
                objectFit: 'cover',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
              }}
            />
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-main)', marginBottom: '4px' }}>
                {item.title}
              </h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>
                {item.description}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px', fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                <span>Carregar e Analisar</span>
                <ArrowRight size={12} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
