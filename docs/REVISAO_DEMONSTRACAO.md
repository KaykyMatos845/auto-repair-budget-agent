# Revisão da apresentação e da demonstração — Auto Repair

Base: `public/auto-repair-apresentacao-20-slides.pptx` (20 slides).
Revisão: `public/auto-repair-apresentacao-demonstracao.pptx` (30 slides).
A base foi preservada, com ajustes nas afirmações sobre evidências já executadas.
Dez slides novos documentam os resultados observados e as pendências.

## Fontes disponíveis

Os prints estão visíveis na conversa, mas seus arquivos originais não estão no
workspace. As tabelas e figuras novas são **transcrições/sínteses explicitamente
identificadas**, não imagens originais nem novas execuções dos comandos.

| Fonte | Conteúdo observado | Conclusão permitida |
|---|---|---|
| P01 | Visualizer inicial: frontend/backend em ambos; Visualizer/proxy no manager | Distribuição inicial em dois nós |
| P02 | `docker node ls`: kayky Ready/Active/Leader; n2 Ready/Active | Cluster com manager e worker distintos; Engine 29.9.2 |
| P03 | `docker stack services autobudget`: aplicação 2/2; monitoramento 1/1 | Convergência inicial; imagens próprias v5 no GHCR |
| P04 | Visualizer reduzido: frontend no manager e backend no worker | Uma tarefa de cada serviço da aplicação |
| P05 | `docker service scale autobudget_backend=1 autobudget_frontend=1` | Redução solicitada pela CLI |
| P06 | Visualizer: n2 vermelho; frontend/backend/Visualizer/proxy no manager | Worker indisponível; tarefas da aplicação no manager |
| P07 | `docker node ls`: kayky Ready/Active/Leader; n2 Down/Active | O manager detectou a perda do worker |

`Availability=Active` não significa que o nó está ligado. O nó pode manter a
configuração de agendamento Active enquanto seu estado de comunicação é Down.

## Vídeos recebidos, ainda não revisados

Todos os downloads foram recusados pelo limite de transferência de **32 MiB por
arquivo**. Nenhum vídeo foi aberto, decodificado, transcrito ou incorporado ao
PPTX. Não é possível deduzir a sequência gravada ou o sucesso de uma análise pelo
nome do arquivo.

- V01: `Auto Repair — Vistorias e orçamentos - Google Chrome 2026-11-08 22-42-24.mp4`
- V02: `root@kayky_ _home_kayky_auto-repair-budget-agent 2026-11-08 22-47-18.mp4`
- V03: `Auto Repair — Vistorias e orçamentos - Google Chrome 2026-11-08 22-31-35.mp4`

Para concluir a revisão, reenviar os trechos em MP4 de até 32 MB cada e os prints
como anexos PNG/JPG. Preservar imagens legíveis e o encadeamento temporal do teste.
Não é necessário gravar tudo novamente antes de revisar o material existente.

## Conferência do enunciado

| Requisito | Implementação / evidência | Pendência de documentação |
|---|---|---|
| Dockerfiles dos serviços | Dockerfile.frontend, Dockerfile.backend, Dockerfile.monitor; Visualizer oficial por digest | Mostrar rapidamente os arquivos/estágios na gravação se ainda não constar dos vídeos |
| Swarm em VMs ou DinD | Duas VMs reais; manager e worker comprovados em P02 e P07 | Nenhuma terceira VM é necessária para este enunciado |
| Compose como infraestrutura como código | docker-compose.yml e docker-compose.demo.yml; APP_REPLICAS variável | Registrar aplicação da escala pelo Compose |
| Variação de réplicas | Estado 2/2 em P03, redução via CLI em P05 e resultado em P04 | Falta comprovar ciclo declarativo; não tratar CLI como alteração no YAML |
| Docker Visualizer | P01, P04 e P06 mostram estados distintos do cluster | Incorporar os prints originais quando fornecidos como arquivos |

A continuidade após falha e o retorno do worker complementam a demonstração;
não são requisitos adicionais impostos ao enunciado.

## O que os registros ainda não comprovam

1. **Contagem dos serviços durante a queda.** Falta `docker stack services
   autobudget` com n2 Down. O Visualizer mostra tarefas, não a quantidade desejada.
2. **Cronologia do agendamento.** Não há prova suficiente de que o backend já
   estava no manager antes da queda ou foi recriado ali depois.
3. **Nova análise concluída após a queda.** Uma página já aberta não comprova uma
   nova resposta do backend; verificar os vídeos antes de pedir outra gravação.
4. **Retorno do worker.** Falta n2 Ready/Active, aplicação 2/2 e Visualizer recuperado.
5. **Escala declarativa executada.** Os prints documentam `docker service scale`,
   que não altera os arquivos Compose. O roteiro 1 → 2 → 1 ainda não foi comprovado.

Com duas réplicas desejadas e `max_replicas_per_node: 1`, a queda do worker deixa
1/2 disponível por serviço. Com apenas uma réplica desejada, uma tarefa perdida
pode ser recriada no manager e voltar a 1/1, com possível interrupção transitória.
Sem os registros da contagem não se deve escolher um desses cenários como fato.
Um único manager não oferece redundância do controle; não foi medido tempo de
indisponibilidade nem demonstrada ausência de interrupções.

## Comandos para completar somente o que faltar

### Com o worker desligado, no manager

```bash
docker node ls
docker stack services autobudget
curl --fail --max-time 30 http://192.168.165.135:8080/api/health
```

Em seguida, na aplicação pelo IP do manager, enviar uma foto e executar uma
análise nova. Registrar o resultado e o horário com o worker ainda Down.
O healthcheck comprova resposta da API; a análise comprova o fluxo de inferência.

### Depois de ligar novamente o worker

```bash
docker node ls
```

Aguardar ambos Ready/Active; somente então restaurar duas réplicas pelo Compose:

```bash
cd /home/kayky/auto-repair-budget-agent
set -a
source .env.swarm
set +a
APP_REPLICAS=2 bash scripts/deploy-swarm.sh
docker stack services autobudget
```

Registrar aplicação 2/2 e o Visualizer com uma tarefa de cada serviço por nó.

### Evidência da variação pelo Compose

Com os dois nós Ready/Active e as imagens acessíveis no registro:

```bash
bash scripts/demo-replicas.sh
```

O roteiro faz **1 → 2 → 1**, pausa para capturas e salva saídas em
`artifacts/swarm-demo/`. Como termina com uma réplica, antes de repetir o teste
de queda executar novamente:

```bash
APP_REPLICAS=2 bash scripts/deploy-swarm.sh
```

O deploy exige dois nós prontos; não executá-lo enquanto n2 estiver Down.

## Reprodução da apresentação

Dependência opcional de autoria: python-pptx. Não faz parte do runtime da aplicação.

```bash
python3 scripts/build_evidence_presentation.py
```

O gerador lê a apresentação original e cria outro arquivo, sem sobrescrever a base.
A versão atual não contém tokens, chaves, credenciais, vídeos ou prints originais.
