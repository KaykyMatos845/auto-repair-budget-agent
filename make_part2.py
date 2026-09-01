p2_code = """
const { useState, useRef, useEffect } = React;

function fmt(v) {
  if (typeof v !== 'number' || isNaN(v)) return 'R$ 0,00';
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

const SAMPLES = [
  {
    id: 'onix-front', label: 'Chevrolet Onix 2021', sub: 'Batida traseira/lateral — Tampa e Para-choque', img: '/samples/onix_rear.jpg',
    vehicle: { brand:'Chevrolet', model:'Onix LTZ 1.0 Turbo', year:'2021', color:'Prata', plate:'ONX-2021', clientName:'Lucas Oliveira', fipeValue: 68500 },
    parts: [
      { id:'s1', name:'Farol Dianteiro Esquerdo', category:'Iluminação', actionRequired:'Substituição', severity:'Alto', confidence:0.98, notes:'Carcaça fraturada e lente quebrada.', box:[20,15,55,55], selectedChoice:'used', newPrice:{brandName:'Original GM Arteb',price:890,supplier:'Concessionária GM',link:'https://produto.mercadolivre.com.br/MLB-5501296624-farol-led-chevrolet-onix-2020-2021-2022-2023-2024-_JM'}, usedPrice:{brandName:'Seminova GM DETRAN',price:499,supplier:'CDV Desmanche Credenciado SP',link:'https://produto.mercadolivre.com.br/MLB-5405547970-farol-onix-2020-2021-2022-2023-2024-2025-direito-original-_JM'} },
      { id:'s2', name:'Para-choque Dianteiro com Grade', category:'Carroceria Frontal', actionRequired:'Substituição', severity:'Alto', confidence:0.95, notes:'Fissura estrutural e suportes quebrados.', box:[45,30,80,85], selectedChoice:'used', newPrice:{brandName:'Original GM sem Pintura',price:680,supplier:'GM Peças Online',link:'https://produto.mercadolivre.com.br/MLB-3610996841-parachoque-dianteiro-onix-premier-turbo-2020-2021-2022-2023-_JM'}, usedPrice:{brandName:'Seminova GM DETRAN',price:380,supplier:'Recuperadora Sucatas BR',link:'https://produto.mercadolivre.com.br/MLB-3482701449-parachoque-dianteiro-chevrolet-onix-2020-2021-2022-original-_JM'} },
      { id:'s3', name:'Capô Dianteiro (Desamassamento)', category:'Lataria', actionRequired:'Recuperação', severity:'Médio', confidence:0.88, notes:'Vinco na borda esquerda — recuperável com funilaria.', box:[10,25,45,75], selectedChoice:'repair', newPrice:{brandName:'Serviço Funilaria',price:0,supplier:'Oficina',link:'#'}, usedPrice:{brandName:'Serviço Funilaria',price:0,supplier:'Oficina',link:'#'} },
    ],
    labor: { bodyworkHours:7, bodyworkRate:95, paintPanels:2, paintRatePerPanel:480, mechanicMontage:350 }
  },
  {
    id: 'civic-front', label: 'Honda Civic Touring 2021', sub: 'Colisão frontal esquerda — farol LED e para-choque', img: '/samples/civic_front.jpg',
    vehicle: { brand:'Honda', model:'Civic Touring 1.5 Turbo', year:'2021', color:'Prata', plate:'BRA-2021', clientName:'Ricardo Silva', fipeValue: 128000 },
    parts: [
      { id:'c1', name:'Farol Dianteiro Esquerdo Full LED', category:'Iluminação', actionRequired:'Substituição', severity:'Alto', confidence:0.97, notes:'Lente acrílica e máscara interna destruídas.', box:[15,10,50,45], selectedChoice:'used', newPrice:{brandName:'Original Honda OEM',price:2850,supplier:'Concessionária Honda',link:'https://produto.mercadolivre.com.br/MLB-3388190019-farol-dianteiro-esquerdo-honda-civic-g10-full-led-2020-2021-_JM'}, usedPrice:{brandName:'Seminova Honda DETRAN',price:1250,supplier:'CDV Sucatas Autorizadas SP',link:'https://produto.mercadolivre.com.br/MLB-3518290112-farol-full-led-honda-civic-g10-2019-2020-2021-original-usado-_JM'} },
      { id:'c2', name:'Para-choque Dianteiro com Suportes', category:'Carroceria Frontal', actionRequired:'Substituição', severity:'Alto', confidence:0.93, notes:'Rachadura nos encaixes do paralama.', box:[40,20,85,90], selectedChoice:'used', newPrice:{brandName:'DTS Paralela 1ª Linha',price:750,supplier:'Distribuidora AutoLatina',link:'https://produto.mercadolivre.com.br/MLB-2109820012-parachoque-dianteiro-honda-civic-g10-2020-2021-original-_JM'}, usedPrice:{brandName:'Original Alinhada DETRAN',price:420,supplier:'Recuperadora AutoSul',link:'https://produto.mercadolivre.com.br/MLB-3418290912-parachoque-dianteiro-honda-civic-g10-2021-usado-original-_JM'} },
    ],
    labor: { bodyworkHours:10, bodyworkRate:95, paintPanels:3, paintRatePerPanel:480, mechanicMontage:380 }
  },
  {
    id: 'corolla-side', label: 'Toyota Corolla XEi 2020', sub: 'Impacto lateral direito — porta e retrovisor', img: '/samples/corolla_side.jpg',
    vehicle: { brand:'Toyota', model:'Corolla XEi 2.0 Flex', year:'2020', color:'Branco Pérola', plate:'TOY-2020', clientName:'Juliana Costa', fipeValue: 135000 },
    parts: [
      { id:'t1', name:'Retrovisor Elétrico Direito com Pisca', category:'Elétrica', actionRequired:'Substituição', severity:'Alto', confidence:0.98, notes:'Mecanismo de rebatimento destruído.', box:[25,65,55,90], selectedChoice:'used', newPrice:{brandName:'Original Toyota OEM',price:1350,supplier:'Concessionária Toyota',link:'https://produto.mercadolivre.com.br/MLB-3219080112-retrovisor-eletrico-toyota-corolla-2020-2021-2022-original-_JM'}, usedPrice:{brandName:'Seminova Toyota RS',price:650,supplier:'CDV Sucatas RS',link:'https://produto.mercadolivre.com.br/MLB-3489102911-retrovisor-direito-corolla-2020-2021-original-usado-_JM'} },
      { id:'t2', name:'Folha da Porta Dianteira Direita', category:'Lataria / Porta', actionRequired:'Substituição', severity:'Alto', confidence:0.91, notes:'Amassado profundo e dobradiças danificadas.', box:[30,15,80,70], selectedChoice:'used', newPrice:{brandName:'Original Toyota sem Pintura',price:1850,supplier:'Toyota Parts',link:'https://produto.mercadolivre.com.br/MLB-3318902811-porta-dianteira-direita-corolla-2020-2021-2022-original-_JM'}, usedPrice:{brandName:'Porta Completa Alinhada',price:890,supplier:'Mega Desmanche SP',link:'https://produto.mercadolivre.com.br/MLB-3590129811-porta-dianteira-direita-toyota-corolla-2020-2021-usada-_JM'} },
    ],
    labor: { bodyworkHours:8, bodyworkRate:95, paintPanels:2, paintRatePerPanel:480, mechanicMontage:350 }
  },
];
"""

with open("part2.py", "w", encoding="utf-8") as f:
    f.write('part2 = """' + p2_code + '"""')
print("Wrote part2")
