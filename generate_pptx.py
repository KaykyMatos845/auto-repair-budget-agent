import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(DIRECTORY, "assets")
SAMPLES_DIR = os.path.join(DIRECTORY, "public", "samples")

# ── Colors & Styles ──────────────────────────────────────────────────────────
COLOR_BG = RGBColor(10, 15, 29)          # #0A0F1D Deep Dark Navy
COLOR_CARD = RGBColor(20, 29, 48)        # #141D30 Card Navy
COLOR_CARD_BORDER = RGBColor(38, 53, 84) # Subtle slate border
COLOR_GOLD = RGBColor(245, 158, 11)      # #F59E0B Gold
COLOR_GOLD_LIGHT = RGBColor(251, 191, 36)
COLOR_CYAN = RGBColor(6, 182, 212)       # #06B6D4 Cyan
COLOR_CYAN_LIGHT = RGBColor(56, 189, 248)
COLOR_EMERALD = RGBColor(16, 185, 129)   # #10B981 Emerald
COLOR_ROSE = RGBColor(244, 63, 94)       # #F43F5E Rose
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

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, title_highlight=""):
        # Tag Badge
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(4.8), Inches(0.36))
        tag.fill.solid()
        tag.fill.fore_color.rgb = RGBColor(28, 40, 65)
        tag.line.color.rgb = COLOR_GOLD
        tag.line.width = Pt(1)
        p_t = tag.text_frame.paragraphs[0]
        p_t.text = tag_text.upper()
        p_t.font.name = FONT_BODY
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_GOLD_LIGHT
        p_t.alignment = PP_ALIGN.CENTER

        # Title
        tx = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.5), Inches(0.8))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN

        if title_highlight:
            run = p.add_run()
            run.text = title_highlight
            run.font.name = FONT_HEADING
            run.font.size = Pt(26)
            run.font.bold = True
            run.font.color.rgb = COLOR_GOLD_LIGHT

    def add_metric_card(slide, left, top, width, height, number, label, subtext="", border_color=COLOR_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.18)
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)

        # Number
        p_num = tf.paragraphs[0]
        p_num.text = number
        p_num.font.name = FONT_HEADING
        p_num.font.size = Pt(28)
        p_num.font.bold = True
        p_num.font.color.rgb = border_color
        p_num.alignment = PP_ALIGN.LEFT

        # Label
        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.font.name = FONT_HEADING
        p_lbl.font.size = Pt(13)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = COLOR_TEXT_MAIN
        p_lbl.space_before = Pt(4)

        if subtext:
            p_sub = tf.add_paragraph()
            p_sub.text = subtext
            p_sub.font.name = FONT_BODY
            p_sub.font.size = Pt(10)
            p_sub.font.color.rgb = COLOR_TEXT_MUTED
            p_sub.space_before = Pt(2)

        return card

    def add_notes(slide, notes):
        slide.notes_slide.notes_text_frame.text = "NOTAS DO ORADOR (O QUE FALAR):\n" + notes

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 1: CAPA VISUAL COM FOTO DO PROJETO
    # ══════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    # Left: Headlines & Metrics
    tx1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(5.8), Inches(2.5))
    tf1 = tx1.text_frame
    tf1.word_wrap = True
    p_tag = tf1.paragraphs[0]
    p_tag.text = "PROJETO DE DISCIPLINA • DEVOPS & SISTEMAS DISTRIBUÍDOS"
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_GOLD_LIGHT

    p_title = tf1.add_paragraph()
    p_title.text = "AutoBudget AI"
    p_title.font.size = Pt(46)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_GOLD_LIGHT
    p_title.space_before = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Vistoria Automotiva com Visão Computacional & Orquestração em Cluster Docker Swarm"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = COLOR_TEXT_MAIN
    p_sub.space_before = Pt(6)

    # 3 Metrics pills left
    add_metric_card(s1, Inches(0.8), Inches(4.2), Inches(1.8), Inches(2.4), "IA", "Gemini 2.0", "Visão computacional e bounding boxes", COLOR_GOLD)
    add_metric_card(s1, Inches(2.8), Inches(4.2), Inches(1.8), Inches(2.4), "3 Nós", "Cluster DinD", "1 Manager + 2 Workers reais", COLOR_CYAN)
    add_metric_card(s1, Inches(4.8), Inches(4.2), Inches(1.8), Inches(2.4), "100%", "Disponível", "Zero downtime e auto-healing", COLOR_EMERALD)

    # Right: Big Image (Annotated Car Inspection)
    ai_img_path = os.path.join(ASSETS_DIR, "ai_annotated_inspection.jpg")
    if os.path.exists(ai_img_path):
        s1.shapes.add_picture(ai_img_path, Inches(6.9), Inches(1.1), width=Inches(5.6))

    add_notes(s1, "Boa noite professor e turma! Hoje apresento o AutoBudget AI. O projeto une Inteligência Artificial de visão computacional para detecção de danos em veículos com alta disponibilidade corporativa em um cluster Docker Swarm de 3 nós.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 2: O PROBLEMA (VISUAL ANTES VS DEPOIS)
    # ══════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "Contexto do Problema", "O Cenário Atual vs", "AutoBudget AI")

    # Column Left: O Processo Tradicional (Gargalo)
    card_trad = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    card_trad.fill.solid()
    card_trad.fill.fore_color.rgb = RGBColor(26, 20, 24)
    card_trad.line.color.rgb = COLOR_ROSE
    card_trad.line.width = Pt(2)
    tf_tr = card_trad.text_frame
    tf_tr.word_wrap = True
    tf_tr.margin_left = Inches(0.3)
    tf_tr.margin_top = Inches(0.3)
    p_tr_h = tf_tr.paragraphs[0]
    p_tr_h.text = "⚠️ PROCESSO TRADICIONAL (MANUAL)"
    p_tr_h.font.size = Pt(16)
    p_tr_h.font.bold = True
    p_tr_h.font.color.rgb = COLOR_ROSE
    p_tr_h.space_after = Pt(14)

    items_trad = [
        ("⏳ 48h a 7 dias", "Demora na regulação do sinistro"),
        ("💸 Cotações Manuais", "Preços arbitrários e risco de superfaturamento"),
        ("📄 Sem Cruzamento FIPE", "Dificuldade em auditar a regra de 75% Perda Total"),
        ("❌ Vistoria Subjetiva", "Sem mapeamento visual rastreável das peças trocadas")
    ]
    for title, desc in items_trad:
        p1 = tf_tr.add_paragraph()
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(13)
        p1.font.color.rgb = COLOR_TEXT_MAIN
        p2 = tf_tr.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_after = Pt(8)

    # Column Right: A Solução AutoBudget
    card_auto = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0))
    card_auto.fill.solid()
    card_auto.fill.fore_color.rgb = RGBColor(16, 32, 40)
    card_auto.line.color.rgb = COLOR_EMERALD
    card_auto.line.width = Pt(2)
    tf_au = card_auto.text_frame
    tf_au.word_wrap = True
    tf_au.margin_left = Inches(0.3)
    tf_au.margin_top = Inches(0.3)
    p_au_h = tf_au.paragraphs[0]
    p_au_h.text = "✨ COM AUTBUDGET AI (AUTOMATIZADO)"
    p_au_h.font.size = Pt(16)
    p_au_h.font.bold = True
    p_au_h.font.color.rgb = COLOR_EMERALD
    p_au_h.space_after = Pt(14)

    items_auto = [
        ("⚡ 15 Segundos", "Diagnóstico pericial instantâneo via IA multimodal"),
        ("🏷️ Cotação Dupla Transparente", "Peças novas OEM vs usadas certificadas pelo DETRAN"),
        ("📊 Tabela FIPE Integrada", "Cálculo matemático automático da regra de 75%"),
        ("🎯 Bounding Boxes Visuais", "Caixas delimitadoras em cada peça danificada")
    ]
    for title, desc in items_auto:
        p1 = tf_au.add_paragraph()
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(13)
        p1.font.color.rgb = COLOR_TEXT_MAIN
        p2 = tf_au.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_after = Pt(8)

    add_notes(s2, "Explique a dor do mercado: as vistorias tradicionais são lentas e manuais. Mostre o contraste: o AutoBudget AI reduz o tempo de 7 dias para apenas 15 segundos, com dados FIPE e cotação de mercado em tempo real.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 3: VISÃO COMPUTACIONAL NA PRÁTICA (COM IMAGEM)
    # ══════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "Inteligência Artificial", "Visão Computacional &", "Mapeamento de Danos")

    # Left: Big Annotated Car Picture
    if os.path.exists(ai_img_path):
        s3.shapes.add_picture(ai_img_path, Inches(0.8), Inches(1.8), width=Inches(6.2))

    # Right: 3 Visual Highlight Cards
    add_metric_card(s3, Inches(7.3), Inches(1.8), Inches(5.2), Inches(1.5), "Identificação", "Veículo & Modelo", "Marca, modelo, ano e cor identificados pelas fotos.", COLOR_GOLD)
    add_metric_card(s3, Inches(7.3), Inches(3.5), Inches(5.2), Inches(1.5), "Classificação", "Ação Pericial", "Diferencia troca de lanterna de recuperação de lata.", COLOR_CYAN)
    add_metric_card(s3, Inches(7.3), Inches(5.2), Inches(5.2), Inches(1.5), "Bounding Boxes", "Coordenadas Reais", "Caixas delimitadoras percentuais projetadas sobre o dano.", COLOR_EMERALD)

    add_notes(s3, "Mostre a foto na tela: a IA recebe fotos do carro batido e analisa em 3 níveis: identifica o modelo, gera as caixas coloridas nos pontos de impacto e decide a ação (substituição obrigatória para óptica ou recuperação para lata).")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 4: ARQUITETURA DE MICROSSERVIÇOS (PIPELINE)
    # ══════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "Arquitetura de Software", "Separação em Camadas &", "Microsserviços")

    add_metric_card(s4, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), "01. BORDA", "Nginx Reverse Proxy", 
                    "• Porta pública 80\n• Serve o frontend React estático\n• Compressão Gzip ativa\n• Proxy reverso /api/ -> backend\n• Upload de fotos até 50MB\n• Timeout de 120s para IA", COLOR_CYAN)

    add_metric_card(s4, Inches(4.7), Inches(1.8), Inches(3.6), Inches(4.8), "02. LÓGICA", "Python REST API", 
                    "• Porta interna 5000\n• Threaded TCP Server de alta concorrência\n• Integração com Gemini 2.0 Flash\n• Banco FIPE e cotações de peças\n• Cálculo de R$ 80/h de mão de obra", COLOR_GOLD)

    add_metric_card(s4, Inches(8.6), Inches(1.8), Inches(3.6), Inches(4.8), "03. CLIENTE", "React Standalone SPA", 
                    "• Interface reativa em Dark Mode\n• Bounding box overlay nas imagens\n• Modal de configuração de API Key\n• Histórico de vistorias local\n• Emissão de laudo em PDF", COLOR_EMERALD)

    add_notes(s4, "Explique a modularidade: o Nginx expõe a porta 80 e encaminha as chamadas para a API Python na porta interna 5000 via rede overlay. Essa arquitetura é leve, segura e rápida.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 5: CLUSTER DOCKER SWARM (COM DIAGRAMA EM ALTA RESOLUÇÃO)
    # ══════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "Orquestração de Nós", "Topologia do Cluster", "Docker Swarm (DinD)")

    # Big Diagram Image
    diag_path = os.path.join(ASSETS_DIR, "swarm_cluster_diagram.png")
    if os.path.exists(diag_path):
        s5.shapes.add_picture(diag_path, Inches(0.8), Inches(1.8), width=Inches(11.7))

    add_notes(s5, "Este é o núcleo da disciplina: nosso cluster Swarm tem 1 nó Manager e 2 nós Workers rodando em Docker-in-Docker. Mostre no diagrama o Visualizer e o Registry no Manager, e as réplicas distribuídas nos Workers via Overlay Network.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 6: ALTA DISPONIBILIDADE & RESILIÊNCIA
    # ══════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Tolerância a Falhas", "Alta Disponibilidade &", "Auto-Healing")

    add_metric_card(s6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(3.0), "2 Réplicas", "Redundância Ativa", "Backend e frontend rodam com 2 cópias ativas distribuídas entre os nós.", COLOR_GOLD)
    add_metric_card(s6, Inches(4.7), Inches(1.8), Inches(3.6), Inches(3.0), "Auto-Healing", "Reinicialização Automática", "restart_policy: on-failure garante recuperação imediata em caso de falha.", COLOR_EMERALD)
    add_metric_card(s6, Inches(8.6), Inches(1.8), Inches(3.6), Inches(3.0), "Zero Downtime", "Rolling Updates", "Atualizações graduais com delay de 10s sem derrubar a aplicação.", COLOR_CYAN)

    # Bottom Terminal Box with code
    box_code = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.1), Inches(11.4), Inches(1.8))
    box_code.fill.solid()
    box_code.fill.fore_color.rgb = RGBColor(6, 9, 19)
    box_code.line.color.rgb = COLOR_CARD_BORDER
    tf_c = box_code.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = Inches(0.3)
    tf_c.margin_top = Inches(0.2)
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "# Ingress Routing Mesh ativo na porta 80:"
    p_c1.font.name = FONT_CODE
    p_c1.font.size = Pt(11)
    p_c1.font.color.rgb = COLOR_TEXT_MUTED
    
    p_c2 = tf_c.add_paragraph()
    p_c2.text = "docker service update --image 127.0.0.1:5000/autobudget-backend:latest --force autobudget_backend"
    p_c2.font.name = FONT_CODE
    p_c2.font.size = Pt(11)
    p_c2.font.color.rgb = COLOR_CYAN_LIGHT

    p_c3 = tf_c.add_paragraph()
    p_c3.text = "[OK] 2/2 replicas atualizadas com sucesso • Zero perda de pacotes"
    p_c3.font.name = FONT_CODE
    p_c3.font.size = Pt(11)
    p_c3.font.color.rgb = COLOR_EMERALD

    add_notes(s6, "Destaque como o Swarm trata falhas: se um container cair, o Swarm sobe outro automaticamente. Se atualizarmos a imagem, ele faz rolling update sem o usuário perceber.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 7: REGISTRY PRIVADO LOCAL & IMAGENS
    # ══════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "Gerenciamento de Artefatos", "Registry Privado Local &", "Imagens Slim/Alpine")

    add_metric_card(s7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), "Porta 5000", "Registry Local", 
                    "• Subido diretamente no manager\n• Elimina dependência do Docker Hub\n• Sem limite de rate limit de downloads\n• Distribuição instantânea pela rede interna\n• docker push 127.0.0.1:5000/backend:latest", COLOR_GOLD)

    add_metric_card(s7, Inches(4.7), Inches(1.8), Inches(3.6), Inches(4.8), "~23 MB", "Nginx Alpine (Frontend)", 
                    "• Imagem ultraleve para borda\n• Tempo de boot em milissegundos\n• Superfície de ataque reduzida\n• Servindo bundle React e Nginx config", COLOR_CYAN)

    add_metric_card(s7, Inches(8.6), Inches(1.8), Inches(3.6), Inches(4.8), "Python Slim", "Backend Otimizado", 
                    "• Baseado em python:3.11-slim\n• Sem compiladores desnecessários\n• Inicialização em menos de 1s\n• Consumo mínimo de RAM por réplica", COLOR_EMERALD)

    add_notes(s7, "Explique o Registry local na porta 5000: os nós puxam as imagens diretamente do Manager sem gastar internet e sem bater em limites de download do Docker Hub.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 8: OBSERVABILIDADE COM VISUALIZER
    # ══════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_header(s8, "Monitoramento do Cluster", "Observabilidade com", "Docker Visualizer")

    add_metric_card(s8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), "Porta 8080", "Dashboard em Tempo Real", 
                    "• Mapeia visualmente nós e réplicas\n• Atualização automática em tempo real\n• Audita se o balanceamento está correto\n• Visualização imediata de containers ativos", COLOR_GOLD)

    add_metric_card(s8, Inches(4.7), Inches(1.8), Inches(3.6), Inches(4.8), "Constraint", "node.role == manager", 
                    "• Restrição de colocação no compose\n• Acesso exclusivo ao docker.sock\n• Protege os workers de privilégios de root\n• Prática recomendada de segurança", COLOR_CYAN)

    add_metric_card(s8, Inches(8.6), Inches(1.8), Inches(3.6), Inches(4.8), "Ao Vivo", "Failover Visual", 
                    "• Se pausarmos um worker ao vivo, o Visualizer mostra os containers migrando na hora para os nós saudáveis\n• Excelente para demonstrar ao professor!", COLOR_EMERALD)

    add_notes(s8, "Apresente o Visualizer: ele roda na porta 8080 e mostra em blocos coloridos onde está cada réplica. Comente a constraint de segurança para rodar apenas no Manager.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 9: VALIDAÇÃO DE QUALIDADE (MÉTRICAS GRANDES)
    # ══════════════════════════════════════════════════════════════════════════
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9)
    add_header(s9, "Validação de Qualidade", "Resultados de Teste de Carga &", "Resiliência")

    add_metric_card(s9, Inches(0.8), Inches(1.8), Inches(2.7), Inches(2.4), "100%", "Taxa de Sucesso", "Zero erros nos testes de estresse REST", COLOR_EMERALD)
    add_metric_card(s9, Inches(3.7), Inches(1.8), Inches(2.7), Inches(2.4), "35 ms", "Latência Média", "Tempo de resposta dos endpoints da API", COLOR_CYAN)
    add_metric_card(s9, Inches(6.6), Inches(1.8), Inches(2.7), Inches(2.4), "50 MB", "Capacidade Payload", "Suporte a múltiplas fotos em alta resolução", COLOR_GOLD)
    add_metric_card(s9, Inches(9.5), Inches(1.8), Inches(2.7), Inches(2.4), "Concorrente", "Multi-Thread", "Testado sob múltiplas requisições simultâneas", COLOR_CYAN)

    # Bottom summary box
    box_test = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.5), Inches(11.4), Inches(2.2))
    box_test.fill.solid()
    box_test.fill.fore_color.rgb = COLOR_CARD
    box_test.line.color.rgb = COLOR_EMERALD
    tf_t = box_test.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = Inches(0.3)
    tf_t.margin_top = Inches(0.2)
    p_t1 = tf_t.paragraphs[0]
    p_t1.text = "SUÍTE DE TESTES AUTOMATIZADOS (stress_test.py):"
    p_t1.font.size = Pt(13)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_EMERALD

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "• Testes de integridade de headers CORS e proxy reverso Nginx [PASS]\n• Validação dinâmica da API Key do Gemini com contingência [PASS]\n• Simulação de upload e processamento de sinistro com imagem base64 [PASS]\n• Teste de concorrência com threads simultâneas simulando peritos ativos [PASS]"
    p_t2.font.size = Pt(11)
    p_t2.font.color.rgb = COLOR_TEXT_MAIN
    p_t2.space_before = Pt(6)

    add_notes(s9, "Apresente os dados de teste: criamos o stress_test.py para estressar a aplicação. Mostre que tivemos 100% de sucesso, com latência média de 35ms e capacidade de receber fotos grandes sem falhas.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 10: VEÍCULOS DE TESTE (GALERIA VISUAL COM 3 FOTOS REAIS)
    # ══════════════════════════════════════════════════════════════════════════
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10)
    add_header(s10, "Casos de Teste Reais", "Veículos Validados na", "Live Demo")

    # 3 Vehicle Photos with labels
    cars = [
        ("civic_front.jpg", Inches(0.8), "Honda Civic (Colisão Frontal)", "Farol e Para-choque"),
        ("corolla_side.jpg", Inches(4.7), "Toyota Corolla (Lateral)", "Porta e Retrovisor"),
        ("onix_rear.jpg", Inches(8.6), "Chevrolet Onix (Traseira)", "Lanterna e Eixo Traseiro")
    ]

    for fname, x_pos, car_title, car_parts in cars:
        fpath = os.path.join(SAMPLES_DIR, fname)
        if os.path.exists(fpath):
            s10.shapes.add_picture(fpath, x_pos, Inches(1.8), width=Inches(3.6), height=Inches(2.7))
        
        # Label card below image
        lbl_card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, Inches(4.7), Inches(3.6), Inches(2.0))
        lbl_card.fill.solid()
        lbl_card.fill.fore_color.rgb = COLOR_CARD
        lbl_card.line.color.rgb = COLOR_CARD_BORDER
        tf_l = lbl_card.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = Inches(0.2)
        tf_l.margin_top = Inches(0.18)
        p1 = tf_l.paragraphs[0]
        p1.text = car_title
        p1.font.bold = True
        p1.font.size = Pt(13)
        p1.font.color.rgb = COLOR_GOLD_LIGHT
        p2 = tf_l.add_paragraph()
        p2.text = f"Danos: {car_parts}\nStatus: Pronto para teste ao vivo"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(4)

    add_notes(s10, "Aqui mostramos os 3 carros reais incluídos no sistema: o Civic com colisão frontal, o Corolla com colisão lateral e o Onix com colisão traseira. Você pode rodar a análise de qualquer um ao vivo durante a apresentação!")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 11: DIFERENCIAIS TÉCNICOS & DEVOPS
    # ══════════════════════════════════════════════════════════════════════════
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11)
    add_header(s11, "Resumo de Destaques", "Diferenciais do", "AutoBudget AI")

    add_metric_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "DevOps & Cloud", "Excelência em Infraestrutura", 
                    "• 100% conteinerizado e escalável vertical e horizontalmente\n• Simulação fiel de cluster multi-nó em ambiente DinD\n• Registry privado local otimizando a distribuição de imagens\n• Alta resiliência comprovada com failover automático e balanceamento por mesh\n• Observabilidade nativa via Docker Visualizer", COLOR_GOLD)

    add_metric_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Inovação & IA", "Impacto Real de Negócio", 
                    "• Substitui formulários manuais por visão computacional instantânea\n• Transparência pericial com auditoria e rastreabilidade de peças DETRAN\n• UX premium profissional com temas escuros refinados e animações reativas\n• Parametrização dinâmica de chaves com persistência em disco e memória\n• Totalmente alinhado às necessidades reais do mercado de sinistros", COLOR_CYAN)

    add_notes(s11, "Sintetize os grandes destaques do projeto: IA de ponta com Gemini, arquitetura em cluster Swarm com DinD sem gastar nada com nuvem paga, código modular e foco total em resolver um problema real de negócio.")

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 12: CONCLUSÃO & PERGUNTAS
    # ══════════════════════════════════════════════════════════════════════════
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12)
    add_header(s12, "Encerramento", "Obrigado! Estamos Abertos a", "Perguntas")

    add_metric_card(s12, Inches(0.8), Inches(1.8), Inches(3.6), Inches(3.8), "GitHub", "Repositório Aberto", 
                    "KaykyMatos845/\nauto-repair-budget-agent\n\nCódigo-fonte, compose e scripts disponíveis.", COLOR_GOLD)

    add_metric_card(s12, Inches(4.7), Inches(1.8), Inches(3.6), Inches(3.8), "Cluster", "Estado Atual", 
                    "1 Manager + 2 Workers ativos\n5 Réplicas saudáveis\nOverlay Network ativa.", COLOR_CYAN)

    add_metric_card(s12, Inches(8.6), Inches(1.8), Inches(3.6), Inches(3.8), "Acessos", "Pontos de Entrada", 
                    "App Web: Porta 80\nVisualizer: Porta 8080\nSlides: /slides.html", COLOR_EMERALD)

    # Banner
    banner = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.4), Inches(0.9))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(28, 40, 65)
    banner.line.color.rgb = COLOR_GOLD
    p_b = banner.text_frame.paragraphs[0]
    p_b.text = "Estamos à disposição para demonstrar o cluster ao vivo, pausar nós ou inspecionar o código! 🛠️"
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_GOLD_LIGHT
    p_b.alignment = PP_ALIGN.CENTER

    add_notes(s12, "Agradeça a atenção do professor e da turma, deixe o slide aberto e convide todos a fazer perguntas ou pedir testes práticos no cluster.")

    # Save
    out_path = os.path.join(DIRECTORY, "Apresentacao_AutoBudget_AI.pptx")
    prs.save(out_path)
    print(f"Visually enriched presentation saved to: {out_path}")

if __name__ == "__main__":
    create_presentation()
