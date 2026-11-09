"""Extend the 20-slide deck using evidence visible in the project conversation.

No chat screenshot is fabricated: tables and diagrams explicitly identify themselves
as transcriptions/syntheses. All three videos were reviewed visually from their ZIP archives.
"""
from pathlib import Path
import argparse
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parents[1]
BG='F3F6F8'; NAVY='102F3B'; TEAL='0B786C'; MINT='92DFC4'; INK='183440'; MUTED='607582'; BORDER='DCE6EA'; WHITE='FFFFFF'; SOFT='E6F2ED'; AMBER='92641D'; PALE='FFF3DC'; RED='AE3946'
parser=argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=ROOT/'public/auto-repair-apresentacao-demonstracao.pptx')
args=parser.parse_args()
prs=Presentation(ROOT/'public/auto-repair-apresentacao-20-slides.pptx')
original=list(prs.slides._sldIdLst)


def rect(s,x,y,w,h,fill=WHITE,border=None):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(fill)
    sh.line.fill.background()
    if border: sh.line.color.rgb=RGBColor.from_string(border)
    sh.adjustments[0]=.1
    return sh


def text(s,x,y,w,h,value,size=20,color=INK,bold=False,font='Arial',align=PP_ALIGN.LEFT):
    sh=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=sh.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for n,line in enumerate(value.split('\n')):
        p=tf.paragraphs[0] if n==0 else tf.add_paragraph()
        p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold
        p.font.color.rgb=RGBColor.from_string(color);p.alignment=align;p.space_after=Pt(6)
    return sh


def base(chapter,title,subtitle):
    s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor.from_string(BG)
    text(s,.65,.4,12,.3,chapter.upper(),12,TEAL,True)
    text(s,.65,.95,12,.8,title,32,INK,True)
    text(s,.65,1.72,12,.48,subtitle,14,MUTED)
    rect(s,.65,7.03,12.02,.012,BORDER)
    text(s,.65,7.14,10,.2,'AUTO REPAIR  /  DOCKER & SWARM',9,MUTED)
    return s


def note(s,value): s.notes_slide.notes_text_frame.text=value


def code(s,x,y,w,h,value,size=18):
    rect(s,x,y,w,h,NAVY)
    text(s,x+.22,y+.17,w-.44,h-.25,value,size,MINT,font='Consolas')


def banner(s,value,warning=False):
    rect(s,.65,6.25,12.02,.55,PALE if warning else SOFT)
    text(s,.85,6.39,11.62,.3,value,14,AMBER if warning else TEAL,True)


def table(s,headers,rows,widths,y=2.4):
    x=.65
    for label,width in zip(headers,widths):
        rect(s,x,y,width-.03,.48,NAVY)
        text(s,x+.14,y+.11,width-.3,.3,label,14,WHITE,True);x+=width
    for j,row in enumerate(rows):
        x=.65;yy=y+.58+j*.67
        for label,width in zip(row,widths):
            rect(s,x,yy,width-.03,.59,WHITE,BORDER)
            text(s,x+.14,yy+.14,width-.3,.4,label,15,INK);x+=width


def node(s,x,y,w,title,status,services,down=False):
    rect(s,x,y,w,2.8,WHITE,BORDER)
    text(s,x+.22,y+.2,w-.44,.35,title,22,INK,True)
    text(s,x+.22,y+.68,w-.44,.3,status,15,RED if down else TEAL,True)
    for n,label in enumerate(services):
        yy=y+1.17+n*.34
        text(s,x+.25,yy,w-.5,.3,'• '+label,15,MUTED)


# Revise old slides so planned steps cannot be mistaken for observed results.
def replace(slide,old,new):
    found=False
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text==old:
            paragraph=shape.text_frame.paragraphs[0]
            if paragraph.runs:
                paragraph.runs[0].text=new
                for run in list(paragraph.runs)[1:]: run.text=''
                for extra in list(shape.text_frame.paragraphs)[1:]:
                    extra._p.getparent().remove(extra._p)
            else: shape.text=new
            found=True
    if not found: raise ValueError('Text not found: '+old)

replace(prs.slides[15],'Uma mudança declarativa, três etapas','Roteiro declarativo para variar réplicas')
replace(prs.slides[15],'Frontend e backend variam juntos. Visualizer e proxy permanecem em uma réplica.\nEm cada pausa, capture o gráfico real antes de continuar.','Roteiro pelo Compose: 1 → 2 → 1. Nos prints recebidos, a redução 2 → 1 foi feita pela CLI.\nA execução declarativa ainda precisa de um registro próprio.')
replace(prs.slides[17],'Saídas reais salvas pelo roteiro','Coleta automatizada disponível')
replace(prs.slides[17],'Aplicação em 1/1, depois 2/2 e novamente 1/1.','Prints: 2/2 → 1 pela CLI.\nCompose: execução pendente.')
replace(prs.slides[18],'Estado declarativo aplicado em 1 → 2 → 1 réplicas.','Compose configurado; redução 2 → 1 registrada via CLI.')
replace(prs.slides[18],'Docker Visualizer aberto e capturado nas três etapas.','Prints: duas réplicas, uma réplica e worker indisponível.')
replace(prs.slides[18],'Configuração preparada não substitui as evidências da execução real nas duas VMs.','As próximas evidências distinguem resultados observados e registros ainda pendentes.')
replace(prs.slides[19],'Roteiro: docs/DEMONSTRACAO.md\nConclua a comprovação com registros e capturas coletados nas duas VMs.','Demonstração: cluster, escala e falha do worker registrados em prints.\nTrês vídeos revisados e incorporados. Falta registrar a recuperação.')
for idx in [15,17,18,19]:
    note(prs.slides[idx], prs.slides[idx].notes_slide.notes_text_frame.text + '\nREVISÃO: os prints do chat confirmam redução via CLI e worker Down. Não foi comprovado o ciclo declarativo completo, a análise nova após a queda ou a recuperação. V01, V02 e V03 foram revisados visualmente e incorporados. V01 mostra uma nova análise e foi identificado pelo autor como teste após a queda. V02 mostra n2 Down com contagem ainda 2/2; não há captura simultânea do navegador e do terminal.')

s=base('Demonstração real','Dos arquivos à execução nas duas VMs','Prints do chat e três vídeos revisados; resultados e limites de cada registro.')
table(s,['Etapa','Evidência','Situação'],[
 ('Cluster inicial','P01 + P02 + P03','Dois nós; serviços 2/2'),
 ('Redução de réplicas','P04 + P05','Uma réplica por serviço'),
 ('Queda do worker','P06 + P07','n2 Down; tarefas no manager'),
 ('Aplicação / recuperação','V01 + V02 + V03','Análises vistas; retorno pendente'),
], [3.0,3.5,5.52])
banner(s,'Prints originais do ZIP, capturas dos vídeos e sínteses identificadas nos slides seguintes.')
note(s,'Ordem das fontes: P01 Visualizer inicial; P02 docker node ls inicial; P03 docker stack services inicial; P04 Visualizer com uma réplica; P05 comando docker service scale; P06 Visualizer após desligar n2; P07 docker node ls com n2 Down. O ZIP das fotos fornece P02–P07, incorporados aos slides correspondentes sem alterar o conteúdo. P01 foi visto apenas no chat; a distribuição inicial também é confirmada por P03.')

s=base('Evidência P02','Dois nós prontos no início','Transcrição dos campos legíveis do print de docker node ls; não é uma nova execução.')
code(s,.65,2.35,12.02,.64,'docker node ls',20)
table(s,['Hostname','Status','Availability','Manager'],[
 ('kayky','Ready','Active','Leader'),('n2','Ready','Active','—')
],[3.0,3.0,3.0,3.02],y=3.25)
text(s,.88,5.45,11.7,.4,'Docker Engine 29.9.2 em ambos os nós.',21,TEAL,True)
banner(s,'Active é a disponibilidade para agendamento; Ready é o estado de comunicação do nó.')
note(s,'Fonte P02. IDs omitidos para facilitar leitura; nenhuma linha de saída foi criada. A evidência confirma manager e worker com identidades distintas. O IP do manager é 192.168.165.135 e do worker 192.168.165.140, informados antes no chat.')

s=base('Evidência P03','Serviços convergidos antes do teste','Transcrição de docker stack services autobudget; imagens próprias com tag v5 no GHCR.')
code(s,.65,2.35,12.02,.64,'docker stack services autobudget',20)
table(s,['Serviço','Réplicas','Posicionamento / acesso'],[
 ('autobudget_backend','2/2','Máximo de uma réplica por nó'),
 ('autobudget_frontend','2/2','Aplicação publicada em 8080'),
 ('autobudget_monitor-proxy','1/1','Manager; API interna'),
 ('autobudget_visualizer','1/1','Manager; painel em 8081'),
],[4.3,1.7,6.02],y=3.2)
banner(s,'A contagem confirma tarefas disponíveis; valide a aplicação com uma requisição nova.')
note(s,'Fonte P03. Backend, frontend e monitor apontam para ghcr.io/kaykymatos845/auto-repair-*:v5. O Visualizer usa imagem dockersamples/visualizer fixada por digest. A publicação 8081 e as constraints vêm dos arquivos da stack; a captura de serviços mostra explicitamente a porta 8080 do frontend.')

s=base('Evidências P01 e P04','A distribuição muda com a escala','Síntese gráfica dos prints do Docker Visualizer; não substitui as imagens originais.')
for x,title,manager,worker in [(.65,'ESTADO INICIAL · 2 RÉPLICAS',['Frontend + Backend','Visualizer + Proxy'],['Frontend + Backend']), (6.82,'APÓS REDUÇÃO · 1 RÉPLICA',['Frontend','Visualizer + Proxy'],['Backend'])]:
    text(s,x,2.4,5.86,.4,title,17,TEAL,True)
    rect(s,x,3.0,5.86,2.75,WHITE,BORDER)
    text(s,x+.22,3.22,5.4,.3,'kayky · manager',20,INK,True)
    text(s,x+.22,3.73,5.4,.65,'\n'.join(manager),17,MUTED)
    text(s,x+.22,4.55,5.4,.3,'n2 · worker',20,INK,True)
    text(s,x+.22,5.06,5.4,.4,'\n'.join(worker),17,MUTED)
banner(s,'Frontend e backend podem executar em nós diferentes e se comunicar pela rede overlay.')
note(s,'Fonte P01: manager com os quatro serviços e worker com frontend/backend. Fonte P04: manager com frontend/Visualizer/proxy e worker apenas com backend. Não atribuir 1/1 ao output de docker stack services, que não foi fornecido nessa etapa; o Visualizer mostra uma tarefa por serviço.')

s=base('Evidência P05','Redução executada pela linha de comando','O print registra uma alteração imperativa no estado dos serviços do Swarm.')
code(s,.65,2.4,12.02,1.0,'docker service scale autobudget_backend=1 autobudget_frontend=1',19)
rect(s,.65,3.75,5.86,1.95,WHITE,BORDER)
text(s,.9,3.98,5.35,.4,'O que foi comprovado',22,TEAL,True)
text(s,.9,4.56,5.35,.85,'Redução 2 → 1 e resultado\nvisível no Visualizer.',21,INK)
rect(s,6.82,3.75,5.86,1.95,WHITE,BORDER)
text(s,7.07,3.98,5.35,.4,'O que falta pelo Compose',22,AMBER,True)
text(s,7.07,4.56,5.35,.85,'Registrar APP_REPLICAS aplicado\npelo script declarativo.',21,INK)
banner(s,'docker service scale não altera o YAML; o próximo deploy reaplica o valor do Compose.',True)
note(s,'P05 comprova o comando e P04 o resultado. Para o requisito de Compose, execute scripts/demo-replicas.sh ou APP_REPLICAS=1/2 bash scripts/deploy-swarm.sh com o worker Ready. Não use o script enquanto n2 estiver Down: o deploy exige dois nós Ready/Active. Ele termina com uma réplica: retorne a duas antes de repetir o teste de queda.')

s=base('Evidências P06 e P07','Worker desligado; manager permanece ativo','P07 mostra n2 Down. P06 mostra os quatro serviços executando no manager.')
node(s,.65,2.55,5.86,'kayky · manager','Ready / Active / Leader',['Frontend','Backend','Docker Visualizer','Monitor-proxy'])
node(s,6.82,2.55,5.86,'n2 · worker','Down / Active',[],down=True)
text(s,7.07,4.0,5.35,1.0,'O nó continua cadastrado,\nmas está indisponível.',21,MUTED)
banner(s,'Active no nó Down não indica que a VM está ligada; são campos com funções diferentes.')
note(s,'P07 mostra manager Ready Active Leader e worker Down Active. P06 mostra apenas uma tarefa de frontend e backend no manager. Esta síntese não determina as réplicas desejadas ou a sequência de agendamento. A atualização do backend muda entre prints, mas isso sozinho não comprova o momento da recriação.')

s=base('Interpretação do teste','O que a queda permite concluir','O Visualizer comprova o estado dos nós e tarefas; a continuidade exige teste da aplicação.')
rect(s,.65,2.45,5.86,3.25,WHITE,BORDER)
text(s,.9,2.72,5.35,.4,'Confirmado pelos prints',23,TEAL,True)
text(s,.9,3.4,5.35,1.95,'• Worker reconhecido como Down.\n• Manager permanece Leader.\n• Frontend e backend no manager.\n• Monitoramento continua ativo.',20,INK)
rect(s,6.82,2.45,5.86,3.25,WHITE,BORDER)
text(s,7.07,2.72,5.35,.4,'Ainda precisa de evidência',23,AMBER,True)
text(s,7.07,3.4,5.35,1.95,'• Estado das tarefas após a queda.\n• Análise e nó Down simultâneos.\n• Momento da recriação das tarefas.\n• Worker recuperado e serviços 2/2.',20,INK)
banner(s,'Não afirmar migração, zero interrupções ou redundância do controle com um único manager.',True)
note(s,'Se havia duas réplicas desejadas, o limite uma por nó deixa 1/2 durante a queda. Se havia uma, o Swarm pode recriar o backend no manager e voltar a 1/1; nesse cenário uma interrupção transitória é possível. Não sabemos qual cenário ocorreu sem contagem e cronologia. Uma tela já aberta não prova que o backend atendeu uma requisição depois da queda.')

s=base('Acervo de vídeos','Três gravações recebidas para a apresentação','V03: teste inicial. V01: teste após queda, segundo o autor. V02: terminal com n2 Down.')
video_rows=[
 ('V01','Chrome · Auto Repair','2026-11-08 22-42-24'),
 ('V02','Terminal · root@kayky','2026-11-08 22-47-18'),
 ('V03','Chrome · Auto Repair','2026-11-08 22-31-35')]
table(s,['Arquivo','Nome da gravação','Data/hora no nome'],video_rows,[1.3,5.3,5.42])
text(s,.85,5.48,11.6,.45,'V01: 52s. V02: 58s. V03: 2min22s. Todos incorporados ao PPTX.',18,MUTED)
banner(s,'As três gravações estão no arquivo; não dependem de links externos.',True)
note(s,'V01: Auto Repair — Vistorias e orçamentos - Google Chrome 2026-11-08 22-42-24.mp4. V02: root@kayky_ _home_kayky_auto-repair-budget-agent 2026-11-08 22-47-18.mp4. V03: Auto Repair — Vistorias e orçamentos - Google Chrome 2026-11-08 22-31-35.mp4. V03 foi extraído do ZIP de 29 MB e revisado visualmente em sequência de quadros a cada dois segundos, com capturas em resolução original. Duração 141,876 segundos, 1920x1140. O áudio é silencioso (pico -91 dB). Uma cópia H.264 de 1280x760/15 fps foi incorporada ao PPTX; o original foi preservado fora do Git. V01 e V02 também foram revisados visualmente após recebimento em ZIP; ver slides específicos.')

s=base('Roteiro de apresentação','Mostre o efeito antes de explicar o comando','Sequência sugerida; os tempos são estimativas para a fala, não durações dos vídeos.')
steps=[('00:00–00:30','Aplicação','Foto → análise → revisão do resultado.'),('00:30–01:10','Cluster','Dois nós Ready; serviços 2/2; Visualizer.'),('01:10–02:00','Escala','Redução e expansão; comparar os gráficos.'),('02:00–03:00','Falha','n2 Down; nova análise pelo IP do manager.'),('03:00–03:40','Recuperação','Ligar n2; aguardar Ready e serviços 2/2.')]
for i,(timing,title,body) in enumerate(steps):
    y=2.35+i*.72
    text(s,.65,y,1.8,.35,timing,17,TEAL,True)
    text(s,2.65,y,2.0,.4,title,20,INK,True)
    text(s,4.85,y,7.82,.45,body,18,MUTED)
banner(s,'Antes da queda: duas réplicas. Depois: análise nova. Ao final: worker recuperado.')
note(s,'Fala: Este é o Auto Repair. Cada serviço tem sua imagem. As duas VMs executam frontend e backend. Vamos variar as réplicas e observar o Visualizer. Agora desligamos somente n2; o manager detecta a falha. Uma nova requisição confirma se a aplicação atende. Por fim, ligamos o worker e observamos a recomposição. Não narre um teste como concluído antes de verificá-lo.')

s=base('Pendências de comprovação','O que falta para fechar a entrega','Itens objetivos para complementar a revisão e os registros já recebidos.')
table(s,['Prioridade','Registro necessário','Como obter'],[
 ('1','Recuperação do worker','n2 Ready + aplicação 2/2'),
 ('2','Escala aplicada pelo Compose','scripts/demo-replicas.sh + capturas'),
 ('3','Sincronismo do teste de falha','Análise + nó Down na mesma captura'),
 ('4','Detalhar contagem durante falha','docker service ps --no-trunc'),
],[1.2,5.0,5.82])
banner(s,'Vídeos revisados; falta sincronizar o teste de falha e mostrar a recuperação.',True)
note(s,'Ver docs/REVISAO_DEMONSTRACAO.md para comandos e lista de evidências. Requisitos estruturais: Dockerfiles próprios para três serviços e Visualizer oficial; Swarm em duas VMs; Compose define infraestrutura e réplica variável. Evidência de variação existe via CLI, mas falta execução do ciclo pelo Compose. Continuidade e recuperação são complementos importantes do teste, não requisitos extras inventados para o enunciado.')

# Original captures and full reviewed recording from the V03 archive.
video_section_start=len(prs.slides)
media=ROOT/'assets/demonstracao'
s=base('Vídeo V03 · teste inicial','Da foto à primeira sugestão revisável','Captura real do vídeo em 00:35; aplicação acessada pelo manager em 192.168.165.135:8080.')
s.shapes.add_picture(str(media/'v03-analise.jpg'), Inches(.65), Inches(2.22), width=Inches(6.7))
text(s,8.0,2.45,4.65,.4,'O que foi observado',22,TEAL,True)
text(s,8.0,3.05,4.65,2.6,'00:13 · Foto carregada.\n00:29 · Análise em execução.\n00:31 · Um item para revisão.\n00:33–00:37 · Região na foto.',20,INK)
banner(s,'A sugestão observada foi Porta. Um único teste não mede a precisão do detector.')
note(s,'Fonte: V03, gravação original 22-31-35 recebida em ZIP. Revisão visual de quadros a cada dois segundos: foto carregada, acionamento da análise e retorno de um item. Captura extraída em 35s, sem alterar o conteúdo. Não há terminal ou Visualizer nessa gravação: ela não comprova o estado dos nós nem continuidade após queda.')

s=base('Vídeo V03 · orçamento','Revisão humana e orçamento consolidado','Captura real em 02:07. Os valores são dados do teste, não cotações verificadas.')
s.shapes.add_picture(str(media/'v03-orcamento.jpg'), Inches(.65), Inches(2.22), width=Inches(6.7))
text(s,8.0,2.45,4.65,.4,'Resultado exibido',22,TEAL,True)
text(s,8.0,3.04,4.65,2.4,'Peças: R$ 2.525,00\nMão de obra: R$ 320,00\nTerceiros: R$ 200,00\nTotal: R$ 3.045,00',21,INK)
banner(s,'O vídeo mostra inclusão manual de peça, ajustes e prévia de impressão; não mostra PDF salvo.')
note(s,'V03: 00:39–01:13 cadastro manual de para-choque traseiro; 01:15–01:39 revisão e valores/horas; 01:41–02:03 inclusão de serviço de terceiros; 02:05–02:11 resumo; 02:13 prévia e 02:17–02:19 diálogo do navegador para imprimir. O diálogo é cancelado/fechado; não afirmar gravação de arquivo PDF ou envio por WhatsApp. A gravação não é narrada: trilha de áudio silenciosa.')

s=base('Vídeo V03 · reprodução','Primeiro teste completo da aplicação','Vídeo incorporado ao PowerPoint · 2min22s · sem narração · clicar para reproduzir.')
s.shapes.add_picture(str(media/'v03-analise.jpg'), Inches(2.88), Inches(2.12), width=Inches(7.2), height=Inches(4.275))
s.shapes.add_movie(str(media/'v03-inicial.mp4'), Inches(2.88), Inches(2.12), Inches(7.2), Inches(4.275),poster_frame_image=str(media/'v03-analise.jpg'),mime_type='video/mp4')
text(s,.85,6.55,11.65,.3,'No PDF, esta página é estática. Teste a reprodução no PowerPoint antes de apresentar.',14,MUTED)
note(s,'A cópia comprimida H.264/AAC está dentro do PPTX, sem depender de link externo. Original 1920x1140, duração 141,876s; cópia 1280x760 a 15 fps. Não houve cortes na duração. Revisão visual, sem fala a transcrever. Sugestão de fala: Este é o teste inicial, anterior à simulação da falha. A análise retorna uma sugestão; a pessoa revisa os itens, inclui o que falta e ajusta os custos antes de abrir a impressão.')

failure_section_start=len(prs.slides)
s=base('Vídeos V01 e V02 · teste de falha','Nova análise e worker indisponível','Evidências complementares em gravações separadas; não há uma tela simultânea das duas.')
s.shapes.add_picture(str(media/'v01-analise.jpg'), Inches(.65), Inches(2.35), width=Inches(6.0))
s.shapes.add_picture(str(media/'v02-terminal.jpg'), Inches(6.83), Inches(2.35), width=Inches(5.85))
text(s,.65,5.95,6.0,.3,'V01 · 00:21 · Um item retornado pela análise.',14,TEAL,True)
text(s,6.83,5.95,5.85,.3,'V02 · 00:25 · n2 Down; contagem exibe 2/2.',14,TEAL,True)
banner(s,'O autor identifica V01 como pós-queda; o vídeo do navegador não mostra o estado dos nós.')
note(s,'V01 (51,714s): foto carregada em cerca de 13s, análise em andamento em 17s, retorno de um item em 19–21s, revisão/custos e prévia de impressão até 51s. V02 (58,214s): watch de docker node ls e docker stack services; n2 Down e serviços da aplicação 2/2 nos quadros vistos. A contagem exibida não comprova duas tarefas saudáveis; não foi mostrado docker service ps para esclarecer. Não substituir o observado por 1/2. Não é possível provar sincronismo apenas pelos nomes/datas de gravações separadas.')

s=base('Vídeo V01 · reprodução','Aplicação no teste relatado após a queda','Gravação incorporada · 52 segundos · sem narração · clicar para reproduzir.')
s.shapes.add_picture(str(media/'v01-analise.jpg'), Inches(2.88), Inches(2.12), width=Inches(7.2), height=Inches(4.275))
s.shapes.add_movie(str(media/'v01.mp4'), Inches(2.88), Inches(2.12), Inches(7.2), Inches(4.275),poster_frame_image=str(media/'v01-analise.jpg'),mime_type='video/mp4')
text(s,.85,6.55,11.65,.3,'Mostra uma nova análise e orçamento. A associação à queda foi informada pelo autor.',14,MUTED)
note(s,'Fonte V01, arquivo 22-42-24. O endereço é o IP do manager na porta 8080. O navegador parte sem itens, carrega foto, aciona análise e recebe um resultado. Não há monitoramento dos nós no mesmo quadro. A demonstração deve apresentar V02/P07 como evidência complementar, sem prometer sincronismo, ausência de interrupções ou migração comprovada.')

s=base('Vídeo V02 · reprodução','Terminal durante a indisponibilidade do worker','Gravação incorporada · 58 segundos · sem narração · clicar para reproduzir.')
s.shapes.add_picture(str(media/'v02-terminal.jpg'), Inches(2.88), Inches(2.12), width=Inches(7.2), height=Inches(4.275))
s.shapes.add_movie(str(media/'v02.mp4'), Inches(2.88), Inches(2.12), Inches(7.2), Inches(4.275),poster_frame_image=str(media/'v02-terminal.jpg'),mime_type='video/mp4')
text(s,.85,6.55,11.65,.3,'n2 aparece Down. A contagem ainda mostra 2/2; verificar tarefas antes de afirmar convergência.',14,MUTED)
note(s,'V02, arquivo de terminal 22-47-18. Observado watch a cada dois segundos com n2 Down, kayky Ready/Active/Leader; backend e frontend 2/2; monitor-proxy e Visualizer 1/1. Isso registra o estado exibido, não garante que todas as tarefas respondem. Complemento sugerido no manager: docker stack ps --no-trunc autobudget e docker service ps --no-trunc autobudget_backend / autobudget_frontend, junto de curl ou nova análise.')

# Keep the original 20 slides and insert the evidence section before final audit/close.
added=list(prs.slides._sldIdLst)[20:video_section_start]
video_slides=list(prs.slides._sldIdLst)[video_section_start:failure_section_start]
failure_slides=list(prs.slides._sldIdLst)[failure_section_start:]
for element in original[:7]+video_slides+original[7:18]+added[:6]+failure_slides+added[6:]+original[18:]:
    prs.slides._sldIdLst.append(element)
for i,slide in enumerate(prs.slides,1):
    for shape in slide.shapes:
        if shape.has_text_frame and re.fullmatch(r'\d{2} / 20',shape.text):
            shape.text_frame.paragraphs[0].runs[0].text=f'{i:02d} / {len(prs.slides):02d}'
            break
    else:
        text(slide,11.6,7.12,1.1,.25,f'{i:02d} / {len(prs.slides):02d}',11,MUTED,align=PP_ALIGN.RIGHT)
prs.core_properties.title='Auto Repair — apresentação e evidências da demonstração'
prs.core_properties.subject='Base ampliada com evidências de Swarm e três vídeos incorporados'

# Replace synthesis-only layouts with the six original photographs from the ZIP.
def find_title(value):
    return next(slide for slide in prs.slides if any(sh.has_text_frame and sh.text==value for sh in slide.shapes))

def clear_body(slide):
    for sh in list(slide.shapes):
        if Inches(1.95) < sh.top < Inches(7.0):
            element=sh._element;element.getparent().remove(element)

def set_subtitle(slide,value):
    for sh in slide.shapes:
        if sh.has_text_frame and Inches(1.65)<sh.top<Inches(1.95):
            sh.text_frame.paragraphs[0].runs[0].text=value

s=find_title('Dois nós prontos no início');clear_body(s)
set_subtitle(s,'Print original P02 recebido em ZIP; identidades distintas de manager e worker.')
s.shapes.add_picture(str(media/'p02-node-ready.png'), Inches(.65), Inches(2.45), width=Inches(12.02))
for x,title,body in [(.65,'kayky · manager','Ready / Active / Leader'),(6.83,'n2 · worker','Ready / Active')]:
    rect(s,x,4.0,5.85,1.6,WHITE,BORDER);text(s,x+.25,4.28,5.35,.4,title,24,TEAL,True);text(s,x+.25,4.92,5.35,.4,body,22,INK)
banner(s,'Docker Engine 29.9.2 nos dois nós; estado inicial do cluster.')

s=find_title('Serviços convergidos antes do teste');clear_body(s)
set_subtitle(s,'Print original P03: docker stack services autobudget, antes da simulação de falha.')
s.shapes.add_picture(str(media/'p03-services.png'), Inches(.65), Inches(2.4), width=Inches(12.02))
for x,title,body in [(.65,'Aplicação · 2/2','Frontend e backend distribuídos.'),(6.83,'Monitoramento · 1/1','Visualizer e proxy no manager.')]:
    rect(s,x,4.25,5.85,1.35,WHITE,BORDER);text(s,x+.25,4.45,5.35,.4,title,24,TEAL,True);text(s,x+.25,5.02,5.35,.4,body,19,INK)
banner(s,'Imagens próprias v5 no GHCR; frontend publicado na porta 8080.')

s=find_title('A distribuição muda com a escala');clear_body(s)
set_subtitle(s,'Print original P04 após a redução: frontend no manager e backend no worker.')
s.shapes.add_picture(str(media/'p04-visualizer-scale.png'), Inches(.65), Inches(2.24), width=Inches(6.5))
text(s,7.55,2.6,5.1,.4,'Uma réplica por serviço',24,TEAL,True)
text(s,7.55,3.35,5.1,2.3,'Manager: frontend e monitoramento.\nWorker: backend.\nComunicação entre serviços pela rede overlay.',21,INK)
banner(s,'A redução está documentada pelo comando P05 e pelo resultado no Visualizer P04.')

s=find_title('Redução executada pela linha de comando')
for sh in list(s.shapes):
    if sh.has_text_frame and sh.text=='docker service scale autobudget_backend=1 autobudget_frontend=1':
        element=sh._element;element.getparent().remove(element)
s.shapes.add_picture(str(media/'p05-scale-command.png'), Inches(.8), Inches(2.72), width=Inches(11.72))

s=find_title('Worker desligado; manager permanece ativo');clear_body(s)
set_subtitle(s,'Prints originais P06 e P07: Visualizer em vermelho e n2 Down no terminal.')
s.shapes.add_picture(str(media/'p06-visualizer-down.png'), Inches(.65), Inches(2.3), width=Inches(6.0))
s.shapes.add_picture(str(media/'p07-node-down.png'), Inches(6.9), Inches(2.7), width=Inches(5.77))
text(s,6.9,3.7,5.77,1.9,'Manager permanece Leader.\nWorker aparece Down.\nFrontend e backend aparecem no manager.',22,INK)
banner(s,'P06 mostra as tarefas remanescentes; V01 registra a análise relatada após a queda.')

args.output.parent.mkdir(parents=True,exist_ok=True)
prs.save(args.output)
print(f'Created {args.output}: {len(prs.slides)} slides')
