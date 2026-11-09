"""Build the audience deck, without presenter checklists or coaching screens.

Retains the reviewed technical material and embeds only the edited V05 footage.
The review deck and original uploads remain separate from this delivery.
"""
from pathlib import Path
import argparse
import re
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=ROOT/'public/auto-repair-apresentacao-final.pptx')
args=parser.parse_args()
prs=Presentation(ROOT/'public/auto-repair-apresentacao-demonstracao.pptx')
MEDIA=ROOT/'assets/demonstracao'
NAVY='102F3B';TEAL='0B786C';INK='183440';MUTED='607582';BG='F3F6F8';SOFT='E6F2ED'


def text(slide,x,y,w,h,value,size=20,color=INK,bold=False):
    shape=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame=shape.text_frame;frame.word_wrap=True
    frame.margin_left=frame.margin_right=frame.margin_top=frame.margin_bottom=0
    for i,line in enumerate(value.split('\n')):
        p=frame.paragraphs[0] if i==0 else frame.add_paragraph()
        p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(6)
    return shape


def rect(slide,x,y,w,h,color):
    shape=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid();shape.fill.fore_color.rgb=RGBColor.from_string(color);shape.line.fill.background();shape.adjustments[0]=.1


def find(title):
    return next(s for s in prs.slides if any(sh.has_text_frame and sh.text==title for sh in s.shapes))


def replace(slide,old,new):
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text==old:
            frame=shape.text_frame;p=frame.paragraphs[0]
            if p.runs:
                p.runs[0].text=new
                for run in list(p.runs)[1:]:run.text=''
                for extra in list(frame.paragraphs)[1:]:extra._p.getparent().remove(extra._p)
            else:shape.text=new
            return
    raise ValueError('Missing expected slide text: '+old)


# Delete the slide and its relationship so unused coaching parts are not packaged.
remove_titles={
 'Mostrar o cluster, não apenas os arquivos',
 'Dos arquivos à execução nas duas VMs',
 'Quatro gravações incorporadas à apresentação',
 'Mostre o efeito antes de explicar o comando',
 'O que falta para fechar a entrega',
}
for title in remove_titles:
    slide=find(title)
    element=next(e for e in prs.slides._sldIdLst if int(e.id)==slide.slide_id)
    prs.part.drop_rel(element.rId);prs.slides._sldIdLst.remove(element)

# Replace the planned cycle with the reduction actually present in the footage.
slide=find('Roteiro declarativo para variar réplicas')
replace(slide,'Roteiro declarativo para variar réplicas','Escala declarativa com Docker Compose')
for shape in list(slide.shapes):
    if Inches(1.9)<shape.top<Inches(7.0):
        node=shape._element;node.getparent().remove(node)
for x,title,filename,body in [
 (.65,'2 RÉPLICAS POR SERVIÇO','v05-duas-replicas.jpg','Frontend e backend presentes nos dois nós.'),
 (6.83,'1 RÉPLICA POR SERVIÇO','v05-uma-replica.jpg','Uma tarefa de frontend e uma de backend no manager.'),
]:
    text(slide,x,2.05,5.85,.35,title,18,TEAL,True)
    slide.shapes.add_picture(str(MEDIA/filename), Inches(x), Inches(2.65),width=Inches(5.85))
    text(slide,x,5.0,5.85,.8,body,19,MUTED)
rect(slide,.65,6.18,12.02,.62,SOFT)
text(slide,.88,6.35,11.5,.35,'O Compose aplica uma réplica; o Visualizer exibe a redução de 2 → 1.',17,TEAL,True)
scale_slide_id=slide.slide_id

slide=find('Redução executada pela linha de comando')
replace(slide,'O que falta pelo Compose','Escala pelo Compose')
replace(slide,'Registrar APP_REPLICAS aplicado\npelo script declarativo.','Configuração declarativa aplicada\nno vídeo de execução.')

slide=find('O que a queda permite concluir')
replace(slide,'O que a queda permite concluir','Resiliência e limites do cluster')
replace(slide,'O Visualizer comprova o estado dos nós e tarefas; a continuidade exige teste da aplicação.','Os registros mostram a falha do worker e a execução da aplicação em gravações separadas.')
replace(slide,'Ainda precisa de evidência','Escopo dos registros')
replace(slide,'• Estado das tarefas após a queda.\n• Análise e nó Down simultâneos.\n• Momento da recriação das tarefas.\n• Worker recuperado e serviços 2/2.','• Telas gravadas separadamente.\n• Nova análise registrada.\n• Tempo de indisponibilidade não medido.\n• Um único manager no controle.')
replace(slide,'Não afirmar migração, zero interrupções ou redundância do controle com um único manager.','O controle depende de um manager; a demonstração não mede o tempo de indisponibilidade.')

slide=find('Primeiro teste completo da aplicação')
replace(slide,'No PDF, esta página é estática. Teste a reprodução no PowerPoint antes de apresentar.','Foto, análise, revisão dos itens e orçamento demonstrados na aplicação.')
slide=find('Terminal durante a indisponibilidade do worker')
replace(slide,'n2 aparece Down. A contagem ainda mostra 2/2; verificar tarefas antes de afirmar convergência.','O registro mostra n2 Down e contagem 2/2; a contagem não comprova duas tarefas saudáveis.')

slide=find('O que comprova cada parte do trabalho')
replace(slide,'O que comprova cada parte do trabalho','Dockerfiles, Swarm e Compose na prática')
replace(slide,'Compose configurado; redução 2 → 1 registrada via CLI.','Estado declarativo aplicado; redução 2 → 1 registrada no Visualizer.')
replace(slide,'As próximas evidências distinguem resultados observados e registros ainda pendentes.','Imagens próprias, duas VMs, escala de serviços e representação gráfica da execução.')
slide=find('Infraestrutura verificável. Revisão humana.')
replace(slide,'Demonstração: cluster, escala e falha do worker registrados em prints.\nQuatro vídeos revisados e incorporados. Falta registrar a recuperação.','Análise local em CPU e orçamento com revisão humana.\nInfraestrutura em duas VMs com Docker Compose e Swarm.')

# New playback slide: the coaching recording is deliberately never referenced.
new=prs.slides.add_slide(prs.slide_layouts[6]);new.background.fill.solid();new.background.fill.fore_color.rgb=RGBColor.from_string(BG)
text(new,.65,.4,12,.3,'DEMONSTRAÇÃO · COMPOSE E VISUALIZER',12,TEAL,True)
text(new,.65,.95,12,.8,'Aplicação da escala e distribuição dos containers',30,INK,True)
text(new,.65,1.72,12,.35,'Registro editado · 43 segundos · execução do Compose e atualização do painel.',15,MUTED)
new.shapes.add_picture(str(MEDIA/'v05-poster.jpg'), Inches(2.25), Inches(2.3), width=Inches(8.8),height=Inches(4.95))
new.shapes.add_movie(str(ROOT/'public/auto-repair-demonstracao-editada.mp4'), Inches(2.25), Inches(2.3), Inches(8.8), Inches(4.95),poster_frame_image=str(MEDIA/'v05-poster.jpg'),mime_type='video/mp4')
# Keep video above the common footer.
for shape in list(new.shapes)[-2:]:
    shape.top=Inches(2.25);shape.width=Inches(7.8);shape.height=Inches(4.3875);shape.left=Inches(2.77)
text(new,.65,7.14,10,.2,'AUTO REPAIR  /  DOCKER & SWARM',9,MUTED)
ids=prs.slides._sldIdLst
new_id=next(e for e in ids if int(e.id)==new.slide_id)
ids.remove(new_id)
position=next(i for i,e in enumerate(ids) if int(e.id)==scale_slide_id)
ids.insert(position+1,new_id)

# Audience copy has no internal scripts/checklists hidden in speaker notes.
for number,slide in enumerate(prs.slides,1):
    slide.notes_slide.notes_text_frame.text=''
    for shape in slide.shapes:
        if shape.has_text_frame and re.fullmatch(r'\d{2} / \d{2}',shape.text):
            shape.text_frame.paragraphs[0].runs[0].text=f'{number:02d} / {len(prs.slides):02d}'
            break
    else:
        text(slide,11.6,7.12,1.1,.25,f'{number:02d} / {len(prs.slides):02d}',11,MUTED)
new.notes_slide.notes_text_frame.text='Registro editado composto por trechos de duas gravações. Comando e saídas preservados; barras do navegador, trocas de janela e a gravação de orientações foram excluídos. A evidência observada mostra aplicação de uma réplica e Visualizer de 2 para 1. Não representa teste contínuo de falha nem ciclo completo de 1 para 2 para 1.'
prs.core_properties.title='Auto Repair — apresentação final'
prs.core_properties.subject='Aplicação local, Dockerfiles, Compose e Swarm em duas VMs'
prs.core_properties.comments='Versão para apresentação; fontes e detalhes da edição em documentação separada.'
args.output.parent.mkdir(parents=True,exist_ok=True);prs.save(args.output)
print(f'{args.output}: {len(prs.slides)} slides')
