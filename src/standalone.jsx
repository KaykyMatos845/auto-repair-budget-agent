import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

const LABOR_RATE = 80;
const OPS = [
  { id: 'fun', label: 'Funilaria', icon: '🔨' },
  { id: 'pin', label: 'Pintura', icon: '🎨' },
  { id: 'tap', label: 'Tapeçaria/Vid.', icon: '🪟' },
  { id: 'mec', label: 'Mecânica', icon: '⚙️' },
  { id: 'rec', label: 'Recuperação', icon: '🔄' }
];
const DEFAULT_OPS = { fun: 0, pin: 0, tap: 0, mec: 0, rec: 0 };

function fmt(v) {
  if (typeof v !== 'number' || isNaN(v)) return 'R$ 0,00';
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function partLaborTotal(ops) {
  return OPS.reduce((s, op) => s + (parseFloat((ops || {})[op.id]) || 0), 0) * LABOR_RATE;
}

function partLaborHours(ops) {
  return OPS.reduce((s, op) => s + (parseFloat((ops || {})[op.id]) || 0), 0);
}

function getBoxStyle(box) {
  if (!box || !Array.isArray(box) || box.length < 4) return null;
  let [y1, x1, y2, x2] = box;
  if (y1 > 100 || x1 > 100 || y2 > 100 || x2 > 100) {
    y1 /= 10; x1 /= 10; y2 /= 10; x2 /= 10;
  }
  const top = Math.max(0, Math.min(95, y1));
  const left = Math.max(0, Math.min(95, x1));
  const height = Math.max(4, Math.min(100 - top, y2 - y1));
  const width = Math.max(4, Math.min(100 - left, x2 - x1));
  return {
    top: top + '%',
    left: left + '%',
    width: width + '%',
    height: height + '%'
  };
}

const SAMPLES = [
  {
    id: 'onix',
    label: 'Chevrolet Onix 2021',
    sub: 'Sinistro Completo • Eixo Torto + Lanterna + Lataria',
    img: '/samples/onix_rear.jpg',
    vehicle: { brand: 'Chevrolet', model: 'Onix Hatch LTZ 1.0 Turbo', year: '2021', color: 'Prata', plate: 'ONX-2021', clientName: 'Lucas Oliveira', fipeValue: 0 },
    parts: [
      {
        id: 's1',
        name: 'Lanterna Traseira Esquerda (Lado Motorista)',
        category: 'Iluminação',
        actionRequired: 'Substituição',
        side: 'Esquerdo',
        position: 'Traseiro',
        notes: 'Lente acrílica e carcaça plástica quebradas no impacto. Substituição obrigatória.',
        box: [25, 68, 55, 92],
        selectedChoice: 'used',
        ops: { fun: 0, pin: 0.5, tap: 0, mec: 0.5, rec: 0 },
        newPrice: {
          brandName: 'Original GM Arteb (Lado Esquerdo)',
          price: 780,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/lanterna-traseira-onix-hatch-2020-2021-2022-esquerda-nova_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Esquerdo (Motorista) • Em Estoque • 100% Compatível Onix 2021'
        },
        usedPrice: {
          brandName: 'Seminova GM DETRAN (Lado Esquerdo)',
          price: 390,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/lanterna-traseira-onix-hatch-2020-2021-2022-esquerda-usada-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Esquerdo • Desmanche Credenciado DETRAN • Em Estoque'
        }
      },
      {
        id: 's2',
        name: 'Eixo Traseiro com Suspensão & Barra de Torção',
        category: 'Mecânica / Suspensão',
        actionRequired: 'Substituição',
        side: 'Central / Esquerdo',
        position: 'Traseiro',
        notes: 'Eixo traseiro empenado/torto com desvio grave de geometria e cambagem.',
        box: [60, 45, 90, 85],
        selectedChoice: 'used',
        ops: { fun: 0.5, pin: 0, tap: 0, mec: 3.5, rec: 0 },
        newPrice: {
          brandName: 'Eixo Traseiro Original GM Novo',
          price: 1750,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-onix-2020-2021-2022-2023-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Eixo Traseiro Completo • Em Estoque • 100% Compatível Onix'
        },
        usedPrice: {
          brandName: 'Eixo Traseiro Usado Certificado DETRAN',
          price: 820,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/eixo-traseiro-onix-2020-2021-2022-2023-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Eixo Traseiro com Laudo de Alinhamento • DETRAN'
        }
      },
      {
        id: 's3',
        name: 'Lateral Traseira Esquerda (Painel & Caixa de Roda)',
        category: 'Lataria / Carroceria',
        actionRequired: 'Recuperação',
        side: 'Esquerdo',
        position: 'Lateral Traseira',
        notes: 'Amassado estrutural profundo na folha lateral com repuxo e alinhamento do vinco.',
        box: [30, 20, 75, 80],
        selectedChoice: 'repair',
        ops: { fun: 5, pin: 4.5, tap: 1, mec: 0, rec: 0 },
        newPrice: { brandName: 'Serviço de Recuperação', price: 0, link: '#' },
        usedPrice: { brandName: 'Serviço de Recuperação', price: 0, link: '#' }
      },
      {
        id: 's4',
        name: 'Parabarro Traseiro Esquerdo (Protetor de Caixa de Roda)',
        category: 'Acabamento / Plásticos',
        actionRequired: 'Substituição',
        side: 'Esquerdo',
        position: 'Traseiro',
        notes: 'Protetor plástico rasgado e presilhas de fixação destruídas.',
        box: [45, 55, 78, 85],
        selectedChoice: 'used',
        ops: { fun: 0, pin: 0, tap: 0, mec: 0.5, rec: 0 },
        newPrice: {
          brandName: 'Parabarro Original GM Novo',
          price: 150,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-onix-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Esquerdo • Em Estoque • 100% Compatível'
        },
        usedPrice: {
          brandName: 'Parabarro Semiusado DETRAN',
          price: 80,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/parabarro-traseiro-onix-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Esquerdo • CDV DETRAN • Em Estoque'
        }
      },
      {
        id: 's5',
        name: 'Grade Extratora de Ar Traseira (Válvula de Respiro)',
        category: 'Acabamento / Plásticos',
        actionRequired: 'Substituição',
        side: 'Esquerdo',
        position: 'Traseiro',
        notes: 'Grade plástica com membranas de borracha esmagadas na deformação do painel.',
        box: [35, 30, 60, 65],
        selectedChoice: 'used',
        ops: { fun: 0, pin: 0, tap: 0, mec: 0.5, rec: 0 },
        newPrice: {
          brandName: 'Grade de Respiro Original GM',
          price: 120,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/grade-respiro-traseira-onix-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Extrator Traseiro • Em Estoque'
        },
        usedPrice: {
          brandName: 'Grade de Respiro Semiusada DETRAN',
          price: 60,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/grade-respiro-traseira-onix-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Extrator Traseiro • CDV DETRAN'
        }
      },
      {
        id: 's6',
        name: 'Para-choque Traseiro',
        category: 'Carroceria',
        actionRequired: 'Substituição',
        side: 'Central',
        position: 'Traseiro',
        notes: 'Travas laterais rompidas e fissura na capa plástica.',
        box: [65, 15, 92, 85],
        selectedChoice: 'used',
        ops: { fun: 0.5, pin: 2.0, tap: 0, mec: 0.5, rec: 0 },
        newPrice: {
          brandName: 'Original GM Traseiro',
          price: 680,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-traseiro-onix-hatch-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Posição Traseira • Em Estoque • 100% Compatível Onix 2021'
        },
        usedPrice: {
          brandName: 'Seminova DETRAN Traseiro',
          price: 380,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-traseiro-onix-hatch-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Posição Traseira • Desmanche Credenciado DETRAN • Em Estoque'
        }
      }
    ],
    thirdParty: [
      { id: 'tp1', name: 'Alinhamento Técnico de Chassi e Geometria 3D', value: 350 }
    ]
  },
  {
    id: 'civic',
    label: 'Honda Civic Touring 2021',
    sub: 'Colisão Frontal • Farol & Para-choque',
    img: '/samples/civic_front.jpg',
    vehicle: { brand: 'Honda', model: 'Civic Touring 1.5 Turbo', year: '2021', color: 'Prata', plate: 'BRA-2021', clientName: 'Ricardo Silva', fipeValue: 0 },
    parts: [
      {
        id: 'c1',
        name: 'Farol Dianteiro Esquerdo Full LED (Motorista)',
        category: 'Iluminação',
        actionRequired: 'Substituição',
        side: 'Esquerdo',
        position: 'Dianteiro',
        notes: 'Lente acrílica e máscara interna destruídas no impacto frontal esquerdo.',
        box: [35, 62, 60, 90],
        selectedChoice: 'used',
        ops: { fun: 0, pin: 0.5, tap: 0, mec: 1, rec: 0 },
        newPrice: {
          brandName: 'Original Honda OEM Full LED (Esquerdo)',
          price: 2850,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-esquerdo-honda-civic-g10-full-led-2020-2021-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Esquerdo (Motorista) • Em Estoque • 100% Compatível Civic G10'
        },
        usedPrice: {
          brandName: 'Seminova Honda DETRAN (Esquerdo)',
          price: 1250,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/farol-dianteiro-esquerdo-honda-civic-g10-full-led-2020-2021-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Esquerdo • Desmanche Credenciado DETRAN • Em Estoque'
        }
      },
      {
        id: 'c2',
        name: 'Para-choque Dianteiro',
        category: 'Carroceria',
        actionRequired: 'Substituição',
        side: 'Central',
        position: 'Dianteiro',
        notes: 'Rachadura nos encaixes do paralama dianteiro esquerdo.',
        box: [55, 20, 88, 85],
        selectedChoice: 'used',
        ops: { fun: 0.5, pin: 2, tap: 0, mec: 0, rec: 0 },
        newPrice: {
          brandName: 'DTS Paralela 1ª Linha Dianteiro',
          price: 750,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-dianteiro-honda-civic-g10-2020-2021-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Posição Dianteira • Em Estoque • 100% Compatível Civic G10'
        },
        usedPrice: {
          brandName: 'Original Alinhada DETRAN Dianteiro',
          price: 420,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/parachoque-dianteiro-honda-civic-g10-2020-2021-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Posição Dianteira • Desmanche Credenciado DETRAN • Em Estoque'
        }
      }
    ],
    thirdParty: [
      { id: 'tp2', name: 'Geometria e Alinhamento 3D', value: 220 }
    ]
  },
  {
    id: 'corolla',
    label: 'Toyota Corolla XEi 2020',
    sub: 'Impacto Lateral • Porta & Retrovisor',
    img: '/samples/corolla_side.jpg',
    vehicle: { brand: 'Toyota', model: 'Corolla XEi 2.0 Flex', year: '2020', color: 'Branco Pérola', plate: 'TOY-2020', clientName: 'Juliana Costa', fipeValue: 0 },
    parts: [
      {
        id: 't1',
        name: 'Retrovisor Elétrico Direito (Passageiro)',
        category: 'Elétrica / Carroceria',
        actionRequired: 'Substituição',
        side: 'Direito',
        position: 'Lateral',
        notes: 'Mecanismo de rebatimento destruído no impacto direito.',
        box: [28, 62, 48, 82],
        selectedChoice: 'used',
        ops: { fun: 0, pin: 0.5, tap: 0, mec: 1, rec: 0 },
        newPrice: {
          brandName: 'Original Toyota OEM (Lado Direito)',
          price: 1350,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-eletrico-direito-toyota-corolla-2020-2021-2022-novo_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Direito (Passageiro) • Em Estoque • 100% Compatível Corolla'
        },
        usedPrice: {
          brandName: 'Seminova Toyota RS (Lado Direito)',
          price: 650,
          link: 'https://lista.mercadolivre.com.br/pecas-carros/retrovisor-eletrico-direito-toyota-corolla-2020-2021-2022-usado-original_OrderId_PRICE_ASC_NoIndex_True',
          compatibility: 'Lado Direito • Desmanche Credenciado DETRAN • Em Estoque'
        }
      },
      {
        id: 't2',
        name: 'Porta Dianteira Direita (Passageiro)',
        category: 'Lataria / Porta',
        actionRequired: 'Recuperação',
        side: 'Direito',
        position: 'Lateral',
        notes: 'Amassado na folha externa e recuperação de dobradiça.',
        box: [40, 25, 82, 75],
        selectedChoice: 'repair',
        ops: { fun: 3, pin: 4, tap: 1, mec: 0.5, rec: 0 },
        newPrice: { brandName: 'Serviço de Recuperação', price: 0, link: '#' },
        usedPrice: { brandName: 'Serviço de Recuperação', price: 0, link: '#' }
      }
    ],
    thirdParty: []
  }
];

function App() {
  const [images, setImages] = useState([]);
  const [vehicle, setVehicle] = useState({ brand: '', model: '', year: '', plate: '', color: '', clientName: '', fipeValue: 0 });
  const [parts, setParts] = useState([]);
  const [thirdParty, setThirdParty] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [analysisError, setAnalysisError] = useState('');
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  useEffect(() => { setReviewConfirmed(false); }, [parts, vehicle, thirdParty, analysis, images]);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  const [apiKey, setApiKey] = useState(true);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [keyInput, setKeyInput] = useState(() => localStorage.getItem('autobudget_gemini_key') || '');
  const [showPdf, setShowPdf] = useState(false);
  const [showAddPart, setShowAddPart] = useState(false);
  const [newPart, setNewPart] = useState({
    name: '',
    category: 'Mecânica / Suspensão',
    actionRequired: 'Substituição',
    side: 'Esquerdo',
    notes: '',
    priceNew: '',
    priceUsed: '',
    ops: { fun: 0, pin: 0, tap: 0, mec: 1.0, rec: 0 }
  });
  const [activeTab, setActiveTab] = useState('budget');
  const [osStatus, setOsStatus] = useState('Em Vistoria');
  const [osList, setOsList] = useState(() => {
    try { return JSON.parse(localStorage.getItem('autobudget_os_list') || '[]'); } catch(e) { return []; }
  });
  const reviewComplete = !loading && !analysisError && parts.length > 0 &&
    parts.every(p => p.reviewed) && reviewConfirmed;
  const reviewLabel = analysis?.analysisMode === 'demo' ? 'DEMONSTRAÇÃO — dados simulados' :
    reviewComplete ? 'Estimativa revisada pelo usuário' : 'RASCUNHO — revisão pendente';
  const requireReview = () => {
    if (reviewComplete) return true;
    alert('Revise cada item, a decisão de reparo, as horas e os preços; depois confirme a revisão do orçamento.');
    return false;
  };
  const fileRef = useRef();

  useEffect(() => {
    const saved = localStorage.getItem('autobudget_gemini_key');
    fetch('/api/health')
      .then(r => r.json())
      .then(d => {
        setApiKey(Boolean(d.geminiKeyConfigured || saved));
      })
      .catch(() => {
        setApiKey(Boolean(saved));
      });
  }, []);

  const handleSaveKey = async () => {
    const k = (keyInput || '').trim();
    if (!k) {
      alert('Por favor digite ou cole sua chave do Gemini.');
      return;
    }
    localStorage.setItem('autobudget_gemini_key', k);
    setApiKey(true);
    setShowKeyModal(false);
    alert('✅ Chave Gemini AI configurada e salva com sucesso!');
  };

  const setVField = (field, value) => {
    setVehicle(prev => ({ ...prev, [field]: value }));
  };

  const newInspection = () => {
    setAnalysisError('');
    setImages([]);
    setVehicle({ brand: '', model: '', year: '', plate: '', color: '', clientName: '', fipeValue: 0 });
    setParts([]);
    setThirdParty([]);
    setAnalysis(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const setPartOp = (partId, opId, val) => {
    const num = Math.max(0, parseFloat(val) || 0);
    setParts(prev => prev.map(p => {
      if (p.id !== partId) return p;
      return { ...p, reviewed: false, ops: { ...(p.ops || DEFAULT_OPS), [opId]: num } };
    }));
  };

  const stepPartOp = (partId, opId, delta) => {
    setParts(prev => prev.map(p => {
      if (p.id !== partId) return p;
      const current = parseFloat((p.ops || {})[opId]) || 0;
      const next = Math.max(0, parseFloat((current + delta).toFixed(1)));
      return { ...p, reviewed: false, ops: { ...(p.ops || DEFAULT_OPS), [opId]: next } };
    }));
  };

  const toggleChoice = (partId, choice) => {
    setParts(prev => prev.map(p => {
      if (p.id !== partId) return p;
      return { ...p, reviewed: false, selectedChoice: p.selectedChoice === choice ? 'repair' : choice };
    }));
  };

  const removePart = (partId) => {
    setParts(prev => prev.filter(p => p.id !== partId));
  };

  const saveManualPart = () => {
    if (!newPart.name.trim()) {
      alert('Por favor informe o nome da peça.');
      return;
    }

    const pNew = parseFloat(newPart.priceNew) || 0;
    const pUsed = parseFloat(newPart.priceUsed) || (pNew > 0 ? Math.round(pNew * 0.5) : 0);
    const slug = (newPart.name + ' ' + (vehicle.brand || '') + ' ' + (vehicle.model || '') + ' ' + (vehicle.year || '')).toLowerCase().replace(/\s+/g, '-');
    const isRepair = newPart.actionRequired === 'Recuperação' || newPart.actionRequired === 'Pintura';

    const item = {
      id: 'p-man-' + Date.now().toString().slice(-6),
      name: newPart.name.trim(),
      category: newPart.category,
      actionRequired: newPart.actionRequired,
      side: newPart.side,
      position: 'Manual',
      notes: newPart.notes || 'Adicionado manualmente pelo perito.',
      box: null,
      reviewed: false,
      selectedChoice: isRepair ? 'repair' : (pUsed > 0 ? 'used' : 'new'),
      ops: { ...newPart.ops },
      newPrice: {
        brandName: (vehicle.brand || 'Veículo') + ' Original OEM',
        price: pNew,
        link: 'https://lista.mercadolivre.com.br/pecas-carros/' + slug + '-novo_OrderId_PRICE_ASC_NoIndex_True',
        compatibility: 'Lado ' + newPart.side + ' • Valor informado manualmente'
      },
      usedPrice: {
        brandName: 'Peça usada — procedência a confirmar',
        price: pUsed,
        link: 'https://lista.mercadolivre.com.br/pecas-carros/' + slug + '-usado-original_OrderId_PRICE_ASC_NoIndex_True',
        compatibility: 'Lado ' + newPart.side + ' • Desmanche Credenciado DETRAN'
      }
    };

    setParts(prev => [...prev, item]);
    setShowAddPart(false);
    setNewPart({
      name: '',
      category: 'Mecânica / Suspensão',
      actionRequired: 'Substituição',
      side: 'Esquerdo',
      notes: '',
      priceNew: '',
      priceUsed: '',
      ops: { fun: 0, pin: 0, tap: 0, mec: 1.0, rec: 0 }
    });
  };

  const addThirdParty = () => {
    setThirdParty(prev => [...prev, { id: 'tp' + Date.now(), name: '', value: 0 }]);
  };
  const removeThirdParty = (id) => {
    setThirdParty(prev => prev.filter(t => t.id !== id));
  };
  const setTPField = (id, field, val) => {
    setThirdParty(prev => prev.map(t => {
      if (t.id !== id) return t;
      return { ...t, [field]: field === 'value' ? (Math.max(0, parseFloat(val) || 0)) : val };
    }));
  };

  const totalLaborParts = parts.reduce((sum, p) => sum + partLaborTotal(p.ops || DEFAULT_OPS), 0);
  const totalThirdPartyVal = thirdParty.reduce((sum, t) => sum + (parseFloat(t.value) || 0), 0);
  const totalLabor = totalLaborParts + totalThirdPartyVal;

  let totNew = 0;
  let totSelected = 0;
  parts.forEach(p => {
    totNew += p.newPrice ? (p.newPrice.price || 0) : 0;
    const sp = p.selectedChoice === 'new' ? (p.newPrice ? p.newPrice.price || 0 : 0) :
               p.selectedChoice === 'used' ? (p.usedPrice ? p.usedPrice.price || 0 : 0) : 0;
    totSelected += sp;
  });

  const budgetNew = totNew + totalLabor;
  const budgetSel = totSelected + totalLabor;
  const saving = Math.max(0, budgetNew - budgetSel);
  const savingPct = budgetNew > 0 ? ((saving / budgetNew) * 100).toFixed(1) : '0.0';
  
  const fipeVal = parseFloat(vehicle.fipeValue) || 0;
  const fipePct = fipeVal > 0 ? ((budgetSel / fipeVal) * 100).toFixed(1) : '0.0';
  const isTotalLoss = fipeVal > 0 && parseFloat(fipePct) >= 75.0;

  const processFiles = async (files) => {
    const selected = Array.from(files);
    if (!selected.length) return;
    if (selected.length > 4 || selected.some(f => !['image/jpeg', 'image/png', 'image/webp'].includes(f.type) || f.size > 8 * 1024 * 1024)) {
      setAnalysisError('Selecione de 1 a 4 fotos JPEG, PNG ou WebP, com até 8 MB cada.');
      return;
    }
    setAnalysisError('');
    setParts([]);
    setAnalysis(null);
    const imgs = [];
    for (const f of selected) {
      const blobUrl = URL.createObjectURL(f);
      const b64 = await new Promise(resolve => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result.split(',')[1]);
        reader.readAsDataURL(f);
      });
      imgs.push({ blobUrl, base64: b64, name: f.name });
    }
    setImages(imgs);
  };

  const analyze = async () => {
    if (!images.length) return;
    setAnalysisError('');
    setLoading(true);
    setLoadingMsg('Inspecionando lataria, mecânica/suspensão e iluminação com IA...');
    try {
      const savedKey = localStorage.getItem('autobudget_gemini_key') || keyInput || '';
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          images: images.map(i => i.base64), 
          vehicle,
          apiKey: savedKey 
        })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || 'A IA não concluiu a análise. Tente novamente.');
      if (data.error) throw new Error(data.error);

      // AUTO-FILL VEHICLE DATA IDENTIFIED BY AI
      if (data.vehicle) {
        setVehicle(prev => ({
          ...prev,
          brand: data.vehicle.brand && data.vehicle.brand !== 'Veículo Identificado' ? data.vehicle.brand : (prev.brand || data.vehicle.brand || ''),
          model: data.vehicle.model && data.vehicle.model !== 'Modelo Identificado' ? data.vehicle.model : (prev.model || data.vehicle.model || ''),
          year: data.vehicle.year && data.vehicle.year !== 'N/A' ? data.vehicle.year : (prev.year || data.vehicle.year || ''),
          color: data.vehicle.color && data.vehicle.color !== 'N/A' ? data.vehicle.color : (prev.color || data.vehicle.color || ''),
          fipeValue: prev.fipeValue || 0
        }));
      }

      const rawParts = data.parts || (data.damageAnalysis && data.damageAnalysis.parts) || [];
      const enriched = rawParts.map((p, i) => ({
        ...p,
        id: p.id || ('p' + Date.now().toString().slice(-6) + i),
        ops: { ...DEFAULT_OPS },
        reviewed: false,
        selectedChoice: p.selectedChoice || 'repair'
      }));
      setParts(enriched);
      setThirdParty([]);
      setAnalysis(data);
    } catch(e) {
      setAnalysisError(e.message);
    } finally {
      setLoading(false);
      setLoadingMsg('');
    }
  };

  const loadSample = (s) => {
    setAnalysisError('');
    setImages([{ blobUrl: s.img, base64: '', name: 'sample.jpg' }]);
    setVehicle({ ...s.vehicle });
    setParts(s.parts.map(p => ({ ...p, reviewed: false, ops: p.ops || { ...DEFAULT_OPS } })));
    setThirdParty(s.thirdParty || []);
    setAnalysis({ aiPowered: false, analysisMode: 'demo' });
  };

  const saveOS = () => {
    if (!requireReview()) return;
    const newOs = {
      id: 'OS-' + Date.now().toString().slice(-6),
      date: new Date().toLocaleDateString('pt-BR'),
      vehicle: (vehicle.brand || 'Veículo') + ' ' + (vehicle.model || ''),
      plate: vehicle.plate || 'N/I',
      client: vehicle.clientName || 'Cliente',
      total: budgetSel,
      fipePct: fipeVal > 0 ? fipePct : 'N/A',
      isTotalLoss: isTotalLoss,
      analysisMode: analysis?.analysisMode || 'manual',
      reviewStatus: reviewLabel,
      status: osStatus
    };
    const updated = [newOs, ...osList].slice(0, 50);
    setOsList(updated);
    localStorage.setItem('autobudget_os_list', JSON.stringify(updated));
    alert('✅ Ordem de Serviço ' + newOs.id + ' salva com sucesso!');
  };

  const shareWhatsApp = () => {
    if (!requireReview()) return;
    const pList = parts.map((p, i) => {
      const v = p.selectedChoice === 'new' ? (p.newPrice ? p.newPrice.price : 0) :
                p.selectedChoice === 'used' ? (p.usedPrice ? p.usedPrice.price : 0) : 0;
      const opsDetail = OPS.filter(op => parseFloat((p.ops || {})[op.id]) > 0)
        .map(op => op.label + ': ' + p.ops[op.id] + 'h').join(', ');
      return (i + 1) + '. ' + p.name + ' (' + p.actionRequired + ') — ' + fmt(v) + (opsDetail ? ' | MO: ' + opsDetail : '');
    }).join('\n');

    const tpList = thirdParty.filter(t => t.name)
      .map(t => '  • ' + t.name + ': ' + fmt(t.value)).join('\n');

    const lines = [
      '🏎️ *ORÇAMENTO DE REPAROS AUTOMOTIVOS*',
      reviewLabel,
      'Preços estimados; confirmar cotação. Fotos não confirmam danos internos.',
      '📅 Data: ' + new Date().toLocaleDateString('pt-BR'),
      '🚗 Veículo: ' + (vehicle.brand || '') + ' ' + (vehicle.model || '') + ' (' + (vehicle.year || '') + ')',
      '🏷️ Placa: ' + (vehicle.plate || 'N/I') + ' | Cliente: ' + (vehicle.clientName || 'Cliente'),
      (fipeVal > 0 ? '📊 FIPE: ' + fmt(fipeVal) + ' | Comprometimento: ' + fipePct + '% ' + (isTotalLoss ? '🚨 RISCO PERDA TOTAL' : '') : '📊 FIPE: Não informada'),
      '',
      '📋 *PEÇAS & COMPONENTES:*',
      pList,
      '',
      '🔧 *MÃO DE OBRA (Taxa linear R$ 80,00/h):*',
      '  Subtotal Operações: ' + fmt(totalLaborParts),
      (tpList ? '\n🔗 *SERVIÇOS DE TERCEIROS:*\n' + tpList + '\n  Subtotal: ' + fmt(totalThirdPartyVal) : ''),
      '',
      '💰 *TOTAL GERAL: ' + fmt(budgetSel) + '*',
      '🎉 Economia estimada: ' + fmt(saving) + ' (' + savingPct + '% OFF)',
      '',
      'Status: ' + osStatus,
      '_AutoBudget AI v3.0 — Vistoria Computacional_'
    ].filter(l => l !== undefined);

    const msg = lines.join('\n');
    window.open('https://wa.me/?text=' + encodeURIComponent(msg), '_blank');
  };

  return (
    <div className="wrap">
      
      {/* HEADER */}
      <header className="glass-panel" style={{ padding: '18px 24px', marginBottom: 22, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: 'linear-gradient(135deg, #fbbf24 0%, #d97706 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem', boxShadow: '0 4px 16px rgba(245, 158, 11, 0.3)' }}>🏎️</div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ background: 'linear-gradient(135deg, #fbbf24, #f43f5e, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AutoBudget AI</span>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: 4 }}>v3.0 PRO</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
              Vistoria Computacional • Mão de Obra R$ 80,00/h fixo • FIPE Integrada • Peças Mercado Livre
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-ghost" onClick={newInspection} title="Limpar tudo e iniciar novo orçamento" style={{ borderColor: 'rgba(245,158,11,0.4)', color: 'var(--gold-light)' }}>
            🔄 Nova Vistoria
          </button>
          <button className="btn btn-ghost" onClick={() => setActiveTab(activeTab === 'history' ? 'budget' : 'history')}>
            📋 Histórico ({osList.length})
          </button>
          <a href="/slides.html" target="_blank" rel="noopener noreferrer" className="btn btn-ghost" style={{ textDecoration: 'none', borderColor: 'rgba(6,182,212,0.4)', color: '#38bdf8' }} title="Abrir slides de apresentação do projeto">
            📊 Slides
          </a>
          {apiKey === false && (
            <button 
              className="badge" 
              onClick={() => setShowKeyModal(true)}
              style={{ 
                cursor: 'pointer',
                background: 'rgba(244,63,94,0.18)', 
                color: 'var(--rose-light)', 
                border: '1px solid rgba(244,63,94,0.4)',
                padding: '6px 12px',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6
              }}
              title="Clique para configurar sua chave da API do Gemini">
              ⚠️ Sem API Key • Inserir Chave
            </button>
          )}
          {apiKey === true && (
            <button 
              className="badge badge-ai" 
              onClick={() => setShowKeyModal(true)}
              style={{ 
                cursor: 'pointer',
                padding: '6px 12px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6
              }}
              title="Clique para gerenciar ou alterar a chave do Gemini">
              ✨ Gemini AI Ativo • ⚙️ Chave
            </button>
          )}
        </div>
      </header>

      {/* FIPE & BUDGET SUMMARY BAR (Top persistent) */}
      {parts.length > 0 && (
        <div className={'fipe-card' + (isTotalLoss ? ' total-loss' : '')}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', gap: 20, alignItems: 'center', flexWrap: 'wrap' }}>
              <div>
                <label className="form-label" style={{ color: 'var(--gold-light)' }}>VALOR TABELA FIPE (MANUAL)</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ color: 'var(--text-muted)', fontWeight: 700, fontSize: '0.9rem' }}>R$</span>
                  <input
                    type="number"
                    className="form-inp"
                    placeholder="0,00 (Manual)"
                    value={vehicle.fipeValue ? vehicle.fipeValue : ''}
                    onChange={e => setVField('fipeValue', Math.max(0, parseFloat(e.target.value) || 0))}
                    style={{ width: 140, fontWeight: 800, fontSize: '1.05rem', color: '#fff', padding: '6px 12px' }}
                  />
                </div>
              </div>

              <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 20 }}>
                <div className="form-label">Peças Selecionadas</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>{fmt(totSelected)}</div>
              </div>

              <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 20 }}>
                <div className="form-label">M.O. + Terceiros</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--violet-light)' }}>{fmt(totalLabor)}</div>
              </div>

              <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 20 }}>
                <div className="form-label">Total Orçamento</div>
                <div style={{ fontSize: '1.45rem', fontWeight: 900, color: 'var(--gold-light)' }}>{fmt(budgetSel)}</div>
              </div>

              <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 20 }}>
                <div className="form-label">% da FIPE</div>
                <div style={{ fontSize: '1.45rem', fontWeight: 900, color: isTotalLoss ? 'var(--rose-light)' : (fipeVal > 0 ? 'var(--emerald-light)' : 'var(--text-dim)') }}>
                  {fipeVal > 0 ? (fipePct + '%') : '—'}
                </div>
              </div>
            </div>

            {isTotalLoss && (
              <div style={{ background: 'rgba(244,63,94,0.18)', border: '1px solid var(--rose)', borderRadius: 'var(--radius-sm)', padding: '8px 16px', color: 'var(--rose-light)', fontWeight: 800, fontSize: '0.84rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>🚨</span> ALERTA DE PERDA TOTAL (Atinge {'>'} 75% da FIPE)
              </div>
            )}
            
            {fipeVal === 0 && (
              <div style={{ color: 'var(--text-dim)', fontSize: '0.78rem', background: 'rgba(255,255,255,0.03)', padding: '6px 12px', borderRadius: 'var(--radius-sm)', border: '1px dashed var(--border)' }}>
                💡 Digite o valor da FIPE ao lado para calcular o % de perda total
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB: OS HISTORY */}
      {activeTab === 'history' && (
        <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 800 }}>📋 Histórico de Ordens de Serviço</h2>
            <button className="btn btn-ghost" onClick={() => setActiveTab('budget')}>← Voltar ao Orçamento</button>
          </div>
          {osList.length === 0 ? (
            <p style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 40 }}>Nenhuma OS salva ainda.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="tbl-custom">
                <thead>
                  <tr>
                    <th>Nº OS</th>
                    <th>Data</th>
                    <th>Veículo</th>
                    <th>Placa</th>
                    <th>Cliente</th>
                    <th>Total</th>
                    <th>% FIPE</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {osList.map(os => (
                    <tr key={os.id}>
                      <td style={{ fontWeight: 800, color: 'var(--gold-light)' }}>{os.id}</td>
                      <td>{os.date}</td>
                      <td>{os.vehicle}<div>{os.reviewStatus || 'Registro anterior — origem não verificada'}</div></td>
                      <td><code style={{ background: 'rgba(255,255,255,0.06)', padding: '2px 6px', borderRadius: 4 }}>{os.plate}</code></td>
                      <td>{os.client || '—'}</td>
                      <td style={{ fontWeight: 800 }}>{fmt(os.total)}</td>
                      <td style={{ fontWeight: 800, color: parseFloat(os.fipePct) >= 75 ? 'var(--rose-light)' : 'var(--emerald-light)' }}>
                        {os.fipePct !== 'N/A' ? (os.fipePct + '%') : '—'}
                      </td>
                      <td><span className="badge badge-repair">{os.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB: MAIN BUDGET VIEW */}
      {activeTab === 'budget' && (
        <div>

          {/* 1. SAMPLES PRESETS */}
          <div className="glass-panel" style={{ padding: '18px 22px', marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                ⚡ Carregar Vistoria Rápida de Exemplo
              </div>
              <button className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: '0.72rem' }} onClick={newInspection}>
                🔄 Limpar Campos
              </button>
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {SAMPLES.map(s => (
                <button
                  key={s.id}
                  className="btn btn-ghost"
                  onClick={() => loadSample(s)}
                  style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '10px 16px', gap: 2 }}
                >
                  <span style={{ fontWeight: 800, fontSize: '0.88rem', color: 'var(--text-main)' }}>{s.label}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{s.sub}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 2. PHOTOS UPLOAD & BOUNDING BOXES */}
          <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: 20 }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 12 }}>
              📷 Fotos da Avaria / Vistoria Computacional
            </div>
            
            <div
              className="upload-box"
              onClick={() => fileRef.current.click()}
              onDragOver={e => e.preventDefault()}
              onDrop={e => { e.preventDefault(); processFiles(e.dataTransfer.files); }}
            >
              <div style={{ fontSize: '2.2rem', marginBottom: 6 }}>📸</div>
              <div style={{ fontWeight: 800, fontSize: '0.95rem', marginBottom: 4 }}>Selecione até 4 fotos: visão geral, lados e detalhes dos danos</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Formatos: JPG, PNG, WEBP (A IA identifica automaticamente o veículo e as avarias)</div>
              <input ref={fileRef} type="file" multiple accept="image/*" style={{ display: 'none' }} onChange={e => processFiles(e.target.files)} />
            </div>

            {images.length > 0 && (
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 18 }}>
                {images.map((img, idx) => (
                  <div key={idx} className="img-box-container" style={{ position: 'relative', width: '100%', maxWidth: 540, borderRadius: 10, overflow: 'hidden', border: '1px solid var(--border-accent)', background: '#000' }}>
                    <img src={img.blobUrl} style={{ width: '100%', height: 'auto', display: 'block' }} alt={'Foto ' + (idx + 1)} />
                    {parts.map((p, pi) => {
                      const boxStyle = getBoxStyle(p.box);
                      if (!boxStyle || (analysis?.aiPowered && p.imageIndex !== idx)) return null;
                      return (
                        <div key={p.id} className="bbox-overlay" style={boxStyle} title={p.name + ': ' + p.notes}>
                          <span className="bbox-label">#{pi + 1} {p.name.split(' ')[0]}</span>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 3. VEHICLE DATA (Auto-filled by AI) */}
          <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <div>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  🚗 Dados do Veículo & Cliente (Preenchidos pela IA ou Manual)
                </div>
                <p style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>A IA detecta automaticamente Marca, Modelo, Ano e Cor a partir das fotos</p>
              </div>
              <button className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: '0.72rem' }} onClick={newInspection}>
                🔄 Nova Vistoria
              </button>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
              {[
                ['brand', 'Marca', 'Detectada por IA ou digite'],
                ['model', 'Modelo', 'Detectado por IA ou digite'],
                ['year', 'Ano', 'Ex: 2021'],
                ['plate', 'Placa', 'Ex: ABC-1234'],
                ['color', 'Cor', 'Ex: Prata'],
                ['clientName', 'Cliente', 'Nome do proprietário']
              ].map(([key, label, placeholder]) => (
                <div key={key}>
                  <label className="form-label">{label}</label>
                  <input
                    className="form-inp"
                    placeholder={placeholder}
                    value={vehicle[key] || ''}
                    onChange={e => setVField(key, e.target.value)}
                  />
                </div>
              ))}
              
              <div>
                <label className="form-label" style={{ color: 'var(--gold-light)' }}>Valor FIPE (R$)</label>
                <input
                  type="number"
                  className="form-inp"
                  placeholder="0,00 (Manual)"
                  value={vehicle.fipeValue ? vehicle.fipeValue : ''}
                  onChange={e => setVField('fipeValue', Math.max(0, parseFloat(e.target.value) || 0))}
                  style={{ fontWeight: 800, color: 'var(--gold-light)' }}
                />
              </div>
            </div>

            <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
              <button
                className="btn btn-gold"
                disabled={!images.length || loading || images.some(img => !img.base64)}
                onClick={analyze}
              >
                {loading ? (loadingMsg || 'Analisando com IA...') : '🤖 Analisar Avarias com Gemini AI'}
              </button>
              {analysis && (
                <span className="badge badge-ai">
                  {analysis.analysisMode === 'demo' ? 'DEMONSTRAÇÃO — dados simulados' : 'Análise visual preliminar — requer revisão'}
                </span>
              )}
            </div>
          </div>

          {analysisError && <div role="alert" className="glass-panel" style={{ padding: 18, color: '#fda4af' }}>
            Análise não concluída: {analysisError} Os itens anteriores, se houver, não são resultado desta tentativa.
          </div>}
          <section className="glass-panel" style={{ padding: 18, marginBottom: 20 }} aria-label="Revisão da análise">
            <strong>{reviewLabel}</strong>
            <p>Fotografe com boa luz e foco, incluindo visão geral e detalhes. Fotos não confirmam danos internos nem segurança para circulação.</p>
            <p>Preços são referências por regras locais, sem estoque ou compatibilidade verificados. Confirme cotações, decisão de reparo e horas de serviço.</p>
            {analysis?.damageAnalysis?.summary && <p>{analysis.damageAnalysis.summary}</p>}
            {analysis?.imageQuality?.issues?.map((issue, i) => <p key={'q'+i}>Qualidade: {issue}</p>)}
            {analysis?.limitations?.map((item, i) => <p key={'l'+i}>Limitação: {item}</p>)}
            {analysis?.analysisMode === 'insufficient_images' && <p role="alert">Envie novas fotos com melhor iluminação, foco e ângulos. Nenhum dano foi confirmado.</p>}
            {analysis?.analysisMode === 'visual' && parts.length === 0 && <p>Nenhum dano visível foi identificado. Isso não comprova ausência de danos.</p>}
            <label><input type="checkbox" checked={reviewConfirmed}
              disabled={!parts.length || !parts.every(p => p.reviewed) || !!analysisError || loading}
              onChange={e => setReviewConfirmed(e.target.checked)} /> Revisei todos os itens, as horas, os preços e os dados do veículo.</label>
          </section>
          {/* 4. PARTS & LABOR BREAKDOWN */}
          <div className="glass-panel" style={{ padding: '22px 24px', marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span>⚙️</span> Peças Avariadas & Operações de Mão de Obra
                  <span style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: 4, color: 'var(--text-dim)' }}>
                    {parts.length} item(ns)
                  </span>
                </h2>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  Taxa fixa de mão de obra linear: <strong style={{ color: 'var(--gold-light)' }}>R$ 80,00/hora</strong> • Mecânica, Iluminação, Lataria e Plásticos
                </p>
              </div>

              <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                <button
                  className="btn btn-gold"
                  style={{ padding: '7px 16px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: 6 }}
                  onClick={() => setShowAddPart(true)}
                >
                  <span>➕</span> Adicionar Peça / Item Manual
                </button>
                {parts.length > 0 && (
                  <div style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid var(--border-accent)', borderRadius: 'var(--radius-sm)', padding: '6px 14px', fontSize: '0.82rem', fontWeight: 700, color: 'var(--gold-light)' }}>
                    Total M.O. Peças: {fmt(totalLaborParts)}
                  </div>
                )}
              </div>
            </div>

            {parts.length === 0 && (
              <div style={{ textAlign: 'center', padding: '36px 20px', color: 'var(--text-dim)', border: '1px dashed var(--border)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '2rem', marginBottom: 8 }}>📋</div>
                <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--text-muted)', marginBottom: 4 }}>Nenhuma peça adicionada ainda</div>
                <div style={{ fontSize: '0.8rem', marginBottom: 14 }}>Carregue um exemplo acima, analise fotos com a IA ou adicione peças manualmente.</div>
                <button className="btn btn-gold" onClick={() => setShowAddPart(true)}>
                  ➕ Adicionar Primeira Peça Manual
                </button>
              </div>
            )}

            {parts.map((part, pIndex) => {
              const ops = part.ops || DEFAULT_OPS;
              const totalH = partLaborHours(ops);
              const totalMO = partLaborTotal(ops);
              const selPrice = part.selectedChoice === 'new' ? (part.newPrice ? part.newPrice.price || 0 : 0) :
                               part.selectedChoice === 'used' ? (part.usedPrice ? part.usedPrice.price || 0 : 0) : 0;
              const isRepair = part.actionRequired === 'Recuperação' || part.selectedChoice === 'repair';
              const totalItemCost = totalMO + selPrice;

              return (
                <div key={part.id} className="part-card">
                  
                  {/* Header: Part name + category + action badge + delete button */}
                  <div className="part-header">
                    <div>
                      <div className="part-title" style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                        <span>#{pIndex + 1} {part.name}</span>
                        <span className="part-category">• {part.category}</span>
                        <span className={'badge badge-' + (isRepair ? 'repair' : 'replace')}>
                          {part.actionRequired}
                        </span>
                      </div>
                      {part.notes && <div className="part-notes">{part.evidence ? 'Evidência: ' : ''}{part.notes}</div>}
                      {part.evidence && <p>Foto {part.imageIndex + 1} • Achado visual, sem diagnóstico de danos internos.</p>}
                      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                        {['newPrice', 'usedPrice'].map(priceKey => <label key={priceKey}>
                          {priceKey === 'newPrice' ? 'Cotação nova (R$)' : 'Cotação usada (R$)'}
                          <input type="number" min="0" step="0.01" value={part[priceKey]?.price || 0}
                            aria-label={(priceKey === 'newPrice' ? 'Preço nova: ' : 'Preço usada: ') + part.name}
                            onChange={e => setParts(prev => prev.map(p => p.id === part.id ? {
                              ...p, reviewed: false, priceSource: 'user_entered',
                              [priceKey]: { ...p[priceKey], price: Math.max(0, Number(e.target.value) || 0) }
                            } : p))} />
                        </label>)}
                      </div>
                      <label>Decisão após revisão: <select aria-label={'Decisão para ' + part.name}
                        value={part.actionRequired}
                        onChange={e => setParts(prev => prev.map(p => p.id === part.id ? { ...p, actionRequired: e.target.value, reviewed: false } : p))}>
                        {['Avaliação presencial', 'Substituição', 'Recuperação', 'Pintura', 'Alinhamento'].map(action => <option key={action}>{action}</option>)}
                      </select></label>
                      <label style={{ display: 'block' }}><input type="checkbox" checked={!!part.reviewed}
                        onChange={e => setParts(prev => prev.map(p => p.id === part.id ? { ...p, reviewed: e.target.checked } : p))} /> Revisei a evidência, a decisão, os valores e as horas deste item</label>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                      <div className="part-summary-pill">
                        <div>
                          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Mão de Obra</div>
                          <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--violet-light)' }}>{fmt(totalMO)}</div>
                          <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>{totalH.toFixed(1)}h</div>
                        </div>
                        {selPrice > 0 && (
                          <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 12 }}>
                            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Peça</div>
                            <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)' }}>{fmt(selPrice)}</div>
                          </div>
                        )}
                        <div style={{ borderLeft: '1px solid var(--border)', paddingLeft: 12 }}>
                          <div style={{ fontSize: '0.68rem', color: 'var(--gold-light)', textTransform: 'uppercase', fontWeight: 700 }}>Total Item</div>
                          <div style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--gold-light)' }}>{fmt(totalItemCost)}</div>
                        </div>
                      </div>

                      <button
                        className="btn btn-ghost"
                        style={{ padding: '6px 10px', color: 'var(--rose-light)', borderColor: 'rgba(244,63,94,0.3)', fontSize: '0.78rem' }}
                        title="Excluir esta peça do orçamento"
                        onClick={() => removePart(part.id)}
                      >
                        🗑️ Excluir
                      </button>
                    </div>
                  </div>

                  {/* Operations Stepper Grid */}
                  <div className="ops-section-title">
                    <span>Horas por Especialidade (R$ 80,00/h):</span>
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.72rem' }}>Ajuste com + / − ou digite direto</span>
                  </div>

                  <div className="ops-grid">
                    {OPS.map(op => {
                      const h = parseFloat(ops[op.id]) || 0;
                      const cost = h * LABOR_RATE;
                      const hasHours = h > 0;

                      return (
                        <div key={op.id} className={'op-cell' + (hasHours ? ' has-hours' : '')}>
                          <div className="op-header">
                            <span>{op.icon}</span>
                            <span>{op.label}</span>
                          </div>

                          <div className="op-stepper">
                            <button
                              className="op-btn"
                              title="Diminuir 0.5h"
                              onClick={() => stepPartOp(part.id, op.id, -0.5)}
                            >−</button>
                            
                            <input
                              type="number"
                              step="0.5"
                              min="0"
                              className="op-num-input"
                              value={ops[op.id] !== undefined ? ops[op.id] : 0}
                              onChange={e => setPartOp(part.id, op.id, e.target.value)}
                            />
                            <span className="op-unit">h</span>

                            <button
                              className="op-btn"
                              title="Aumentar 0.5h"
                              onClick={() => stepPartOp(part.id, op.id, 0.5)}
                            >+</button>
                          </div>

                          <div className={'op-subtotal' + (hasHours ? ' active' : ' zero')}>
                            {hasHours ? fmt(cost) : 'R$ 0,00'}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Part replacement choices: Nova OEM vs Usada DETRAN */}
                  {part.newPrice && part.newPrice.price > 0 && (
                    <div className="pricing-grid">
                      
                      {/* Nova OEM */}
                      <div
                        className={'price-option-card' + (part.selectedChoice === 'new' ? ' selected-new' : '')}
                        onClick={() => toggleChoice(part.id, 'new')}
                      >
                        <div className="price-option-header">
                          <span className="badge badge-new">🟣 Nova Genuína OEM</span>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 700 }}>
                            {part.selectedChoice === 'new' ? '✓ Selecionada' : 'Selecionar'}
                          </span>
                        </div>
                        <div className="price-val">{fmt(part.newPrice.price)}</div>
                        <div className="price-brand">{part.newPrice.brandName}</div>
                        
                        {/* Validation Badge */}
                        <div style={{ marginTop: 6, display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: '0.72rem', color: 'var(--emerald-light)', background: 'rgba(16,185,129,0.08)', padding: '2px 8px', borderRadius: 4, border: '1px solid rgba(16,185,129,0.25)' }}>
                          <span>🛡️</span>
                          <span>{part.newPrice.compatibility || 'Compatibilidade e estoque não verificados'}</span>
                        </div>

                        {part.newPrice.link && part.newPrice.link !== '#' && (
                          <a
                            href={part.newPrice.link}
                            target="_blank"
                            className="ml-link"
                            style={{ color: 'var(--violet-light)' }}
                            onClick={e => e.stopPropagation()}
                          >
                            🛒 Ver Peça Disponível no Mercado Livre ↗
                          </a>
                        )}
                      </div>

                      {/* Usada DETRAN */}
                      <div
                        className={'price-option-card' + (part.selectedChoice === 'used' ? ' selected-used' : '')}
                        onClick={() => toggleChoice(part.id, 'used')}
                      >
                        <div className="price-option-header">
                          <span className="badge badge-used">Usada — confirmar procedência</span>
                          {part.newPrice.price > part.usedPrice.price && (
                            <span style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--emerald-light)', background: 'rgba(16,185,129,0.15)', padding: '2px 6px', borderRadius: 4 }}>
                              −{(((part.newPrice.price - part.usedPrice.price) / part.newPrice.price) * 100).toFixed(0)}% OFF
                            </span>
                          )}
                        </div>
                        <div className="price-val" style={{ color: 'var(--emerald-light)' }}>
                          {fmt(part.usedPrice ? part.usedPrice.price : 0)}
                        </div>
                        <div className="price-brand">{part.usedPrice ? part.usedPrice.brandName : 'Desmanche Credenciado'}</div>
                        
                        {/* Validation Badge */}
                        <div style={{ marginTop: 6, display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: '0.72rem', color: 'var(--emerald-light)', background: 'rgba(16,185,129,0.08)', padding: '2px 8px', borderRadius: 4, border: '1px solid rgba(16,185,129,0.25)' }}>
                          <span>🛡️</span>
                          <span>{part.usedPrice.compatibility || 'Compatibilidade e estoque não verificados'}</span>
                        </div>

                        {part.usedPrice && part.usedPrice.link && part.usedPrice.link !== '#' && (
                          <a
                            href={part.usedPrice.link}
                            target="_blank"
                            className="ml-link"
                            style={{ color: 'var(--emerald-light)' }}
                            onClick={e => e.stopPropagation()}
                          >
                            🛒 Ver Peça Disponível no Mercado Livre ↗
                          </a>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Notice if recovery */}
                  {isRepair && (!part.newPrice || part.newPrice.price === 0) && (
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.82rem', padding: '10px 14px', background: 'rgba(245,158,11,0.04)', borderRadius: 'var(--radius-sm)', border: '1px dashed var(--border-accent)', marginTop: 8 }}>
                      🔧 <strong>Serviço de Recuperação</strong> — Sem necessidade de aquisição de peça de reposição.
                    </div>
                  )}

                </div>
              );
            })}
          </div>

          {/* MODAL: ADD MANUAL PART */}
          {showAddPart && (
            <div
              style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}
              onClick={() => setShowAddPart(false)}
            >
              <div
                style={{ background: '#111827', color: '#fff', borderRadius: 14, padding: '28px 32px', maxWidth: 640, width: '100%', maxHeight: '90vh', overflowY: 'auto', border: '1px solid var(--border-accent)', boxShadow: '0 20px 50px rgba(0,0,0,0.7)' }}
                onClick={e => e.stopPropagation()}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 900, color: 'var(--gold-light)', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span>➕</span> Adicionar Peça / Item Manual ao Orçamento
                  </h3>
                  <button
                    onClick={() => setShowAddPart(false)}
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}
                  >✕</button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  <div>
                    <label className="form-label">NOME DA PEÇA / COMPONENTE *</label>
                    <input
                      className="form-inp"
                      placeholder="Ex: Eixo Traseiro, Lanterna Traseira Esquerda, Parabarro..."
                      value={newPart.name}
                      onChange={e => setNewPart({ ...newPart, name: e.target.value })}
                      style={{ fontSize: '0.95rem' }}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label className="form-label">CATEGORIA</label>
                      <select
                        className="form-inp"
                        value={newPart.category}
                        onChange={e => setNewPart({ ...newPart, category: e.target.value })}
                      >
                        <option value="Mecânica / Suspensão">⚙️ Mecânica / Suspensão</option>
                        <option value="Iluminação">💡 Iluminação</option>
                        <option value="Lataria / Carroceria">🚗 Lataria / Carroceria</option>
                        <option value="Acabamento / Plásticos">🛡️ Acabamento / Plásticos</option>
                        <option value="Vidros">🪟 Vidros</option>
                        <option value="Elétrica">⚡ Elétrica</option>
                      </select>
                    </div>

                    <div>
                      <label className="form-label">TIPO DE AÇÃO REQUERIDA</label>
                      <select
                        className="form-inp"
                        value={newPart.actionRequired}
                        onChange={e => setNewPart({ ...newPart, actionRequired: e.target.value })}
                      >
                        <option value="Substituição">Substituição (Troca de Peça)</option>
                        <option value="Recuperação">Recuperação (Reparo / Desempeno)</option>
                        <option value="Pintura">Apenas Pintura</option>
                        <option value="Alinhamento">Alinhamento / Geometria</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label className="form-label">LADO / POSIÇÃO</label>
                      <select
                        className="form-inp"
                        value={newPart.side}
                        onChange={e => setNewPart({ ...newPart, side: e.target.value })}
                      >
                        <option value="Esquerdo">Esquerdo (Motorista)</option>
                        <option value="Direito">Direito (Passageiro)</option>
                        <option value="Central">Central / Traseiro / Dianteiro</option>
                      </select>
                    </div>

                    <div>
                      <label className="form-label">PREÇO ESTIMADO NOVA OEM (R$)</label>
                      <input
                        type="number"
                        className="form-inp"
                        placeholder="Ex: 850,00"
                        value={newPart.priceNew}
                        onChange={e => setNewPart({ ...newPart, priceNew: e.target.value })}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="form-label">PREÇO ESTIMADO USADA DETRAN (R$ - Opcional)</label>
                    <input
                      type="number"
                      className="form-inp"
                      placeholder="Deixe em branco para 50% da nova"
                      value={newPart.priceUsed}
                      onChange={e => setNewPart({ ...newPart, priceUsed: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">OBSERVAÇÕES TÉCNICAS DO DANO</label>
                    <input
                      className="form-inp"
                      placeholder="Ex: Eixo empenado no impacto / Lente quebrada..."
                      value={newPart.notes}
                      onChange={e => setNewPart({ ...newPart, notes: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">HORAS INICIAIS DE MÃO DE OBRA (R$ 80,00/h)</label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8, marginTop: 4 }}>
                      {OPS.map(op => (
                        <div key={op.id} style={{ background: 'rgba(255,255,255,0.04)', padding: 8, borderRadius: 6, textAlign: 'center' }}>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{op.label}</div>
                          <input
                            type="number"
                            step="0.5"
                            min="0"
                            className="form-inp"
                            style={{ textAlign: 'center', marginTop: 4, padding: '4px 6px', fontSize: '0.85rem' }}
                            value={newPart.ops[op.id] || 0}
                            onChange={e => setNewPart({
                              ...newPart,
                              ops: { ...newPart.ops, [op.id]: Math.max(0, parseFloat(e.target.value) || 0) }
                            })}
                          />
                        </div>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                    <button className="btn btn-ghost" onClick={() => setShowAddPart(false)}>Cancelar</button>
                    <button className="btn btn-gold" onClick={saveManualPart}>💾 Salvar Peça no Orçamento</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5. THIRD PARTY SERVICES */}
          {parts.length > 0 && (
            <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                <div>
                  <h2 style={{ fontSize: '1rem', fontWeight: 800 }}>🔗 Serviços de Terceiros</h2>
                  <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>Alinhamento 3D, tapeçaria especializada, solda especial ou parceiros externos</p>
                </div>
                <button className="btn btn-ghost" style={{ padding: '6px 14px', fontSize: '0.78rem' }} onClick={addThirdParty}>
                  + Adicionar Serviço
                </button>
              </div>

              {thirdParty.length === 0 ? (
                <div style={{ color: 'var(--text-dim)', fontSize: '0.84rem', textAlign: 'center', padding: '18px 0', border: '1px dashed var(--border)', borderRadius: 'var(--radius-sm)' }}>
                  Nenhum serviço de terceiros adicionado. Clique em <strong>+ Adicionar Serviço</strong> caso necessário.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {thirdParty.map(tp => (
                    <div key={tp.id} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                      <input
                        className="form-inp"
                        placeholder="Descrição do serviço (ex: Alinhamento de chassi, Geometria...)"
                        value={tp.name}
                        style={{ flex: 3 }}
                        onChange={e => setTPField(tp.id, 'name', e.target.value)}
                      />
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, minWidth: 120 }}>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', fontWeight: 700 }}>R$</span>
                        <input
                          type="number"
                          className="form-inp"
                          placeholder="0,00"
                          value={tp.value || ''}
                          onChange={e => setTPField(tp.id, 'value', e.target.value)}
                          style={{ fontWeight: 800, color: 'var(--text-main)' }}
                        />
                      </div>
                      <button
                        className="btn btn-ghost"
                        style={{ padding: '9px 12px', color: 'var(--rose-light)', borderColor: 'rgba(244,63,94,0.3)' }}
                        title="Remover serviço"
                        onClick={() => removeThirdParty(tp.id)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                  <div style={{ textAlign: 'right', fontWeight: 800, color: 'var(--violet-light)', fontSize: '0.9rem', marginTop: 4 }}>
                    Subtotal Terceiros: {fmt(totalThirdPartyVal)}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 6. LABOR SUMMARY TABLE */}
          {parts.length > 0 && (
            <div className="glass-panel" style={{ padding: '22px 24px', marginBottom: 20 }}>
              <div style={{ marginBottom: 16 }}>
                <h2 style={{ fontSize: '1rem', fontWeight: 800 }}>📊 Matriz de Mão de Obra por Especialidade</h2>
                <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>Demonstrativo consolidado de horas e valores por peça (R$ 80,00/h)</p>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table className="tbl-custom">
                  <thead>
                    <tr>
                      <th>Item / Peça</th>
                      <th>🔨 Funilaria</th>
                      <th>🎨 Pintura</th>
                      <th>🪟 Tapeç./Vid.</th>
                      <th>⚙️ Mecânica</th>
                      <th>🔄 Recuperação</th>
                      <th style={{ color: 'var(--violet-light)', textAlign: 'right' }}>Total M.O.</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parts.map(p => {
                      const ops = p.ops || DEFAULT_OPS;
                      const total = partLaborTotal(ops);
                      return (
                        <tr key={p.id}>
                          <td style={{ fontWeight: 700 }}>{p.name}</td>
                          {OPS.map(op => {
                            const h = parseFloat(ops[op.id]) || 0;
                            return (
                              <td key={op.id} style={{ color: h > 0 ? 'var(--text-main)' : 'var(--text-dim)' }}>
                                {h > 0 ? (
                                  <span>
                                    <strong>{h}h</strong> <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>({fmt(h * LABOR_RATE)})</span>
                                  </span>
                                ) : '—'}
                              </td>
                            );
                          })}
                          <td style={{ fontWeight: 800, color: 'var(--violet-light)', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                            {fmt(total)}
                          </td>
                        </tr>
                      );
                    })}

                    <tr style={{ borderTop: '2px solid var(--border)', background: 'rgba(255,255,255,0.02)' }}>
                      <td style={{ fontWeight: 800 }}>SUBTOTAL OPERAÇÕES</td>
                      {OPS.map(op => {
                        const colH = parts.reduce((s, p) => s + (parseFloat((p.ops || {})[op.id]) || 0), 0);
                        const colTotal = colH * LABOR_RATE;
                        return (
                          <td key={op.id} style={{ fontWeight: 800, color: colTotal > 0 ? 'var(--gold-light)' : 'var(--text-dim)' }}>
                            {colTotal > 0 ? (colH + 'h (' + fmt(colTotal) + ')') : '—'}
                          </td>
                        );
                      })}
                      <td style={{ fontWeight: 900, color: 'var(--violet-light)', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                        {fmt(totalLaborParts)}
                      </td>
                    </tr>

                    {totalThirdPartyVal > 0 && (
                      <tr>
                        <td style={{ fontWeight: 700, color: 'var(--rose-light)' }}>Serviços de Terceiros</td>
                        <td colSpan={5} style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                          {thirdParty.filter(t => t.name).map(t => t.name + ': ' + fmt(t.value)).join(' • ')}
                        </td>
                        <td style={{ fontWeight: 800, color: 'var(--rose-light)', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                          {fmt(totalThirdPartyVal)}
                        </td>
                      </tr>
                    )}

                    <tr style={{ borderTop: '2px solid var(--gold)', background: 'rgba(245,158,11,0.06)' }}>
                      <td colSpan={6} style={{ fontWeight: 900, fontSize: '0.95rem' }}>TOTAL CONSOLIDADO MÃO DE OBRA + TERCEIROS</td>
                      <td style={{ fontWeight: 900, fontSize: '1.15rem', color: 'var(--gold-light)', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                        {fmt(totalLabor)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 7. FINAL BUDGET CARD */}
          {parts.length > 0 && (
            <div className="glass-panel" id="pdf-area" style={{ padding: '26px 28px', marginBottom: 28, border: '2px solid var(--gold)', boxShadow: 'var(--shadow-glow)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span>💰</span> Resumo Executivo do Orçamento Final
                  </h2>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Veículo: {(vehicle.brand || 'Veículo')} {(vehicle.model || '')} {(vehicle.year ? '(' + vehicle.year + ')' : '')} • Placa: {vehicle.plate || 'N/I'} • Cliente: {vehicle.clientName || 'Cliente'}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <span className="badge" style={{ background: isTotalLoss ? 'rgba(244,63,94,0.2)' : (fipeVal > 0 ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.08)'), color: isTotalLoss ? 'var(--rose-light)' : (fipeVal > 0 ? 'var(--emerald-light)' : 'var(--text-dim)'), border: '1px solid ' + (isTotalLoss ? 'var(--rose)' : (fipeVal > 0 ? 'var(--emerald)' : 'var(--border)')) }}>
                    {isTotalLoss ? '🚨 RISCO PERDA TOTAL' : (fipeVal > 0 ? '✅ REPARO VIÁVEL' : '📋 FIPE NÃO INFORMADA')}
                  </span>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 14, marginBottom: 22 }}>
                <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', padding: '14px 16px', border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Peças Escolhidas</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 900, color: 'var(--text-main)', marginTop: 4 }}>{fmt(totSelected)}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: 2 }}>Nova OEM Total: {fmt(totNew)}</div>
                </div>

                <div style={{ background: 'var(--violet-glow)', borderRadius: 'var(--radius-sm)', padding: '14px 16px', border: '1px solid rgba(139,92,246,0.3)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--violet-light)', fontWeight: 700, textTransform: 'uppercase' }}>Mão de Obra Total</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 900, color: 'var(--violet-light)', marginTop: 4 }}>{fmt(totalLaborParts)}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>Taxa R$ 80,00/h fixo</div>
                </div>

                {totalThirdPartyVal > 0 && (
                  <div style={{ background: 'var(--rose-glow)', borderRadius: 'var(--radius-sm)', padding: '14px 16px', border: '1px solid rgba(244,63,94,0.3)' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--rose-light)', fontWeight: 700, textTransform: 'uppercase' }}>Terceiros</div>
                    <div style={{ fontSize: '1.35rem', fontWeight: 900, color: 'var(--rose-light)', marginTop: 4 }}>{fmt(totalThirdPartyVal)}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>{thirdParty.filter(t => t.name).length} serviço(s)</div>
                  </div>
                )}

                <div style={{ background: 'var(--gold-glow)', borderRadius: 'var(--radius-sm)', padding: '14px 16px', border: '2px solid var(--gold)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--gold-light)', fontWeight: 700, textTransform: 'uppercase' }}>TOTAL FINAL</div>
                  <div style={{ fontSize: '1.65rem', fontWeight: 900, color: 'var(--gold-light)', marginTop: 4 }}>{fmt(budgetSel)}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--emerald-light)', fontWeight: 700, marginTop: 2 }}>
                    Economia: {fmt(saving)} ({savingPct}%)
                  </div>
                </div>

                <div style={{ background: isTotalLoss ? 'var(--rose-glow)' : (fipeVal > 0 ? 'var(--emerald-glow)' : 'rgba(255,255,255,0.02)'), borderRadius: 'var(--radius-sm)', padding: '14px 16px', border: '1px solid ' + (isTotalLoss ? 'rgba(244,63,94,0.4)' : (fipeVal > 0 ? 'rgba(16,185,129,0.4)' : 'var(--border)')) }}>
                  <div style={{ fontSize: '0.72rem', color: isTotalLoss ? 'var(--rose-light)' : (fipeVal > 0 ? 'var(--emerald-light)' : 'var(--text-dim)'), fontWeight: 700, textTransform: 'uppercase' }}>% Tabela FIPE</div>
                  <div style={{ fontSize: '1.65rem', fontWeight: 900, color: isTotalLoss ? 'var(--rose-light)' : (fipeVal > 0 ? 'var(--emerald-light)' : 'var(--text-dim)'), marginTop: 4 }}>
                    {fipeVal > 0 ? (fipePct + '%') : '—'}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
                    {fipeVal > 0 ? ('FIPE: ' + fmt(fipeVal)) : 'FIPE: Não informada'}
                  </div>
                </div>
              </div>

              {isTotalLoss && (
                <div style={{ background: 'rgba(244,63,94,0.14)', border: '1px solid rgba(244,63,94,0.5)', borderRadius: 'var(--radius-sm)', padding: '14px 18px', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 14 }}>
                  <span style={{ fontSize: '1.8rem' }}>🚨</span>
                  <div>
                    <div style={{ fontWeight: 800, color: 'var(--rose-light)' }}>ALERTA DE PERDA TOTAL DETECTADA</div>
                    <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      O custo acumulado de reparos ({fmt(budgetSel)}) atinge <strong>{fipePct}%</strong> da Tabela FIPE ({fmt(fipeVal)}). Em casos acima de 75%, as seguradoras tipicamente indenizam integralmente o veículo.
                    </div>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                <button className="btn btn-whatsapp" onClick={shareWhatsApp}>
                  💬 Enviar Orçamento no WhatsApp
                </button>
                <button className="btn btn-gold" onClick={() => { if (requireReview()) setShowPdf(true); }}>
                  📄 Imprimir / Exportar PDF
                </button>
                
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                  <select
                    value={osStatus}
                    onChange={e => setOsStatus(e.target.value)}
                    className="form-inp"
                    style={{ width: 'auto', padding: '9px 14px' }}
                  >
                    {['Em Vistoria', 'Aguardando Peças', 'Em Execução', 'Concluído', 'Cancelado'].map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <button className="btn btn-emerald" onClick={saveOS}>
                    💾 Salvar OS
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

      {/* PDF PRINT MODAL */}
      {showPdf && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}
          onClick={() => setShowPdf(false)}
        >
          <div
            style={{ background: '#fff', color: '#111', borderRadius: 14, padding: '32px 36px', maxWidth: 840, width: '100%', maxHeight: '90vh', overflowY: 'auto' }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div>
                <h2 style={{ fontFamily: "'Outfit', sans-serif", color: '#0f172a', fontSize: '1.3rem', fontWeight: 900 }}>
                  AutoBudget AI — Estimativa de Reparos
                </h2>
                <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{reviewLabel} • Valores estimados, sujeitos a cotação e inspeção presencial</p>
              </div>
              <button
                onClick={() => { if (requireReview()) window.print(); }}
                style={{ background: '#f59e0b', color: '#000', border: 'none', padding: '9px 18px', borderRadius: 8, cursor: 'pointer', fontWeight: 800 }}
              >
                🖨️ Imprimir Laudo
              </button>
            </div>

            <div style={{ background: '#f8fafc', padding: 14, borderRadius: 8, marginBottom: 18, fontSize: '0.86rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <div><strong>Veículo:</strong> {(vehicle.brand || 'Veículo')} {(vehicle.model || '')} {(vehicle.year ? '(' + vehicle.year + ')' : '')}</div>
              <div><strong>Placa:</strong> {vehicle.plate || 'N/I'} • <strong>Cor:</strong> {vehicle.color || 'N/I'}</div>
              <div><strong>Cliente:</strong> {vehicle.clientName || 'N/I'}</div>
              <div><strong>Data:</strong> {new Date().toLocaleDateString('pt-BR')}</div>
              <div><strong>Valor FIPE:</strong> {fipeVal > 0 ? fmt(fipeVal) : 'Não informada'}</div>
              <div><strong>Comprometimento:</strong> {fipeVal > 0 ? (fipePct + '%') : '—'} {isTotalLoss ? '(🚨 RISCO PERDA TOTAL)' : ''}</div>
            </div>

            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: 10, color: '#0f172a' }}>Demonstrativo por Peça e Especialidade:</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', marginBottom: 18 }}>
              <thead>
                <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #cbd5e1' }}>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Item</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Funilaria</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Pintura</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Tapeç./Vid.</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Mecânica</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Recup.</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>M.O. Total</th>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Peça</th>
                  <th style={{ padding: '8px 10px', textAlign: 'right' }}>Total Item</th>
                </tr>
              </thead>
              <tbody>
                {parts.map(p => {
                  const ops = p.ops || DEFAULT_OPS;
                  const mo = partLaborTotal(ops);
                  const pc = p.selectedChoice === 'new' ? (p.newPrice ? p.newPrice.price || 0 : 0) :
                             p.selectedChoice === 'used' ? (p.usedPrice ? p.usedPrice.price || 0 : 0) : 0;
                  return (
                    <tr key={p.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '8px 10px', fontWeight: 700 }}>{p.name}</td>
                      {OPS.map(op => {
                        const h = parseFloat(ops[op.id]) || 0;
                        return (
                          <td key={op.id} style={{ padding: '8px 10px', color: h > 0 ? '#0f172a' : '#94a3b8' }}>
                            {h > 0 ? (h + 'h') : '—'}
                          </td>
                        );
                      })}
                      <td style={{ padding: '8px 10px', fontWeight: 700, color: '#7c3aed' }}>{fmt(mo)}</td>
                      <td style={{ padding: '8px 10px' }}>{pc > 0 ? fmt(pc) : '—'}</td>
                      <td style={{ padding: '8px 10px', fontWeight: 900, textAlign: 'right' }}>{fmt(mo + pc)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {thirdParty.filter(t => t.name).length > 0 && (
              <div style={{ marginBottom: 18 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: 8, color: '#0f172a' }}>Serviços de Terceiros:</h3>
                {thirdParty.filter(t => t.name).map(t => (
                  <div key={t.id} style={{ fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid #f1f5f9' }}>
                    <span>{t.name}</span>
                    <strong style={{ color: '#dc2626' }}>{fmt(t.value)}</strong>
                  </div>
                ))}
              </div>
            )}

            <div style={{ background: '#fef3c7', borderRadius: 8, padding: '16px 20px', border: '1px solid #fde68a' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 14 }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: '#92400e', fontWeight: 700 }}>PEÇAS</div>
                  <div style={{ fontWeight: 900, fontSize: '1.1rem', color: '#0f172a' }}>{fmt(totSelected)}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: '#92400e', fontWeight: 700 }}>MÃO DE OBRA</div>
                  <div style={{ fontWeight: 900, fontSize: '1.1rem', color: '#7c3aed' }}>{fmt(totalLaborParts)}</div>
                </div>
                {totalThirdPartyVal > 0 && (
                  <div>
                    <div style={{ fontSize: '0.72rem', color: '#92400e', fontWeight: 700 }}>TERCEIROS</div>
                    <div style={{ fontWeight: 900, fontSize: '1.1rem', color: '#dc2626' }}>{fmt(totalThirdPartyVal)}</div>
                  </div>
                )}
                <div>
                  <div style={{ fontSize: '0.72rem', color: '#92400e', fontWeight: 700 }}>TOTAL GERAL</div>
                  <div style={{ fontWeight: 900, fontSize: '1.3rem', color: '#d97706' }}>{fmt(budgetSel)}</div>
                </div>
              </div>
            </div>

            <p style={{ marginTop: 16, fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center' }}>
              Mão de Obra tabelada: R$ 80,00/hora em todas as operações • AutoBudget AI v3.0
            </p>

            <button
              onClick={() => setShowPdf(false)}
              className="no-print"
              style={{ marginTop: 14, background: '#f1f5f9', border: 'none', padding: '8px 20px', borderRadius: 8, cursor: 'pointer', fontWeight: 700 }}
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {/* MODAL CONFIGURAÇÃO DE CHAVE GEMINI */}
      {showKeyModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.85)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 99999,
          padding: 20
        }}>
          <div style={{
            background: 'var(--surface, #1e293b)',
            border: '1px solid rgba(245,158,11,0.3)',
            borderRadius: 16,
            maxWidth: 540,
            width: '100%',
            padding: 24,
            boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
            color: 'var(--text, #f8fafc)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 8 }}>
                🔑 Configuração da Chave Google Gemini AI
              </h3>
              <button 
                onClick={() => setShowKeyModal(false)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1.4rem', cursor: 'pointer' }}>
                ✕
              </button>
            </div>

            <p style={{ fontSize: '0.88rem', color: '#94a3b8', lineHeight: 1.5, marginBottom: 16 }}>
              A chave do Gemini é utilizada para o <strong>agente pericial automatizado</strong> (visão computacional, identificação do modelo do veículo e mapeamento de avarias).
            </p>

            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#fbbf24', marginBottom: 6 }}>
                SUA CHAVE API GEMINI
              </label>
              <input
                type="text"
                value={keyInput}
                onChange={e => setKeyInput(e.target.value)}
                placeholder="Cole sua chave aqui (ex: AQ.Ab8... ou AIza...)"
                style={{
                  width: '100%',
                  background: 'rgba(15,23,42,0.8)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: 8,
                  padding: '12px 14px',
                  color: '#fff',
                  fontSize: '0.9rem',
                  fontFamily: 'monospace'
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                onClick={() => setShowKeyModal(false)}
                className="btn btn-ghost"
                style={{ padding: '8px 16px', borderRadius: 8, cursor: 'pointer' }}>
                Cancelar
              </button>
              <button
                onClick={handleSaveKey}
                className="btn btn-primary"
                style={{
                  background: 'linear-gradient(135deg, #fbbf24, #d97706)',
                  color: '#0f172a',
                  fontWeight: 800,
                  border: 'none',
                  padding: '8px 20px',
                  borderRadius: 8,
                  cursor: 'pointer'
                }}>
                💾 Salvar e Ativar IA
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
