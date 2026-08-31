import React, { useState } from 'react';
import { AlertTriangle, Plus, Trash2, Check, Sparkles, Wrench, Search } from 'lucide-react';
import { searchPartPrices } from '../services/geminiApi';

export default function DamageAnalysis({ damageAnalysis, setParts, vehicle }) {
  const [newItemName, setNewItemName] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('Lataria');
  const [isSearchingCustom, setIsSearchingCustom] = useState(false);

  const parts = damageAnalysis?.parts || [];

  const handleAddManualPart = async (e) => {
    e.preventDefault();
    if (!newItemName.trim()) return;

    setIsSearchingCustom(true);

    const priceResult = await searchPartPrices(
      vehicle?.brand || 'Universal',
      vehicle?.model || 'Modelo',
      vehicle?.year || '2021',
      newItemName
    );

    const newPart = {
      id: `custom-${Date.now()}`,
      name: newItemName.trim(),
      category: newItemCategory,
      actionRequired: 'Substituição',
      severity: 'Médio',
      confidence: 1.0,
      newPrice: priceResult.prices.newPrice,
      usedPrice: priceResult.prices.usedPrice,
      selectedChoice: 'used',
    };

    setParts((prev) => [...prev, newPart]);
    setNewItemName('');
    setIsSearchingCustom(false);
  };

  const handleRemovePart = (id) => {
    setParts((prev) => prev.filter((p) => p.id !== id));
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} color="var(--accent-amber)" />
            3. Relatório de Vistoria de Avarias & Peças Afetadas
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            {damageAnalysis?.summary || 'Identificação automática de componentes danificados pela IA.'}
          </p>
        </div>

        {damageAnalysis?.overallSeverity && (
          <div style={{ padding: '6px 12px', background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px', fontSize: '0.8rem', color: 'var(--accent-amber)', fontWeight: '600' }}>
            Severidade Global: {damageAnalysis.overallSeverity}
          </div>
        )}
      </div>

      {/* Parts List Identified */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
        {parts.map((part, idx) => (
          <div
            key={part.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '14px 18px',
              background: 'rgba(15, 23, 42, 0.7)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-color)',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: 1, minWidth: '240px' }}>
              <span style={{ 
                width: '28px', 
                height: '28px', 
                borderRadius: '50%', 
                background: 'rgba(59, 130, 246, 0.15)', 
                color: 'var(--accent-primary)',
                fontWeight: '700',
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                {idx + 1}
              </span>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-main)' }}>
                    {part.name}
                  </h4>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
                    {part.category}
                  </span>
                </div>
                {part.notes && (
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {part.notes}
                  </p>
                )}
              </div>
            </div>

            {/* Action Badges */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {part.actionRequired === 'Substituição' ? (
                <span className="badge badge-replace">Substituir Peça</span>
              ) : (
                <span className="badge badge-repair">Funilaria / Recuperar</span>
              )}

              {part.confidence && (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  IA: {(part.confidence * 100).toFixed(0)}%
                </span>
              )}

              <button
                onClick={() => handleRemovePart(part.id)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-dim)',
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '4px',
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--accent-rose)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-dim)'}
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add Manual Item Form */}
      <form onSubmit={handleAddManualPart} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Adicionar outra peça danificada (ex: Absorvedor do choque, Moldura do milha...)"
          value={newItemName}
          onChange={(e) => setNewItemName(e.target.value)}
          style={{
            flex: 2,
            minWidth: '240px',
            padding: '10px 14px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-main)',
            fontSize: '0.88rem',
            outline: 'none',
          }}
        />

        <select
          value={newItemCategory}
          onChange={(e) => setNewItemCategory(e.target.value)}
          style={{
            flex: 1,
            minWidth: '140px',
            padding: '10px 14px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-main)',
            fontSize: '0.88rem',
            outline: 'none',
          }}
        >
          <option value="Lataria">Lataria</option>
          <option value="Carroceria">Carroceria</option>
          <option value="Iluminação">Iluminação</option>
          <option value="Mecânica">Mecânica</option>
          <option value="Vidros">Vidros</option>
          <option value="Elétrica">Elétrica</option>
        </select>

        <button type="submit" disabled={isSearchingCustom || !newItemName.trim()} className="btn-secondary" style={{ fontSize: '0.85rem' }}>
          {isSearchingCustom ? (
            <span className="pulse-glow">Buscando cotação...</span>
          ) : (
            <>
              <Plus size={16} /> Adicionar & Cotar
            </>
          )}
        </button>
      </form>

    </div>
  );
}
