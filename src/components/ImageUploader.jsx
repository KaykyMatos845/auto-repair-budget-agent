import React, { useRef } from 'react';
import { UploadCloud, Camera, Image as ImageIcon, X, Sparkles, CheckCircle2 } from 'lucide-react';

export default function ImageUploader({ selectedImages, setSelectedImages, onStartAnalysis, isAnalyzing }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    const newImages = files.map((file) => URL.createObjectURL(file));
    setSelectedImages((prev) => [...prev, ...newImages]);
  };

  const removeImage = (index) => {
    setSelectedImages((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Camera size={20} color="var(--accent-primary)" />
            1. Fotos da Vistoria & Avarias do Veículo
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Envie uma ou mais fotos do veículo danificado (ângulo geral e detalhes do dano).
          </p>
        </div>

        {selectedImages.length > 0 && (
          <span style={{ fontSize: '0.85rem', color: 'var(--accent-emerald)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={16} /> {selectedImages.length} foto(s) anexada(s)
          </span>
        )}
      </div>

      {/* Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: '2px dashed rgba(59, 130, 246, 0.3)',
          borderRadius: 'var(--radius-md)',
          padding: '32px 20px',
          textAlign: 'center',
          background: 'rgba(15, 23, 42, 0.4)',
          cursor: 'pointer',
          transition: 'var(--transition-normal)',
          marginBottom: selectedImages.length > 0 ? '20px' : '0',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'var(--accent-primary)';
          e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
          e.currentTarget.style.background = 'rgba(15, 23, 42, 0.4)';
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          accept="image/*"
          style={{ display: 'none' }}
        />
        <div style={{ 
          width: '54px', 
          height: '54px', 
          borderRadius: '50%', 
          background: 'rgba(59, 130, 246, 0.12)', 
          margin: '0 auto 12px auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-primary)'
        }}>
          <UploadCloud size={28} />
        </div>
        <h4 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: '4px' }}>
          Clique para selecionar fotos do seu dispositivo
        </h4>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Suporta JPG, PNG, WEBP — Você pode enviar fotos tiradas pelo celular
        </p>
      </div>

      {/* Selected Image Thumbnails */}
      {selectedImages.length > 0 && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '12px', marginBottom: '20px' }}>
            {selectedImages.map((imgUrl, index) => (
              <div key={index} style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden', height: '100px', border: '1px solid var(--border-color)' }}>
                <img src={imgUrl} alt={`Avaria ${index + 1}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeImage(index);
                  }}
                  style={{
                    position: 'absolute',
                    top: '6px',
                    right: '6px',
                    background: 'rgba(0, 0, 0, 0.7)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '50%',
                    width: '24px',
                    height: '24px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              onClick={onStartAnalysis}
              disabled={isAnalyzing}
              className="btn-primary"
              style={{ padding: '14px 28px', fontSize: '0.95rem' }}
            >
              {isAnalyzing ? (
                <>
                  <span className="pulse-glow">Analisando fotos com Visão IA...</span>
                </>
              ) : (
                <>
                  <Sparkles size={18} /> Analisar Fotos com IA & Identificar Peças
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
