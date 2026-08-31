import React from 'react';
import { Wrench, Paintbrush, Hammer, DollarSign } from 'lucide-react';
import { formatCurrency } from '../services/partsSearch';

export default function LaborEstimator({ laborCosts, setLaborCosts }) {
  const handleChange = (field, value) => {
    const numVal = parseFloat(value) || 0;
    setLaborCosts((prev) => ({ ...prev, [field]: numVal }));
  };

  const bodyworkTotal = (laborCosts.bodyworkHours || 0) * (laborCosts.bodyworkRate || 0);
  const paintTotal = (laborCosts.paintPanels || 0) * (laborCosts.paintRatePerPanel || 0);
  const mechanicTotal = laborCosts.mechanicMontage || 0;
  const totalLabor = bodyworkTotal + paintTotal + mechanicTotal;

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Wrench size={20} color="var(--accent-purple)" />
            5. Estimativa de Mão de Obra & Serviços de Oficina
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Ajuste a quantidade de horas e taxas de serviço conforme a tabela da sua oficina.
          </p>
        </div>

        <div style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--accent-purple)' }}>
          Total Mão de Obra: {formatCurrency(totalLabor)}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px' }}>
        
        {/* Funilaria */}
        <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Hammer size={18} color="var(--accent-amber)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700' }}>Funilaria & Desamassamento</h4>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Horas estimadas de funilaria:
            </label>
            <input
              type="number"
              min="0"
              value={laborCosts.bodyworkHours || 0}
              onChange={(e) => handleChange('bodyworkHours', e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '0.9rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Valor da Hora Técnica (R$):
            </label>
            <input
              type="number"
              min="0"
              value={laborCosts.bodyworkRate || 0}
              onChange={(e) => handleChange('bodyworkRate', e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '0.9rem',
              }}
            />
          </div>

          <div style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-main)', textAlign: 'right' }}>
            Subtotal Funilaria: {formatCurrency(bodyworkTotal)}
          </div>
        </div>

        {/* Pintura */}
        <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Paintbrush size={18} color="var(--accent-cyan)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700' }}>Pintura & Estufa</h4>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Número de peças/painéis a pintar:
            </label>
            <input
              type="number"
              min="0"
              value={laborCosts.paintPanels || 0}
              onChange={(e) => handleChange('paintPanels', e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '0.9rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Valor médio de pintura por peça (R$):
            </label>
            <input
              type="number"
              min="0"
              value={laborCosts.paintRatePerPanel || 0}
              onChange={(e) => handleChange('paintRatePerPanel', e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '0.9rem',
              }}
            />
          </div>

          <div style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-main)', textAlign: 'right' }}>
            Subtotal Pintura: {formatCurrency(paintTotal)}
          </div>
        </div>

        {/* Mecânica / Desmontagem */}
        <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Wrench size={18} color="var(--accent-primary)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700' }}>Mecânica & Montagem</h4>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Taxa de desmontagem/montagem e alinhamento (R$):
            </label>
            <input
              type="number"
              min="0"
              value={laborCosts.mechanicMontage || 0}
              onChange={(e) => handleChange('mechanicMontage', e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '0.9rem',
              }}
            />
          </div>

          <div style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-main)', textAlign: 'right' }}>
            Subtotal Montagem: {formatCurrency(mechanicTotal)}
          </div>
        </div>

      </div>
    </div>
  );
}
