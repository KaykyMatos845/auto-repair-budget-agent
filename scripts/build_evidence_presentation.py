"""Extend the 20-slide deck using evidence visible in the project conversation.

No chat screenshot is fabricated: tables and diagrams explicitly identify themselves
as transcriptions/syntheses. Video review is pending because uploads exceed 32 MiB.
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
replace(prs.slides[19],'Roteiro: docs/DEMONSTRACAO.md\nConclua a comprovação com registros e capturas coletados nas duas VMs.','Demonstração: cluster, escala e falha do worker registrados em prints.\nFalta concluir a revisão dos vídeos e registrar a recuperação.')
for idx in [15,17,18,19]:
    note(prs.slides[idx], prs.slides[idx].notes_slide.notes_text_frame.text + '\nREVISÃO: os prints do chat confirmam redução via CLI e worker Down. Não foi comprovado o ciclo declarativo completo, a análise nova após a queda ou a recuperação. Vídeos recebidos ainda não acessíveis por limite de transferência de 32 MiB por arquivo.')

s=base('Demonstração real','Dos arquivos à execução nas duas VMs','Índice das evidências visíveis na conversa; sem inferir o conteúdo dos vídeos.')
table(s,['Etapa','Evidência','Situação'],[
 ('Cluster inicial','P01 + P02 + P03','Dois nós; serviços 2/2'),
 ('Redução de réplicas','P04 + P05','Uma réplica por serviço'),
 ('Queda do worker','P06 + P07','n2 Down; tarefas no manager'),
 ('Análise e recuperação','V01–V03 / nova captura','Revisão pendente'),
], [3.0,3.5,5.52])
banner(s,'P01–P07: prints vistos no chat. Diagramas e tabelas a seguir são sínteses, não capturas.')
note(s,'Ordem das fontes: P01 Visualizer inicial; P02 docker node ls inicial; P03 docker stack services inicial; P04 Visualizer com uma réplica; P05 comando docker service scale; P06 Visualizer após desligar n2; P07 docker node ls com n2 Down. As imagens originais não estão disponíveis como arquivos para incorporação. Não reconstruir uma falsa captura de terminal.')

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
text(s,7.07,3.4,5.35,1.95,'• Contagem 1/1 ou 1/2 na queda.\n• Uma análise nova concluída.\n• Momento da recriação das tarefas.\n• Worker recuperado e serviços 2/2.',20,INK)
banner(s,'Não afirmar migração, zero interrupções ou redundância do controle com um único manager.',True)
note(s,'Se havia duas réplicas desejadas, o limite uma por nó deixa 1/2 durante a queda. Se havia uma, o Swarm pode recriar o backend no manager e voltar a 1/1; nesse cenário uma interrupção transitória é possível. Não sabemos qual cenário ocorreu sem contagem e cronologia. Uma tela já aberta não prova que o backend atendeu uma requisição depois da queda.')

s=base('Acervo de vídeos','Três gravações recebidas para a apresentação','Arquivos recebidos no chat; conteúdo ainda não revisado nem incorporado ao PPTX.')
video_rows=[
 ('V01','Chrome · Auto Repair','2026-11-08 22-42-24'),
 ('V02','Terminal · root@kayky','2026-11-08 22-47-18'),
 ('V03','Chrome · Auto Repair','2026-11-08 22-31-35')]
table(s,['Arquivo','Nome da gravação','Data/hora no nome'],video_rows,[1.3,5.3,5.42])
text(s,.85,5.48,11.6,.45,'Cada anexo excede o limite de transferência de 32 MiB desta ferramenta.',18,MUTED)
banner(s,'Reenviar trechos de até 32 MB permite revisar e inserir as gravações nos slides.',True)
note(s,'V01: Auto Repair — Vistorias e orçamentos - Google Chrome 2026-11-08 22-42-24.mp4. V02: root@kayky_ _home_kayky_auto-repair-budget-agent 2026-11-08 22-47-18.mp4. V03: Auto Repair — Vistorias e orçamentos - Google Chrome 2026-11-08 22-31-35.mp4. Os três downloads falharam explicitamente por exceder 32 MiB. Os nomes não comprovam qual etapa foi gravada. Não há hyperlinks externos que substituam os arquivos nem vídeos ocultos nesta versão.')

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
 ('1','Vídeos acessíveis e prints originais','MP4 ≤32 MB; PNG/JPG anexados'),
 ('2','Escala aplicada pelo Compose','scripts/demo-replicas.sh + capturas'),
 ('3','Aplicação após worker Down','Análise nova + contagem de serviços'),
 ('4','Retorno do worker','n2 Ready + serviços 2/2 + gráfico'),
],[1.2,5.0,5.82])
banner(s,'A infraestrutura está demonstrada em prints; a revisão dos vídeos ainda está pendente.',True)
note(s,'Ver docs/REVISAO_DEMONSTRACAO.md para comandos e lista de evidências. Requisitos estruturais: Dockerfiles próprios para três serviços e Visualizer oficial; Swarm em duas VMs; Compose define infraestrutura e réplica variável. Evidência de variação existe via CLI, mas falta execução do ciclo pelo Compose. Continuidade e recuperação são complementos importantes do teste, não requisitos extras inventados para o enunciado.')

# Keep the original 20 slides and insert the evidence section before final audit/close.
added=list(prs.slides._sldIdLst)[20:]
for element in original[:18]+added+original[18:]:
    prs.slides._sldIdLst.append(element)
for i,slide in enumerate(prs.slides,1):
    for shape in slide.shapes:
        if shape.has_text_frame and re.fullmatch(r'\d{2} / 20',shape.text):
            shape.text_frame.paragraphs[0].runs[0].text=f'{i:02d} / {len(prs.slides):02d}'
            break
    else:
        text(slide,11.6,7.12,1.1,.25,f'{i:02d} / {len(prs.slides):02d}',11,MUTED,align=PP_ALIGN.RIGHT)
prs.core_properties.title='Auto Repair — apresentação e evidências da demonstração'
prs.core_properties.subject='Base de 20 slides ampliada com revisão das evidências; vídeos pendentes de acesso'

args.output.parent.mkdir(parents=True,exist_ok=True)
prs.save(args.output)
print(f'Created {args.output}: {len(prs.slides)} slides')
