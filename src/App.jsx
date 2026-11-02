import React, { useState } from 'react';
import Header from './components/Header';
import SamplePicker from './components/SamplePicker';
import ImageUploader from './components/ImageUploader';
import VehicleDetails from './components/VehicleDetails';
import DamageAnalysis from './components/DamageAnalysis';
import PartsMarketplace from './components/PartsMarketplace';
import LaborEstimator from './components/LaborEstimator';
import BudgetSummary from './components/BudgetSummary';
import PdfReport from './components/PdfReport';
import { analyzeVehicleDamage } from './services/geminiApi';

export default function App() {
  const [selectedImages, setSelectedImages] = useState([]);
  const [vehicle, setVehicle] = useState({
    brand: '',
    model: '',
    year: '',
    plate: '',
    color: '',
    clientName: '',
  });

  const [damageAnalysis, setDamageAnalysis] = useState(null);
  const [parts, setParts] = useState([]);
  const [laborCosts, setLaborCosts] = useState({
    bodyworkHours: 10,
    bodyworkRate: 90,
    paintPanels: 2,
    paintRatePerPanel: 450,
    mechanicMontage: 350,
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showPdf, setShowPdf] = useState(false);

  // Trigger analysis on uploaded images
  const handleStartAnalysis = async () => {
    if (selectedImages.length === 0) return;
    setIsAnalyzing(true);

    try {
      const result = await analyzeVehicleDamage(selectedImages, vehicle);
      if (result.success) {
        setVehicle((prev) => ({
          ...prev,
          ...result.vehicle,
        }));
        setDamageAnalysis(result.damageAnalysis);
        setParts(result.damageAnalysis.parts || []);
        if (result.damageAnalysis.laborCosts) {
          setLaborCosts(result.damageAnalysis.laborCosts);
        }
      }
    } catch (err) {
      console.error('Falha ao analisar fotos:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Load pre-configured demonstration sample case
  const handleSelectSample = (sample) => {
    setSelectedImages([sample.image]);
    setVehicle(sample.vehicle);
    setDamageAnalysis(sample.damageAnalysis);
    setParts(sample.damageAnalysis.parts);
    setLaborCosts(sample.damageAnalysis.laborCosts);
  };

  // Reset all fields for a fresh budget
  const handleReset = () => {
    setSelectedImages([]);
    setVehicle({
      brand: '',
      model: '',
      year: '',
      plate: '',
      color: '',
      clientName: '',
    });
    setDamageAnalysis(null);
    setParts([]);
    setLaborCosts({
      bodyworkHours: 8,
      bodyworkRate: 90,
      paintPanels: 2,
      paintRatePerPanel: 450,
      mechanicMontage: 300,
    });
    setShowPdf(false);
  };

  return (
    <div className="app-container">
      
      {/* Header */}
      <Header onReset={handleReset} />

      {/* Preset Sample Picker */}
      <SamplePicker onSelectSample={handleSelectSample} />

      {/* Image Uploader & Vision Trigger */}
      <ImageUploader
        selectedImages={selectedImages}
        setSelectedImages={setSelectedImages}
        onStartAnalysis={handleStartAnalysis}
        isAnalyzing={isAnalyzing}
      />

      {/* Vehicle & Client Information */}
      <VehicleDetails vehicle={vehicle} setVehicle={setVehicle} />

      {/* Visual Damage Analysis Results */}
      {damageAnalysis && (
        <div className="animate-fade-in">
          
          <DamageAnalysis
            damageAnalysis={damageAnalysis}
            setParts={setParts}
            vehicle={vehicle}
          />

          {/* Parts Marketplace Comparison (New vs Used) */}
          <PartsMarketplace
            parts={parts}
            setParts={setParts}
          />

          {/* Workshop Labor Estimator */}
          <LaborEstimator
            laborCosts={laborCosts}
            setLaborCosts={setLaborCosts}
          />

          {/* Final Budget & Savings Breakdown */}
          <BudgetSummary
            parts={parts}
            laborCosts={laborCosts}
            vehicle={vehicle}
            onOpenPdf={() => setShowPdf(true)}
          />

        </div>
      )}

      {/* PDF / Printable Modal */}
      {showPdf && (
        <PdfReport
          vehicle={vehicle}
          parts={parts}
          laborCosts={laborCosts}
          image={selectedImages[0] || null}
          onClose={() => setShowPdf(false)}
        />
      )}

      {/* Footer */}
      <footer style={{ textAlign: 'center', margin: '40px 0 20px 0', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
        AutoBudget AI © 2026 • Agente de IA para Vistoria, Orçamento de Reparos e Cotação de Peças Automotivas
      </footer>

    </div>
  );
}
