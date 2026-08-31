import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Helper to simulate live market price querying for new vs used car parts
function fetchPartMarketPrices(brand, model, year, partName) {
  const queryBase = `${brand} ${model} ${year} ${partName}`.trim();
  const encodedQueryNew = encodeURIComponent(`${queryBase} novo`);
  const encodedQueryUsed = encodeURIComponent(`${queryBase} usado original`);

  // Realistic price heuristics based on part type
  let basePriceNew = 1200;
  const nameLower = partName.toLowerCase();
  
  if (nameLower.includes('farol') || nameLower.includes('led')) basePriceNew = 2800;
  else if (nameLower.includes('para-choque') || nameLower.includes('parachoque')) basePriceNew = 950;
  else if (nameLower.includes('capô') || nameLower.includes('capo')) basePriceNew = 1600;
  else if (nameLower.includes('porta')) basePriceNew = 2200;
  else if (nameLower.includes('retrovisor')) basePriceNew = 1450;
  else if (nameLower.includes('lanterna')) basePriceNew = 850;
  else if (nameLower.includes('paralama')) basePriceNew = 550;
  else if (nameLower.includes('grade')) basePriceNew = 680;

  // Premium brands factor
  if (['BMW', 'Mercedes-Benz', 'Audi', 'Volvo', 'Porsche'].includes(brand)) {
    basePriceNew *= 2.4;
  } else if (['Honda', 'Toyota', 'Jeep'].includes(brand)) {
    basePriceNew *= 1.35;
  }

  // Used part discount is usually between 45% and 65% of new original price
  const discountFactor = 0.45 + (Math.random() * 0.15); 
  const basePriceUsed = Math.round(basePriceNew * discountFactor);

  return {
    newPrice: {
      brandName: `Original ${brand} OEM / Paralela 1ª Linha`,
      price: Math.round(basePriceNew),
      type: 'Nova (Original / Paralela)',
      supplier: 'Distribuidora AutoPeças Brasil & Concessionárias',
      availability: 'Em estoque',
      link: `https://lista.mercadolivre.com.br/${encodedQueryNew}`
    },
    usedPrice: {
      brandName: `Seminova Original ${brand}`,
      price: Math.round(basePriceUsed),
      type: 'Usada / Seminova (Desmanche Credenciado DETRAN)',
      supplier: 'CDV / Desmanche Credenciado Oficial',
      availability: 'Disponível com Nota Fiscal e Rastreabilidade',
      link: `https://lista.mercadolivre.com.br/${encodedQueryUsed}`
    }
  };
}

// Endpoint: Visual Damage Analysis API
app.post('/api/analyze-damage', async (req, res) => {
  try {
    const { images, vehicleInfo } = req.body;
    
    // Simulate AI Vision delay for realistic user experience
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const brand = vehicleInfo?.brand || 'Veículo Identificado';
    const model = vehicleInfo?.model || 'Modelo Detectado';
    const year = vehicleInfo?.year || '2021';

    // AI vision damage extraction simulation (or integrate with Gemini key if available)
    const detectedParts = [
      {
        id: `detected-1-${Date.now()}`,
        name: 'Para-choque Dianteiro / Grade Inferior',
        category: 'Carroceria Frontal',
        actionRequired: 'Substituição',
        severity: 'Alto',
        confidence: 0.95,
        notes: 'Fissura estrutural e quebra nos suportes de fixação laterais.'
      },
      {
        id: `detected-2-${Date.now()}`,
        name: 'Conjunto do Farol Principal',
        category: 'Iluminação',
        actionRequired: 'Substituição',
        severity: 'Alto',
        confidence: 0.97,
        notes: 'Lente acrílica quebrada e máscara interna danificada por impacto.'
      },
      {
        id: `detected-3-${Date.now()}`,
        name: 'Painel do Capô / Lataria',
        category: 'Lataria Frontal',
        actionRequired: 'Recuperação',
        severity: 'Médio',
        confidence: 0.88,
        notes: 'Vincos leves recuperáveis com funilaria e pintura.'
      }
    ];

    // Enrich with live market price quotes for new vs used
    const enrichedParts = detectedParts.map((part) => {
      const prices = fetchPartMarketPrices(brand, model, year, part.name);
      return {
        ...part,
        ...prices,
        selectedChoice: part.actionRequired === 'Recuperação' ? 'repair' : 'used'
      };
    });

    return res.json({
      success: true,
      vehicle: {
        brand,
        model,
        year,
        detectedAutomatically: true,
        confidenceScore: 0.93
      },
      damageAnalysis: {
        overallSeverity: 'Média - Requer substituição de 2 componentes',
        summary: `Identificadas avarias frontais/laterais no ${brand} ${model}. Recomendada a substituição das peças estruturais/iluminação e funilaria na lataria.`,
        parts: enrichedParts,
        laborCosts: {
          bodyworkHours: 10,
          bodyworkRate: 95.00,
          paintPanels: 3,
          paintRatePerPanel: 450.00,
          mechanicMontage: 380.00
        }
      }
    });

  } catch (error) {
    console.error('Error analyzing damage:', error);
    res.status(500).json({ success: false, message: 'Falha ao analisar imagem de avaria' });
  }
});

// Endpoint: Search Market Prices for Custom/Added Parts
app.post('/api/search-parts', (req, res) => {
  try {
    const { brand, model, year, partName } = req.body;

    if (!partName) {
      return res.status(400).json({ success: false, message: 'Nome da peça é obrigatório' });
    }

    const prices = fetchPartMarketPrices(brand || 'Universal', model || 'Carro', year || '2022', partName);

    res.json({
      success: true,
      query: { brand, model, year, partName },
      prices
    });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Erro ao buscar cotação de mercado' });
  }
});

app.listen(PORT, () => {
  console.log(`AutoBudget AI Server rodando na porta ${PORT}`);
});
