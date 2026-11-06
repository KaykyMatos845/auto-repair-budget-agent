"""Generate the editable course deck. Optional dependency: python-pptx."""
from pathlib import Path
import argparse
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

BG='F3F6F8'; NAVY='102F3B'; TEAL='0B786C'; MINT='92DFC4'; INK='183440'; MUTED='607582'; BORDER='DCE6EA'; WHITE='FFFFFF'; SOFT='E6F2ED'
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
prs.core_properties.title='Auto Repair — Docker, Compose e Swarm'
prs.core_properties.subject='Apresentação acadêmica: Dockerfiles, duas VMs, Visualizer e escala de réplicas'
prs.core_properties.author='Auto Repair'
prs.core_properties.keywords='Auto Repair, Docker, Compose, Swarm, Visualizer'


def box(s,x,y,w,h,fill=WHITE,border=None,radius=True):
 sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
 sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(fill)
 if border:sh.line.color.rgb=RGBColor.from_string(border);sh.line.width=Pt(1)
 else:sh.line.fill.background()
 if radius:sh.adjustments[0]=.12
 return sh


def txt(s,x,y,w,h,content,size=20,color=INK,bold=False,font='Arial',align=PP_ALIGN.LEFT):
 sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame
 tf.word_wrap=True;tf.margin_left=tf.margin_right=0;tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(content.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.alignment=align;p.space_after=Pt(7)
  p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color)
 return sh


def line(s,x1,y1,x2,y2,color=BORDER,width=1):
 sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2));sh.line.color.rgb=RGBColor.from_string(color);sh.line.width=Pt(width)


def base(n,chapter,title):
 s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor.from_string(BG)
 txt(s,.65,.4,11,.3,chapter.upper(),12,TEAL,True);txt(s,.65,.95,12,1,title,34,INK,True)
 line(s,.65,7.03,12.68,7.03);txt(s,.65,7.14,10,.2,'AUTO REPAIR  /  DOCKER & SWARM',9,MUTED);txt(s,11.6,7.12,1.1,.25,f'{n:02d} / 08',11,MUTED,align=PP_ALIGN.RIGHT)
 return s


def notes(s,text):s.notes_slide.notes_text_frame.text=text


def tag(s,x,y,w,text,fill=SOFT,color=TEAL):
 box(s,x,y,w,.38,fill);txt(s,x+.12,y+.07,w-.24,.22,text,11,color,True)


def card(s,x,y,w,h,number,title,body):
 box(s,x,y,w,h,WHITE,BORDER);tag(s,x+.22,y+.22,.48,number);txt(s,x+.86,y+.19,w-1.1,.45,title,22,INK,True);txt(s,x+.24,y+.82,w-.48,h-.92,body,16.5,MUTED)


def code(s,x,y,w,h,text,size=18):
 box(s,x,y,w,h,NAVY);txt(s,x+.25,y+.2,w-.5,h-.35,text,size,MINT,font='Consolas')

# 1 — opening
s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor.from_string(NAVY)
box(s,.8,.7,.65,.65,TEAL);txt(s,.88,.86,.5,.25,'AR',18,WHITE,True)
txt(s,1.65,.88,7,.35,'PROJETO ACADÊMICO  ·  CONTAINERS E ORQUESTRAÇÃO',12,MINT,True)
txt(s,.8,2.05,7.9,1.05,'Auto Repair',60,WHITE,True)
txt(s,.85,3.25,6.9,1.25,'Vistoria por fotos e orçamento de reparos,\ncom análise local e revisão humana.',25,'D3E4E8')
for x,w,label in [(.85,1.7,'CPU LOCAL'),(2.75,2.4,'DOCKER COMPOSE'),(5.35,2.6,'SWARM + VISUALIZER')]:tag(s,x,5.25,w,label,'214551',MINT)
for y,title,body in [(2.05,'FRONTEND','React + Nginx'),(3.2,'BACKEND','Python + ONNX'),(4.35,'CLUSTER','2 VMs Ubuntu')]:
 box(s,9.2,y,3.25,.9,'214551','40656E');txt(s,9.45,y+.14,2.8,.25,title,12,MINT,True);txt(s,9.45,y+.48,2.8,.3,body,18,WHITE)
line(s,10.8,2.95,10.8,3.2,MINT,2);line(s,10.8,4.1,10.8,4.35,MINT,2)
txt(s,.85,6.85,11,.3,'Dockerfiles  /  Infraestrutura como código  /  Demonstração de réplicas',13,'A9C1CB')
notes(s,'Apresente o Auto Repair como uma aplicação de apoio à vistoria. O modelo sugere regiões suspeitas e não substitui inspeção presencial. O foco acadêmico inclui imagens próprias, Swarm em duas VMs e representação gráfica pelo Docker Visualizer.')

# 2 — images
s=base(2,'Imagens e serviços','Cada serviço tem uma responsabilidade')
card(s,.65,2.0,5.86,1.85,'01','Frontend','React compilado em múltiplas etapas.\nNginx sem root, servindo a aplicação na porta 8080.')
card(s,6.8,2.0,5.86,1.85,'02','Backend','Python, ONNX Runtime e pesos verificados.\nAnálise local em CPU, sem API externa de IA.')
card(s,.65,4.08,5.86,1.85,'03','Proxy de monitoramento','Consultas específicas à API Docker.\nA porta 2375 não é publicada no host.')
card(s,6.8,4.08,5.86,1.85,'04','Docker Visualizer','Imagem dockersamples/visualizer, fixada por digest.\nExecução no manager, com acesso pelo proxy.')
code(s,.65,6.18,12.02,.6,'bash scripts/build-images.sh --push',16)
notes(s,'Mostre Dockerfile.frontend, Dockerfile.backend e Dockerfile.monitor. O Visualizer usa a imagem de exemplo indicada no Compose, não uma implementação própria. Antes do build, defina BACKEND_IMAGE, FRONTEND_IMAGE e MONITOR_IMAGE em seu registro HTTPS e faça login. Nenhuma imagem foi publicada automaticamente por esta apresentação.')

# 3 — architecture
s=base(3,'Topologia do cluster','Duas VMs, uma rede de aplicação')
for x,role,ip in [(.65,'MANAGER','192.168.165.135'),(6.85,'WORKER','192.168.165.140')]:
 box(s,x,1.95,5.82,3.55,WHITE,BORDER);txt(s,x+.28,2.2,5.2,.4,role,23,TEAL,True);txt(s,x+.28,2.72,5.2,.3,ip,18,MUTED)
 for dx,label in [(.28,'Frontend'),(3.02,'Backend')]:
  box(s,x+dx,3.35,2.5,.65,SOFT);txt(s,x+dx,3.51,2.5,.35,label,19,TEAL,True,align=PP_ALIGN.CENTER)
 if role=='MANAGER':
  for dx,label in [(.28,'Visualizer'),(3.02,'Proxy Docker')]:
   box(s,x+dx,4.3,2.5,.65,NAVY);txt(s,x+dx,4.47,2.5,.3,label,18,WHITE,align=PP_ALIGN.CENTER)
 else:txt(s,x+.28,4.4,5.1,.65,'Executa tarefas distribuídas\nconforme o estado desejado.',18,MUTED)
line(s,6.47,3.67,6.85,3.67,TEAL,3)
box(s,.65,5.87,12.02,.63,SOFT);txt(s,.9,6.04,11.5,.3,'Rede overlay  ·  Aplicação: 8080  ·  Visualizer no manager: 8081',18,TEAL,True)
txt(s,.65,6.65,12,.24,'Um único manager não oferece alta disponibilidade do controle do cluster.',13,MUTED)
notes(s,'Os IPs foram informados pelo usuário: manager 192.168.165.135 e worker 192.168.165.140. O cluster foi relatado como formado. Confirme docker node ls ao apresentar. Cada serviço da aplicação tem no máximo uma réplica por nó. A perda de um nó pode deixar tarefas pendentes; não prometa migração ilimitada ou alta disponibilidade do controle com um só manager.')

# 4 — declarative
s=base(4,'Infraestrutura como código','Compose declara o estado desejado')
code(s,.65,2.05,6.05,3.1,'deploy:\n  replicas: ${APP_REPLICAS:-2}\n  placement:\n    max_replicas_per_node: 1',21)
txt(s,7.13,2.08,5.45,.45,'Arquivos da infraestrutura',23,INK,True)
for y,title,body in [(2.85,'docker-compose.yml','Frontend, backend e rede overlay.'),(3.95,'docker-compose.demo.yml','Visualizer e proxy no manager.'),(5.05,'compose.ubuntu.yml','Alternativa para um único Ubuntu.')]:
 txt(s,7.13,y,5.45,.32,title,17,TEAL,True);txt(s,7.13,y+.4,5.45,.5,body,18,MUTED)
box(s,.65,5.55,6.05,1.05,WHITE,BORDER);txt(s,.92,5.77,5.52,.65,'Healthchecks, limites de recursos,\natualização gradual e rollback.',18,INK)
notes(s,'Mostre a variável APP_REPLICAS no Compose e a restrição max_replicas_per_node. O script de demonstração reaplica o Compose com valores 1, 2 e 1. Diferencie Compose em um único host da implantação Swarm feita com docker stack deploy. O deploy espera convergência e verifica a API antes de concluir.')

# 5 — monitoring flow
s=base(5,'Monitoramento gráfico','O Visualizer consulta; o proxy filtra')
for x,title,body in [(.65,'VISUALIZER','Gráfico dos nós\ne das tarefas'),(4.8,'PROXY','Somente consultas\nem rotas permitidas'),(8.95,'DOCKER','Estado real\ndo manager')]:
 box(s,x,2.15,3.73,1.6,WHITE,BORDER);txt(s,x+.2,2.43,3.33,.4,title,21,TEAL,True,align=PP_ALIGN.CENTER);txt(s,x+.2,2.95,3.33,.7,body,17,MUTED,align=PP_ALIGN.CENTER)
for x in [4.4,8.55]:txt(s,x,2.64,.38,.6,'→',25,TEAL,True,align=PP_ALIGN.CENTER)
card(s,.65,4.15,5.86,1.65,'✓','Consultas permitidas','Nós, serviços e tarefas do cluster.\nAs respostas alimentam o gráfico do Visualizer.')
card(s,6.8,4.15,5.86,1.65,'×','Alterações bloqueadas','POST, PUT, PATCH e DELETE são bloqueados.\nO dashboard não recebe o socket real.')
txt(s,.65,6.15,12,.5,'Socket montado com :ro, sozinho, não limita a API a leitura.\nO painel de exemplo deve ficar na rede privada ou ser acessado por túnel SSH.',15,MUTED)
notes(s,'Abra http://192.168.165.135:8081. O Visualizer faz requisições, o proxy consulta o socket local e devolve os dados. Somente o proxy recebe /var/run/docker.sock. O filtro permite GET em endpoints explícitos e não publica a porta do proxy. A imagem Visualizer é um exemplo acadêmico antigo, sem autenticação; não a publique livremente na internet.')

# 6 — scale
s=base(6,'Demonstração de escala','Uma mudança declarativa, três etapas')
for x,n,title in [(.65,'1','INÍCIO'),(4.8,'2','EXPANSÃO'),(8.95,'1','REDUÇÃO')]:
 box(s,x,2.0,3.73,2.55,WHITE,BORDER);txt(s,x+.2,2.24,3.33,.3,title,13,TEAL,True,align=PP_ALIGN.CENTER);txt(s,x+.2,2.76,3.33,.95,n,57,INK,True,align=PP_ALIGN.CENTER);txt(s,x+.2,3.85,3.33,.4,'réplica(s) de cada serviço',16,MUTED,align=PP_ALIGN.CENTER)
for x in [4.4,8.55]:txt(s,x,2.96,.38,.6,'→',25,TEAL,True,align=PP_ALIGN.CENTER)
code(s,.65,4.95,12.02,.75,'bash scripts/demo-replicas.sh',22)
txt(s,.65,6.02,12,.6,'Frontend e backend variam juntos. Visualizer e proxy permanecem em uma réplica.\nEm cada pausa, capture o gráfico real antes de continuar.',18,MUTED)
notes(s,'Esta figura apresenta o roteiro, não resultados já executados. Na manager, após configurar as três imagens do registro, execute scripts/demo-replicas.sh. Aguarde cada etapa e capture o Visualizer. O roteiro termina com uma réplica; para retornar a duas, execute APP_REPLICAS=2 bash scripts/deploy-swarm.sh. Com duas VMs e uma réplica por nó, três réplicas deixariam uma pendente.')

# 7 — evidence
s=base(7,'Evidências da apresentação','Mostrar o cluster, não apenas os arquivos')
code(s,.65,2.0,6.05,2.1,'docker node ls\ndocker stack services autobudget\ndocker stack ps --no-trunc autobudget',17)
box(s,.65,4.4,6.05,1.75,WHITE,BORDER);txt(s,.92,4.67,5.5,.4,'Saídas reais salvas pelo roteiro',20,TEAL,True);txt(s,.92,5.23,5.5,.6,'artifacts/swarm-demo/\nCapturas do Visualizer: uma por etapa.',18,MUTED)
for y,num,title,body in [(2.0,'01','Dois nós','Manager e worker Ready/Active.'),(3.35,'02','Réplicas convergidas','Aplicação em 1/1, depois 2/2 e novamente 1/1.'),(4.7,'03','Execução da aplicação','Foto analisada, revisão humana e orçamento.')]:
 tag(s,7.15,y,.5,num);txt(s,7.9,y,4.6,.35,title,20,INK,True);txt(s,7.9,y+.47,4.6,.65,body,18,MUTED)
txt(s,.65,6.5,12,.3,'Os identificadores técnicos autobudget_* foram preservados para compatibilidade.',13,MUTED)
notes(s,'Não apresente saídas de testes unitários ou mocks como prova do cluster. Colete docker node ls, serviços e tarefas no manager. A pasta artifacts contém as saídas geradas na demonstração; as capturas do Visualizer precisam ser feitas manualmente. O prefixo técnico legado foi mantido para evitar criar uma segunda stack e perder compatibilidade. A marca exibida é Auto Repair.')

# 8 — close
s=base(8,'Encerramento','Infraestrutura verificável. Revisão humana.')
card(s,.65,2.0,5.86,2.0,'01','Aplicação','Sugestões de regiões suspeitas.\nPeça, preço, horas e decisão de reparo\nprecisam de revisão.')
card(s,6.8,2.0,5.86,2.0,'02','Cluster','Um manager + um worker.\nHistórico no navegador, sem banco\ncompartilhado ou login na aplicação.')
box(s,.65,4.3,12.02,1.6,NAVY)
txt(s,.95,4.58,11.4,.35,'ENDEREÇOS DA DEMONSTRAÇÃO',12,MINT,True)
txt(s,.95,5.08,5.6,.45,'Aplicação · 192.168.165.135:8080',18,WHITE)
txt(s,6.65,5.08,5.5,.45,'Visualizer · 192.168.165.135:8081',18,WHITE)
txt(s,.65,6.19,12,.5,'Roteiro: docs/DEMONSTRACAO.md\nConclua a comprovação com registros e capturas coletados nas duas VMs.',16,MUTED)
notes(s,'Finalize retomando os requisitos: Dockerfiles, Compose, Swarm em VMs, variação de réplicas e imagem Docker Visualizer. A configuração está preparada; só afirme resultados da execução após verificá-los nas VMs. O detector não confirma segurança para circulação nem danos internos. A apresentação é editável e os diagramas são formas nativas do PowerPoint.')

parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(Path(__file__).resolve().parents[1]/'public/auto-repair-apresentacao.pptx'));args=parser.parse_args()
output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True);prs.save(output)
print(f'Created: {output} ({len(prs.slides)} editable slides)')
