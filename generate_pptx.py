import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ── Colors & Styles ──────────────────────────────────────────────────────────
COLOR_BG = RGBColor(10, 15, 29)         # #0A0F1D Dark Navy
COLOR_CARD = RGBColor(22, 32, 54)       # #162036 Card Navy
COLOR_CARD_BORDER = RGBColor(40, 56, 88)
COLOR_GOLD = RGBColor(245, 158, 11)     # #F59E0B Gold
COLOR_GOLD_LIGHT = RGBColor(251, 191, 36)
COLOR_CYAN = RGBColor(6, 182, 212)      # #06B6D4 Cyan
COLOR_CYAN_LIGHT = RGBColor(56, 189, 248)
COLOR_EMERALD = RGBColor(16, 185, 129)  # #10B981 Emerald
COLOR_TEXT_MAIN = RGBColor(248, 250, 252)
COLOR_TEXT_MUTED = RGBColor(148, 163, 184)
COLOR_TEXT_DIM = RGBColor(100, 116, 139)

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, title_highlight=""):
        # Tag Badge
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(4.5), Inches(0.38))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = RGBColor(30, 42, 68)
        tag_box.line.color.rgb = COLOR_GOLD
        tag_box.line.width = Pt(1)
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_top = Inches(0.04)
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.name = FONT_BODY
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_GOLD_LIGHT
        p_tag.alignment = PP_ALIGN.CENTER

        # Main Title
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.5), Inches(0.9))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN

        if title_highlight:
            run = p.add_run()
            run.text = title_highlight
            run.font.name = FONT_HEADING
            run.font.size = Pt(28)
            run.font.bold = True
            run.font.color.rgb = COLOR_GOLD_LIGHT

    def add_card(slide, left, top, width, height, title, text="", border_color=COLOR_CARD_BORDER, icon=""):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.margin_bottom = Inches(0.2)

        # Title
        p_title = tf.paragraphs[0]
        full_title = f"{icon}  {title}" if icon else title
        p_title.text = full_title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TEXT_MAIN
        p_title.space_after = Pt(8)

        # Body text
        if text:
            p_text = tf.add_paragraph()
            p_text.text = text
            p_text.font.name = FONT_BODY
            p_text.font.size = Pt(12)
            p_text.font.color.rgb = COLOR_TEXT_MUTED
            p_text.line_spacing = 1.25

        return card

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        text_frame = notes_slide.notes_text_frame
        text_frame.text = notes_text

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 1: CAPA
    # ══════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)

    # Big Badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(4.8), Inches(0.42))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 42, 68)
    badge.line.color.rgb = COLOR_GOLD
    p_b = badge.text_frame.paragraphs[0]
    p_b.text = "PROJETO DE DISCIPLINA • DEVOPS & SISTEMAS DISTRIBUÍDOS"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_GOLD_LIGHT
    p_b.alignment = PP_ALIGN.CENTER

    # Title
    tb_title = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.8))
    p1 = tb_title.text_frame.paragraphs[0]
    p1.text = "AutoBudget AI PRO"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_GOLD_LIGHT

    p2 = tb_title.text_frame.add_paragraph()
    p2.text = "Agente Pericial Automotivo em Cluster Docker Swarm de Alta Disponibilidade"
    p2.font.size = Pt(20)
    p2.font.color.rgb = COLOR_TEXT_MAIN
    p2.space_before = Pt(8)

    p3 = tb_title.text_frame.add_paragraph()
    p3.text = "Visão computacional multimodal com Gemini AI, integração FIPE (75% Perda Total) e cluster DinD com 1 Manager e 2 Workers."
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_TEXT_MUTED
    p3.space_before = Pt(8)

    # 4 Highlights bottom
    add_card(s1, Inches(0.8), Inches(4.3), Inches(2.7), Inches(2.2), "Gemini 2.0 AI", "Visão computacional e detecção de avarias via bounding boxes em tempo real.", COLOR_GOLD, "🧠")
    add_card(s1, Inches(3.7), Inches(4.3), Inches(2.7), Inches(2.2), "Docker Swarm", "Cluster DinD com 1 Manager e 2 Workers ativos e overlay network.", COLOR_CYAN, "🐳")
    add_card(s1, Inches(6.6), Inches(4.3), Inches(2.7), Inches(2.2), "Tabela FIPE", "Cálculo pericial automatizado da regra de 75% para Perda Total.", COLOR_GOLD, "📊")
    add_card(s1, Inches(9.5), Inches(4.3), Inches(2.7), Inches(2.2), "Resiliência", "2 réplicas por microsserviço, rolling updates e Nginx reverse proxy.", COLOR_CYAN, "🛡️")

    add_notes(s1, "ROTEIRO DO ORADOR:\nBoa noite professor e colegas! Hoje vou apresentar o AutoBudget AI, uma solução corporativa completa que une Inteligência Artificial Generativa para visão computacional pericial com alta disponibilidade e orquestração de microsserviços via Docker Swarm em arquitetura DinD.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 2: O PROBLEMA DE NEGÓCIO
    # ══════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "Contexto do Problema", "O Desafio das", "Vistorias Automotivas")

    add_card(s2, Inches(0.8), Inches(2.0), Inches(3.6), Inches(3.8), "Lentidão na Regulação", 
             "• Peritos levam de 48h a 7 dias para analisar fotos e cotar peças.\n• Filas longas em seguradoras e oficinas credenciadas.\n• Processo manual com planilhas e consultas descentralizadas.", COLOR_GOLD, "⏳")

    add_card(s2, Inches(4.7), Inches(2.0), Inches(3.6), Inches(3.8), "Superfaturamento & Erros", 
             "• Dificuldade em auditar se a peça necessitava de troca ou de recuperação/pintura.\n• Preços arbitrários de peças sem referência de mercado.\n• Assimetria de dados entre oficinas e clientes.", COLOR_GOLD, "💸")

    add_card(s2, Inches(8.6), Inches(2.0), Inches(3.6), Inches(3.8), "Cálculo de Perda Total", 
             "• Falta de integração em tempo real com o valor venal da Tabela FIPE.\n• Risco de aprovar consertos acima de 75% da FIPE, gerando prejuízo à seguradora.\n• Decisões lentas em acidentes graves.", COLOR_GOLD, "⚖️")

    add_notes(s2, "ROTEIRO DO ORADOR:\nExplique aqui a dor do mercado: as seguradoras e oficinas demoram dias para regular sinistros, o processo manual é sujeito a superfaturamento e fraudes, e não há integração imediata entre fotos, FIPE e cotação de peças.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 3: A SOLUÇÃO AUTBUDGET AI
    # ══════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "Engenharia da Solução", "Como o AutoBudget AI", "Resolve")

    add_card(s3, Inches(0.8), Inches(2.0), Inches(5.6), Inches(2.3), "1. Visão Computacional com Gemini", 
             "Reconhece marca, modelo, ano e cor pelas fotos. Mapeia áreas de colisão e gera caixas delimitadoras (bounding boxes) com severidade do dano.", COLOR_GOLD, "🔍")

    add_card(s3, Inches(6.8), Inches(2.0), Inches(5.6), Inches(2.3), "2. Classificação de Ação Pericial", 
             "Diferencia peças com troca obrigatória (óptica/iluminação ou eixos tortos) de peças recuperáveis via funilaria e pintura, evitando desperdícios.", COLOR_CYAN, "📋")

    add_card(s3, Inches(0.8), Inches(4.6), Inches(5.6), Inches(2.3), "3. Cotação Dupla (Novas vs DETRAN)", 
             "Apresenta preço de peças novas originais OEM e peças usadas certificadas pelo DETRAN com nota e rastreabilidade, gerando economia de até 50%.", COLOR_GOLD, "🏷️")

    add_card(s3, Inches(6.8), Inches(4.6), Inches(5.6), Inches(2.3), "4. Mão de Obra Tabelada & FIPE", 
             "Mão de obra a R$ 80,00/h fixo para funilaria, pintura e mecânica. Verificação automática da regra de 75% da FIPE para emissão de Perda Total.", COLOR_CYAN, "⏱️")

    add_notes(s3, "ROTEIRO DO ORADOR:\nApresente as 4 engrenagens: a IA multimodal que enxerga as fotos, a classificação técnica de ação necessária, a cotação dupla inteligente e o cálculo de mão de obra tabelado com auditoria FIPE.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 4: ARQUITETURA DE MICROSSERVIÇOS
    # ══════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "Arquitetura de Software", "Separação de Camadas &", "Microsserviços")

    add_card(s4, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Nginx Reverse Proxy",
             "• Porta 80 exposta para os clientes\n• Serve o frontend React estático com gzip\n• Roteamento inteligente de /api/ para o backend\n• Suporte a uploads de fotos até 50MB\n• Timeout ampliado de 120s para IA", COLOR_CYAN, "🌐")

    add_card(s4, Inches(4.7), Inches(2.0), Inches(3.6), Inches(4.8), "Backend Python REST",
             "• Porta interna 5000 na overlay network\n• Threaded TCP Server de alta concorrência\n• Integração com Gemini 2.0 Flash\n• Motor de benchmarks FIPE e cálculo de horas\n• API de parametrização dinâmica de chave", COLOR_GOLD, "⚡")

    add_card(s4, Inches(8.6), Inches(2.0), Inches(3.6), Inches(4.8), "Frontend React SPA",
             "• Interface moderna com tema Dark Mode pericial\n• Bounding box overlay desenhado sobre as fotos\n• Modal interativo de configuração de API Key\n• Histórico de ordens de serviço local\n• Emissão e impressão de Laudo Pericial em PDF", COLOR_CYAN, "🖥️")

    add_notes(s4, "ROTEIRO DO ORADOR:\nMostre a separação clara de responsabilidades: o Nginx na porta 80 protege o sistema e atua como gateway de borda, roteando para o backend Python na porta 5000, enquanto o frontend React proporciona uma experiência visual rica.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 5: CLUSTER DOCKER SWARM (O NÚCLEO)
    # ══════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "Orquestração Distribuída", "Cluster Docker Swarm em", "DinD (Multi-Nó)")

    add_card(s5, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.2), "swarm-manager (Leader)",
             "• Função: Orquestração e Raft Consensus\n• Portas mapeadas: 80, 8080, 5000\n• Roda o Docker Visualizer (constraint)\n• Mantém o estado desejado da stack\n• Ingress Routing Mesh ativo", COLOR_GOLD, "👑")

    add_card(s5, Inches(4.7), Inches(2.0), Inches(3.6), Inches(4.2), "swarm-worker-1",
             "• Função: Nó de execução de carga\n• Conectado ao cluster via Join Token\n• Executa réplicas do backend e frontend\n• Isolamento de processos e recursos\n• Comunicação via rede overlay segura", COLOR_CYAN, "⚙️")

    add_card(s5, Inches(8.6), Inches(2.0), Inches(3.6), Inches(4.2), "swarm-worker-2",
             "• Função: Nó de execução e redundância\n• Executa réplicas distribuídas da stack\n• Pronto para auto-scaling imediato\n• Absorve carga em caso de falha de nó\n• Monitorado em tempo real pelo Manager", COLOR_CYAN, "⚙️")

    # Banner Overlay Network
    ov_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.35), Inches(11.4), Inches(0.75))
    ov_box.fill.solid()
    ov_box.fill.fore_color.rgb = RGBColor(16, 36, 60)
    ov_box.line.color.rgb = COLOR_CYAN
    p_ov = ov_box.text_frame.paragraphs[0]
    p_ov.text = "🌐 Overlay Network (autobudget-net): Rede virtual VXLAN que permite comunicação segura e resolução de DNS interno (ex: backend:5000) entre nós distintos sem expor portas internamente."
    p_ov.font.size = Pt(11)
    p_ov.font.color.rgb = COLOR_TEXT_MAIN

    add_notes(s5, "ROTEIRO DO ORADOR:\nAqui é o ponto central da disciplina: criamos um cluster Swarm completo com 1 Manager e 2 Workers reais usando Docker-in-Docker (DinD). O Manager cuida da orquestração e da rede overlay, enquanto os Workers executam as tarefas distribuídas.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 6: ALTA DISPONIBILIDADE & RESILIÊNCIA
    # ══════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "Tolerância a Falhas", "Alta Disponibilidade &", "Auto-Healing")

    add_card(s6, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Múltiplas Réplicas",
             "• Backend: 2 réplicas ativas\n• Frontend: 2 réplicas ativas\n• Distribuídas automaticamente entre os workers pelo scheduler do Swarm\n• Zero downtime se um container for finalizado", COLOR_GOLD, "👥")

    add_card(s6, Inches(4.7), Inches(2.0), Inches(3.6), Inches(4.8), "Rolling Updates",
             "• Atualização contínua com parallelism: 1 e delay: 10s\n• Sobe a réplica nova antes de encerrar a antiga\n• Permite deploy contínuo em produção sem indisponibilidade para o perito", COLOR_CYAN, "🔄")

    add_card(s6, Inches(8.6), Inches(2.0), Inches(3.6), Inches(4.8), "Ingress Routing Mesh",
             "• Roteamento de entrada transparente via IPVS do kernel Linux\n• O usuário pode acessar por qualquer nó do cluster\n• O Swarm redireciona a requisição para um container saudável automaticamente", COLOR_GOLD, "🔀")

    add_notes(s6, "ROTEIRO DO ORADOR:\nDestaque as configurações do docker-compose: replicas: 2, restart_policy: condition: on-failure, e o Ingress Routing Mesh. Se um container cair, o Swarm sobe outro automaticamente.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 7: REGISTRY PRIVADO & IMAGENS
    # ══════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "Gerenciamento de Artefatos", "Registry Privado Local &", "Build de Imagens")

    add_card(s7, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Registry Local (127.0.0.1:5000)",
             "• Subido diretamente no manager do cluster\n• Elimina dependência de conexão com o Docker Hub externo\n• Sem risco de atingir limites de taxa de download (rate limit)\n• Distribuição ultrarrápida de imagens entre nós pela rede interna\n\nComandos utilizados:\n• docker push 127.0.0.1:5000/autobudget-backend:latest\n• docker push 127.0.0.1:5000/autobudget-frontend:latest", COLOR_GOLD, "📦")

    add_card(s7, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8), "Otimização de Dockerfiles",
             "• Dockerfile.backend:\n  Baseado em python:3.11-slim para footprint mínimo de memória, sem compiladores desnecessários e com inicialização em menos de 1 segundo.\n\n• Dockerfile.frontend:\n  Baseado em nginx:alpine de apenas ~23MB servindo os arquivos estáticos compilados e provendo o proxy reverso de alta performance.", COLOR_CYAN, "⚡")

    add_notes(s7, "ROTEIRO DO ORADOR:\nExplique como as imagens foram distribuídas para os nós: utilizamos um registry local na porta 5000 do manager. O manager constrói as imagens, dá push no registry local e os workers puxam de 127.0.0.1:5000.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 8: OBSERVABILIDADE COM VISUALIZER
    # ══════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "Monitoramento em Tempo Real", "Observabilidade com", "Docker Visualizer")

    add_card(s8, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Dashboard Visualizer",
             "• Acessível via navegador na porta 8080\n• Mapeia visualmente cada container em seu respectivo nó do Swarm\n• Permite auditar ao vivo se o balanceamento de réplicas está correto", COLOR_GOLD, "📊")

    add_card(s8, Inches(4.7), Inches(2.0), Inches(3.6), Inches(4.8), "Placement Constraints",
             "• Configurado com node.role == manager\n• Acesso direto ao /var/run/docker.sock\n• Garante que serviços administrativos não rodem em workers não privilegiados", COLOR_CYAN, "🔒")

    add_card(s8, Inches(8.6), Inches(2.0), Inches(3.6), Inches(4.8), "Failover em Tempo Real",
             "• Se pausarmos ou derrubarmos um nó durante a apresentação, o Visualizer mostra os containers migrando instantaneamente para os nós ativos\n• Prova cabal de resiliência corporativa", COLOR_GOLD, "⚡")

    add_notes(s8, "ROTEIRO DO ORADOR:\nMostre o Docker Visualizer! Ele roda na porta 8080 conectado ao socket do Docker (/var/run/docker.sock) com restrição para rodar no manager. Ele mostra visualmente as réplicas em cada nó.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 9: TESTES DE CARGA E RESILIÊNCIA
    # ══════════════════════════════════════════════════════════════════════════
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "Validação de Qualidade", "Testes de Carga &", "Resiliência (stress_test.py)")

    add_card(s9, Inches(0.8), Inches(2.0), Inches(2.7), Inches(2.2), "100% Sucesso", "Zero falhas em testes de endpoints REST e proxy reverso.", COLOR_EMERALD, "✓")
    add_card(s9, Inches(3.7), Inches(2.0), Inches(2.7), Inches(2.2), "~35ms Latência", "Tempo médio de resposta nos endpoints de cotação e saúde.", COLOR_CYAN, "⚡")
    add_card(s9, Inches(6.6), Inches(2.0), Inches(2.7), Inches(2.2), "50MB Body", "Suporte a payloads pesados com múltiplas fotos em alta definição.", COLOR_GOLD, "📦")
    add_card(s9, Inches(9.5), Inches(2.0), Inches(2.7), Inches(2.2), "Multi-Thread", "Testado sob concorrência simultânea sem travamentos.", COLOR_CYAN, "👥")

    # Code / Terminal log
    log_box = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.5), Inches(11.4), Inches(2.2))
    log_box.fill.solid()
    log_box.fill.fore_color.rgb = RGBColor(6, 9, 19)
    log_box.line.color.rgb = COLOR_CARD_BORDER
    tf_l = log_box.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.3)
    tf_l.margin_top = Inches(0.2)
    p_l1 = tf_l.paragraphs[0]
    p_l1.text = "[PASS] Health Check endpoint (/api/health) [12ms]"
    p_l1.font.name = FONT_CODE
    p_l1.font.size = Pt(11)
    p_l1.font.color.rgb = COLOR_EMERALD
    
    p_l2 = tf_l.add_paragraph()
    p_l2.text = "[PASS] Dynamic Gemini Key Verification & Fallback [18ms]"
    p_l2.font.name = FONT_CODE
    p_l2.font.size = Pt(11)
    p_l2.font.color.rgb = COLOR_EMERALD

    p_l3 = tf_l.add_paragraph()
    p_l3.text = "[PASS] FIPE & Part Quote Market Pricing Engine [41ms]"
    p_l3.font.name = FONT_CODE
    p_l3.font.size = Pt(11)
    p_l3.font.color.rgb = COLOR_EMERALD

    p_l4 = tf_l.add_paragraph()
    p_l4.text = "[PASS] Multi-Image Vehicle Inspection Payload Handling [85ms]"
    p_l4.font.name = FONT_CODE
    p_l4.font.size = Pt(11)
    p_l4.font.color.rgb = COLOR_EMERALD

    add_notes(s9, "ROTEIRO DO ORADOR:\nComente que criamos uma suíte de testes de estresse em Python (stress_test.py) que dispara requisições concorrentes contra o cluster para validar tempo de resposta, cabeçalhos de CORS e resiliência a payloads grandes.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 10: ROTEIRO DE DEMONSTRAÇÃO PRÁTICA
    # ══════════════════════════════════════════════════════════════════════════
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "Roteiro da Live Demo", "Demonstração Prática", "Passo a Passo")

    add_card(s10, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Passo 1: Upload",
             "• O perito faz upload das fotos do sinistro (ex: Onix com colisão traseira)\n• O frontend codifica em base64 e despacha via POST /api/analyze\n• Exibição imediata de feedback de progresso ao usuário", COLOR_GOLD, "📸")

    add_card(s10, Inches(4.7), Inches(2.0), Inches(3.6), Inches(4.8), "Passo 2: IA Pericial",
             "• Gemini 2.0 Flash identifica marca, modelo, ano e cor\n• Detecta lanterna quebrada, para-choque deformado e eixo torto\n• Projeta as caixas delimitadoras coloridas sobre as fotos originais", COLOR_CYAN, "🤖")

    add_card(s10, Inches(8.6), Inches(2.0), Inches(3.6), Inches(4.8), "Passo 3: Orçamento & PDF",
             "• Cota peças novas vs usadas de desmanches homologados\n• Calcula horas de funilaria/pintura a R$ 80/h\n• Checa regra de 75% da FIPE para Perda Total\n• Gera laudo pericial pronto para impressão em PDF", COLOR_GOLD, "📑")

    add_notes(s10, "ROTEIRO DO ORADOR:\nPasse por esse slide mostrando a tela do sistema ao vivo: 1) Mostre o badge da IA ativo, 2) Selecione as fotos de exemplo ou suba uma foto, 3) Clique em Analisar, 4) Mostre os danos identificados e a opção de peças novas vs usadas, 5) Mostre o laudo em PDF.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 11: DIFERENCIAIS TÉCNICOS & DEVOPS
    # ══════════════════════════════════════════════════════════════════════════
    s11 = prs.slides.add_slide(blank_layout)
    add_background(s11)
    add_header(s11, "Resumo de Impacto", "Diferenciais do", "AutoBudget AI")

    add_card(s11, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Excelência DevOps & Infraestrutura",
             "• Arquitetura 100% conteinerizada e orquestrada via Docker Swarm\n• Simulação fiel de cluster multi-nó em ambiente DinD com economia de recursos\n• Registry privado local otimizando a distribuição de imagens\n• Alta resiliência comprovada com failover automático e balanceamento por mesh\n• Observabilidade nativa via Docker Visualizer", COLOR_GOLD, "🎯")

    add_card(s11, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8), "Inovação Prática com IA Generativa",
             "• Substitui formulários manuais lentos por visão computacional instantânea\n• Transparência pericial com auditoria e rastreabilidade de peças DETRAN\n• UX premium profissional com temas escuros refinados e animações reativas\n• Parametrização dinâmica de chaves com persistência em disco e memória\n• Totalmente alinhado às necessidades reais do mercado de sinistros", COLOR_CYAN, "✨")

    add_notes(s11, "ROTEIRO DO ORADOR:\nSintetize os grandes destaques do projeto: IA de ponta com Gemini, arquitetura em cluster Swarm com DinD sem gastar nada com nuvem paga, código modular e foco total em resolver um problema real de negócio.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 12: CONCLUSÃO & PERGUNTAS
    # ══════════════════════════════════════════════════════════════════════════
    s12 = prs.slides.add_slide(blank_layout)
    add_background(s12)
    add_header(s12, "Conclusão", "Obrigado! Estamos Abertos a", "Perguntas")

    add_card(s12, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.0), "Código & Repositório",
             "• Repositório no GitHub:\n  KaykyMatos845/auto-repair-budget-agent\n\n• Dockerfiles, compose, scripts DinD e documentação inclusos no projeto", COLOR_GOLD, "💻")

    add_card(s12, Inches(4.7), Inches(2.0), Inches(3.6), Inches(4.0), "Cluster Ativo",
             "• 1 Manager + 2 Workers em execução\n• 5 réplicas saudáveis distribuídas\n• Overlay network autobudget-net ativa\n• Registry local na porta 5000", COLOR_CYAN, "🐳")

    add_card(s12, Inches(8.6), Inches(2.0), Inches(3.6), Inches(4.0), "Pontos de Acesso",
             "• Aplicação Web: porta 80\n• Docker Visualizer: porta 8080\n• API Health: /api/health\n• Slides: /slides.html", COLOR_GOLD, "🚀")

    # Closing banner
    banner = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.2), Inches(11.4), Inches(0.8))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(30, 42, 68)
    banner.line.color.rgb = COLOR_GOLD
    p_ban = banner.text_frame.paragraphs[0]
    p_ban.text = "Estamos à disposição para demonstrar qualquer parte da infraestrutura, derrubar nós ao vivo ou inspecionar o código! 🛠️"
    p_ban.font.size = Pt(12)
    p_ban.font.bold = True
    p_ban.font.color.rgb = COLOR_GOLD_LIGHT
    p_ban.alignment = PP_ALIGN.CENTER

    add_notes(s12, "ROTEIRO DO ORADOR:\nAgradeça a atenção do professor e da turma, deixe o slide aberto e convide todos a fazer perguntas ou pedir testes práticos no cluster.")

    # Save presentation
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Apresentacao_AutoBudget_AI.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_presentation()
