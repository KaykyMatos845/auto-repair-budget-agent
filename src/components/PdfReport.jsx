import React from 'react';
import { X, Printer, ShieldCheck, CheckCircle2, Car } from 'lucide-react';
import { calculateBudgetTotals, formatCurrency } from '../services/partsSearch';

export default function PdfReport({ vehicle, parts, laborCosts, image, onClose }) {
  const totals = calculateBudgetTotals(parts, laborCosts);

  const handlePrint = () => {
    window.print();
  };

  const currentDate = new Date().toLocaleDateString('pt-BR');

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(8px)',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      overflowY: 'auto'
    }}>
      <div style={{
        background: '#ffffff',
        color: '#1e293b',
        width: '100%',
        maxWidth: '850px',
        borderRadius: '12px',
        boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
        maxHeight: '90vh',
        overflowY: 'auto',
        position: 'relative',
      }}>
        
        {/* Modal Controls (Not visible on print) */}
        <div className="no-print" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 24px',
          background: '#0f172a',
          color: '#fff',
          borderTopLeftRadius: '12px',
          borderTopRightRadius: '12px',
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#fff' }}>
            Visualização de Relatório em PDF / Impressão
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button onClick={handlePrint} className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              <Printer size={16} /> Imprimir / Salvar PDF
            </button>
            <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
              <X size={22} />
            </button>
          </div>
        </div>

        {/* Printable Document Area */}
        <div id="pdf-content" style={{ padding: '40px' }}>
          
          {/* Document Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #e2e8f0', paddingBottom: '20px', marginBottom: '24px' }}>
            <div>
              <h1 style={{ fontSize: '1.6rem', fontWeight: '800', color: '#0f172a', margin: 0, textTransform: 'uppercase' }}>
                Relatório de Orçamento Veicular
              </h1>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
                AutoBudget AI • Sistema Inteligente de Vistoria e Cotação de Peças
              </p>
            </div>

            <div style={{ textAlign: 'right', fontSize: '0.85rem', color: '#475569' }}>
              <div><strong>Nº Orçamento:</strong> #{Math.floor(100000 + Math.random() * 900000)}</div>
              <div><strong>Data:</strong> {currentDate}</div>
              <div><strong>Validade:</strong> 15 dias</div>
            </div>
          </div>

          {/* Vehicle & Client Information Box */}
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px 20px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase' }}>Dados do Veículo</div>
              <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>
                {vehicle?.brand} {vehicle?.model} ({vehicle?.year || 'N/I'})
              </div>
              <div style={{ fontSize: '0.85rem', color: '#475569' }}>
                Placa: <strong>{vehicle?.plate || 'Não informada'}</strong> • Cor: {vehicle?.color || 'N/A'}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase' }}>Proprietário / Cliente</div>
              <div style={{ fontSize: '1rem', fontWeight: '600', color: '#0f172a' }}>
                {vehicle?.clientName || 'Cliente Particular'}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#475569' }}>
                Vistoria Realizada via Inteligência Artificial Multimodal
              </div>
            </div>
          </div>

          {/* Attached Photo */}
          {image && (
            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: '700', color: '#334155', marginBottom: '8px' }}>
                Registro Fotográfico da Vistoria:
              </div>
              <img
                src={image}
                alt="Foto da Vistoria"
                style={{ width: '100%', maxHeight: '240px', objectFit: 'cover', borderRadius: '8px', border: '1px solid #cbd5e1' }}
              />
            </div>
          )}

          {/* Itemized Table */}
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>
              Discriminativo de Peças e Serviços
            </h3>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: '#f1f5f9', color: '#334155', textAlign: 'left' }}>
                  <th style={{ padding: '10px 12px', borderBottom: '2px solid #cbd5e1' }}>Item / Componente</th>
                  <th style={{ padding: '10px 12px', borderBottom: '2px solid #cbd5e1' }}>Diagnóstico IA</th>
                  <th style={{ padding: '10px 12px', borderBottom: '2px solid #cbd5e1' }}>Origem Peça</th>
                  <th style={{ padding: '10px 12px', borderBottom: '2px solid #cbd5e1', textAlign: 'right' }}>Valor R$</th>
                </tr>
              </thead>
              <tbody>
                {parts.map((p) => {
                  const val = p.selectedChoice === 'new' 
                    ? p.newPrice?.price 
                    : p.selectedChoice === 'used' 
                    ? p.usedPrice?.price 
                    : 0;

                  return (
                    <tr key={p.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '10px 12px', fontWeight: '600' }}>{p.name}</td>
                      <td style={{ padding: '10px 12px', color: '#475569' }}>{p.actionRequired}</td>
                      <td style={{ padding: '10px 12px', color: '#475569' }}>
                        {p.selectedChoice === 'new' ? 'Nova OEM' : p.selectedChoice === 'used' ? 'Usada Credenciada DETRAN' : 'Recuperada'}
                      </td>
                      <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: '700' }}>
                        {formatCurrency(val)}
                      </td>
                    </tr>
                  );
                })}

                <tr style={{ borderBottom: '1px solid #e2e8f0', background: '#fafafa' }}>
                  <td style={{ padding: '10px 12px', fontWeight: '600' }} colSpan="3">Serviço de Funilaria & Martelinho ({laborCosts.bodyworkHours || 0} horas)</td>
                  <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: '700' }}>{formatCurrency(totals.bodyworkTotal)}</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #e2e8f0', background: '#fafafa' }}>
                  <td style={{ padding: '10px 12px', fontWeight: '600' }} colSpan="3">Pintura e Preparação de Estufa ({laborCosts.paintPanels || 0} painéis)</td>
                  <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: '700' }}>{formatCurrency(totals.paintTotal)}</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #e2e8f0', background: '#fafafa' }}>
                  <td style={{ padding: '10px 12px', fontWeight: '600' }} colSpan="3">Mecânica, Desmontagem & Alinhamento</td>
                  <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: '700' }}>{formatCurrency(totals.mechanicTotal)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Totals & Savings Summary */}
          <div style={{ background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '18px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
            <div>
              {totals.savingsAmount > 0 && (
                <div style={{ fontSize: '0.85rem', color: '#15803d', fontWeight: '700' }}>
                  ✓ Economia obtida com Peças Usadas: {formatCurrency(totals.savingsAmount)} (-{totals.savingsPercent}%)
                </div>
              )}
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Valor Total de Peças 100% Novas: {formatCurrency(totals.totalNewScenario)}
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase' }}>Valor Total Orçado</div>
              <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#0f172a' }}>
                {formatCurrency(totals.totalSelectedBudget)}
              </div>
            </div>
          </div>

          {/* Signatures */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '50px', paddingTop: '20px', borderTop: '1px solid #e2e8f0' }}>
            <div style={{ textAlign: 'center', width: '220px' }}>
              <div style={{ borderTop: '1px solid #94a3b8', paddingTop: '4px', fontSize: '0.8rem', fontWeight: '600', color: '#475569' }}>
                Vistoriador / Responsável Técnico
              </div>
            </div>

            <div style={{ textAlign: 'center', width: '220px' }}>
              <div style={{ borderTop: '1px solid #94a3b8', paddingTop: '4px', fontSize: '0.8rem', fontWeight: '600', color: '#475569' }}>
                De Acordo - Cliente
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* Print Styles */}
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #pdf-content, #pdf-content * {
            visibility: visible;
          }
          #pdf-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            padding: 0;
          }
          .no-print {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}
