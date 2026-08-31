export const sampleCases = [
  {
    id: 'civic-front',
    title: 'Honda Civic Touring 1.5 Turbo (2021)',
    description: 'Colisão frontal com avaria em farol LED, para-choque e vincos do capô.',
    image: '/samples/civic_front.jpg',
    vehicle: {
      brand: 'Honda',
      model: 'Civic Touring 1.5 Turbo',
      year: '2021',
      color: 'Prata',
      plate: 'BRA-2021',
    },
    damageAnalysis: {
      overallSeverity: 'Média - Alta',
      summary: 'Impacto frontal no lado esquerdo. Necessita substituição do farol LED e para-choque dianteiro, além de funilaria/pintura no capô e paralama.',
      parts: [
        {
          id: 'part-1',
          name: 'Farol Dianteiro Esquerdo Full LED',
          category: 'Iluminação',
          actionRequired: 'Substituição',
          severity: 'Alto',
          confidence: 0.96,
          newPrice: {
            brandName: 'Original Honda OEM',
            price: 3450.00,
            type: 'Nova (Original)',
            supplier: 'Concessionária Honda / Mercado Livre Oficial',
            availability: 'Pronta entrega',
            link: 'https://lista.mercadolivre.com.br/farol-honda-civic-2021-led-novo'
          },
          usedPrice: {
            brandName: 'Seminova Original',
            price: 1680.00,
            type: 'Usada / Seminova (Desmanche Credenciado DETRAN)',
            supplier: 'Auto Peças & Desmanche Credenciado SP',
            availability: 'Em estoque com Nota Fiscal',
            link: 'https://lista.mercadolivre.com.br/farol-honda-civic-2021-usado-original'
          },
          selectedChoice: 'used' // 'new' or 'used'
        },
        {
          id: 'part-2',
          name: 'Para-choque Dianteiro com Furos para Sensor',
          category: 'Carroceria Frontal',
          actionRequired: 'Substituição',
          severity: 'Alto',
          confidence: 0.94,
          newPrice: {
            brandName: 'DTS / Paralela 1ª Linha',
            price: 890.00,
            type: 'Nova (Paralela)',
            supplier: 'Distribuidora AutoLatina',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/parachoque-dianteiro-civic-2021-novo'
          },
          usedPrice: {
            brandName: 'Original Recortada / Alinhada',
            price: 450.00,
            type: 'Usada (Desmanche Credenciado)',
            supplier: 'Recuperadora AutoSul',
            availability: 'Pronta entrega',
            link: 'https://lista.mercadolivre.com.br/parachoque-dianteiro-civic-2021-usado'
          },
          selectedChoice: 'used'
        },
        {
          id: 'part-3',
          name: 'Grade Dianteira Central com Moldura Cromada',
          category: 'Acabamento',
          actionRequired: 'Substituição',
          severity: 'Médio',
          confidence: 0.91,
          newPrice: {
            brandName: 'Original Honda',
            price: 780.00,
            type: 'Nova (Original)',
            supplier: 'Honda Peças Direto',
            availability: '2 dias úteis',
            link: 'https://lista.mercadolivre.com.br/grade-dianteira-civic-2021-nova'
          },
          usedPrice: {
            brandName: 'Original Seminova',
            price: 320.00,
            type: 'Usada (Desmanche Credenciado)',
            supplier: 'Leilão Peças BR',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/grade-dianteira-civic-2021-usada'
          },
          selectedChoice: 'used'
        },
        {
          id: 'part-4',
          name: 'Capô Dianteiro (Desamassamento & Funilaria)',
          category: 'Lataria',
          actionRequired: 'Recuperação',
          severity: 'Médio',
          confidence: 0.89,
          notes: 'Dano reparável com martelinho e pintura. Não requer peça nova.',
          newPrice: {
            brandName: 'Serviço de Funilaria',
            price: 0,
            type: 'N/A (Reparo da peça original)',
            supplier: 'Mão de Obra Oficina',
            availability: 'Imediato',
            link: '#'
          },
          usedPrice: {
            brandName: 'Serviço de Funilaria',
            price: 0,
            type: 'N/A (Reparo da peça original)',
            supplier: 'Mão de Obra Oficina',
            availability: 'Imediato',
            link: '#'
          },
          selectedChoice: 'repair'
        }
      ],
      laborCosts: {
        bodyworkHours: 12,
        bodyworkRate: 90.00, // R$ 1.080
        paintPanels: 3, // Para-choque, Capô, Paralama
        paintRatePerPanel: 450.00, // R$ 1.350
        mechanicMontage: 400.00
      }
    }
  },
  {
    id: 'corolla-side',
    title: 'Toyota Corolla XEi 2.0 (2020)',
    description: 'Impacto na lateral direita com avaria na porta dianteira e paralama.',
    image: '/samples/corolla_side.jpg',
    vehicle: {
      brand: 'Toyota',
      model: 'Corolla XEi 2.0 Flex',
      year: '2020',
      color: 'Branco Pérola',
      plate: 'TOY-2020',
    },
    damageAnalysis: {
      overallSeverity: 'Média',
      summary: 'Avaria concentrada na porta dianteira direita e paralama. Retrovisor externo destruído. Requer troca de retrovisor e porta, recuperação do paralama.',
      parts: [
        {
          id: 'part-c1',
          name: 'Retrovisor Elétrico Direito com Rebatimento e Pisca',
          category: 'Acessórios & Elétrica',
          actionRequired: 'Substituição',
          severity: 'Alto',
          confidence: 0.98,
          newPrice: {
            brandName: 'Original Toyota OEM',
            price: 1850.00,
            type: 'Nova (Original)',
            supplier: 'Concessionária Toyota',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/retrovisor-corolla-2020-novo-original'
          },
          usedPrice: {
            brandName: 'Seminova Original (Cor Branca)',
            price: 790.00,
            type: 'Usada / Seminova (Desmanche Credenciado)',
            supplier: 'CDV Sucatas RS',
            availability: 'Com nota fiscal e garantia 90 dias',
            link: 'https://lista.mercadolivre.com.br/retrovisor-corolla-2020-usado-original'
          },
          selectedChoice: 'used'
        },
        {
          id: 'part-c2',
          name: 'Folha de Porta Dianteira Direita',
          category: 'Lataria / Porta',
          actionRequired: 'Substituição',
          severity: 'Alto',
          confidence: 0.92,
          newPrice: {
            brandName: 'Original Toyota sem Pintura',
            price: 2400.00,
            type: 'Nova (Original)',
            supplier: 'Toyota Parts',
            availability: '3 dias úteis',
            link: 'https://lista.mercadolivre.com.br/porta-dianteira-corolla-2020-nova'
          },
          usedPrice: {
            brandName: 'Porta Completa Alinhada',
            price: 1100.00,
            type: 'Usada (Desmanche Credenciado)',
            supplier: 'Mega Desmanche SP',
            availability: 'Pronta entrega',
            link: 'https://lista.mercadolivre.com.br/porta-dianteira-corolla-2020-usada'
          },
          selectedChoice: 'used'
        },
        {
          id: 'part-c3',
          name: 'Paralama Dianteiro Direito',
          category: 'Lataria',
          actionRequired: 'Recuperação',
          severity: 'Médio',
          confidence: 0.88,
          newPrice: {
            brandName: 'Paralelo Importado',
            price: 480.00,
            type: 'Nova (Paralela)',
            supplier: 'Auto Latas',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/paralama-corolla-2020-novo'
          },
          usedPrice: {
            brandName: 'Original Usado sem amassado',
            price: 280.00,
            type: 'Usada (Desmanche Credenciado)',
            supplier: 'Eco Auto Peças',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/paralama-corolla-2020-usado'
          },
          selectedChoice: 'repair'
        }
      ],
      laborCosts: {
        bodyworkHours: 10,
        bodyworkRate: 90.00,
        paintPanels: 2,
        paintRatePerPanel: 480.00,
        mechanicMontage: 350.00
      }
    }
  },
  {
    id: 'onix-rear',
    title: 'Chevrolet Onix Premier 1.0 Turbo (2022)',
    description: 'Colisão traseira urbana com avaria na lanterna direita e tampa do porta-malas.',
    image: '/samples/onix_rear.jpg',
    vehicle: {
      brand: 'Chevrolet',
      model: 'Onix Hatch Premier 1.0 Turbo',
      year: '2022',
      color: 'Vermelho Carmin',
      plate: 'ONX-2022',
    },
    damageAnalysis: {
      overallSeverity: 'Leve - Média',
      summary: 'Impacto traseiro. Quebra da lanterna traseira direita e amassado na tampa do porta-malas e para-choque traseiro.',
      parts: [
        {
          id: 'part-o1',
          name: 'Lanterna Traseira Direita LED Premier',
          category: 'Iluminação Traseira',
          actionRequired: 'Substituição',
          severity: 'Alto',
          confidence: 0.99,
          newPrice: {
            brandName: 'Original GM Arteb',
            price: 980.00,
            type: 'Nova (Original)',
            supplier: 'Achevrolet Concessionária',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/lanterna-traseira-onix-premier-2022-nova'
          },
          usedPrice: {
            brandName: 'Original GM Seminova',
            price: 490.00,
            type: 'Usada / Seminova (Desmanche Credenciado)',
            supplier: 'Desmanche Autorizado GM',
            availability: 'Pronta entrega com garantia',
            link: 'https://lista.mercadolivre.com.br/lanterna-traseira-onix-premier-2022-usada'
          },
          selectedChoice: 'used'
        },
        {
          id: 'part-o2',
          name: 'Para-choque Traseiro Inferior com Defletor',
          category: 'Carroceria Traseira',
          actionRequired: 'Substituição',
          severity: 'Médio',
          confidence: 0.95,
          newPrice: {
            brandName: 'Original GM sem Pintura',
            price: 750.00,
            type: 'Nova (Original)',
            supplier: 'GM Peças Online',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/parachoque-traseiro-onix-2022-novo'
          },
          usedPrice: {
            brandName: 'Original Seminovo',
            price: 380.00,
            type: 'Usada (Desmanche Credenciado)',
            supplier: 'Sucatas do Brasil',
            availability: 'Em estoque',
            link: 'https://lista.mercadolivre.com.br/parachoque-traseiro-onix-2022-usado'
          },
          selectedChoice: 'used'
        },
        {
          id: 'part-o3',
          name: 'Tampa do Porta-malas Traseiro',
          category: 'Lataria Traseira',
          actionRequired: 'Recuperação',
          severity: 'Médio',
          confidence: 0.90,
          newPrice: {
            brandName: 'Original GM',
            price: 1890.00,
            type: 'Nova (Original)',
            supplier: 'Concessionária GM',
            availability: '4 dias úteis',
            link: '#'
          },
          usedPrice: {
            brandName: 'Serviço de Funilaria Martelinho',
            price: 0,
            type: 'N/A (Reparo da peça original)',
            supplier: 'Oficina Funilaria',
            availability: 'Imediato',
            link: '#'
          },
          selectedChoice: 'repair'
        }
      ],
      laborCosts: {
        bodyworkHours: 8,
        bodyworkRate: 85.00,
        paintPanels: 2,
        paintRatePerPanel: 420.00,
        mechanicMontage: 280.00
      }
    }
  }
];

export const commonVehicleBrands = [
  'Chevrolet', 'Volkswagen', 'Fiat', 'Hyundai', 'Toyota', 
  'Honda', 'Jeep', 'Renault', 'Nissan', 'Ford', 'BMW', 'Audi', 'Mercedes-Benz'
];
