import React from 'react';
import { Car, Tag, Calendar, User, ShieldCheck } from 'lucide-react';
import { commonVehicleBrands } from '../data/mockData';

export default function VehicleDetails({ vehicle, setVehicle }) {
  const handleChange = (field, value) => {
    setVehicle((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Car size={20} color="var(--accent-cyan)" />
          2. Dados do Veículo & Cliente
        </h2>
        {vehicle.detectedAutomatically && (
          <span className="badge badge-paint">
            <ShieldCheck size={13} /> Identificado pela IA
          </span>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        
        {/* Marca */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '600' }}>
            Marca / Fabricante
          </label>
          <select
            value={vehicle.brand || ''}
            onChange={(e) => handleChange('brand', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          >
            <option value="">Selecione a marca...</option>
            {commonVehicleBrands.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>

        {/* Modelo */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '600' }}>
            Modelo / Versão
          </label>
          <input
            type="text"
            placeholder="Ex: Civic 1.5 Touring / Corolla XEi"
            value={vehicle.model || ''}
            onChange={(e) => handleChange('model', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

        {/* Ano */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '600' }}>
            Ano de Fabricação/Modelo
          </label>
          <input
            type="text"
            placeholder="Ex: 2021"
            value={vehicle.year || ''}
            onChange={(e) => handleChange('year', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

        {/* Placa */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '600' }}>
            Placa do Veículo
          </label>
          <input
            type="text"
            placeholder="ABC-1D23"
            value={vehicle.plate || ''}
            onChange={(e) => handleChange('plate', e.target.value.toUpperCase())}
            style={{
              width: '100%',
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

        {/* Proprietário */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '600' }}>
            Cliente / Proprietário
          </label>
          <input
            type="text"
            placeholder="Nome do cliente"
            value={vehicle.clientName || ''}
            onChange={(e) => handleChange('clientName', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

      </div>
    </div>
  );
}
