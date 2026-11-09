# Revisão da apresentação e demonstração — Auto Repair

Base preservada: `public/auto-repair-apresentacao-20-slides.pptx`.
Entrega ampliada: `public/auto-repair-apresentacao-demonstracao.pptx`, **36 slides**,
com três vídeos incorporados e seis prints originais do ZIP. PDF com as mesmas
páginas, porém vídeos estáticos. Sem dependência de links externos para reprodução.

## Material revisto e incorporado

| Fonte | Evidência | Uso na apresentação |
|---|---|---|
| P02 | docker node ls: kayky Ready/Active/Leader, n2 Ready/Active | Print original do cluster inicial |
| P03 | Serviços da aplicação 2/2 e monitoramento 1/1 | Print original da stack inicial |
| P04 | Visualizer com frontend no manager e backend no worker | Print original após redução |
| P05 | docker service scale com ambos os serviços em 1 | Print original do comando |
| P06 | Visualizer: n2 vermelho; aplicação e monitoramento no manager | Print original da falha |
| P07 | docker node ls: n2 Down, manager Leader | Print original do estado do worker |
| V03 | Primeiro teste completo da aplicação, 141,876s | Capturas e vídeo incorporado |
| V01 | Nova análise, revisão e orçamento, 51,714s; autor identifica como pós-queda | Captura e vídeo incorporado |
| V02 | Terminal com n2 Down, 58,214s | Captura e vídeo incorporado |

P01 (Visualizer inicial com duas réplicas por serviço) foi visto no chat, mas não
está entre as seis imagens do ZIP. P03 comprova a contagem inicial; o material
recebido foi incorporado integralmente, sem reconstruir capturas fictícias.
Os nomes completos dos vídeos estão nas notas do slide de acervo.

A revisão visual cobriu sequências de quadros a cada dois segundos dos três vídeos,
com extrações em resolução original. Todos têm áudio silencioso (pico -91 dB).
As cópias H.264/AAC em `assets/demonstracao/` mantêm a duração, em 1280×760/15 fps.
Os originais de 1920×1140 foram preservados no workspace, fora do Git.
As imagens do ZIP foram copiadas sem alterar os pixels. A compressão dos vídeos
reduz tamanho e resolução, sem cortar a sequência. Não houve transcrição de fala.

## Resultados do teste inicial V03

- Aproximadamente 00:13: foto carregada.
- 00:29–00:37: análise acionada, retorno de uma sugestão Porta e região na imagem.
- 00:39–01:13: inclusão manual de para-choque traseiro.
- 01:15–01:39: revisão de cotações e horas.
- 01:41–02:03: serviço de terceiros e valor de R$ 200.
- 02:05–02:11: peças R$ 2.525, mão de obra R$ 320, terceiros R$ 200; total R$ 3.045.
- 02:13–02:21: prévia do orçamento e diálogo de impressão do navegador.

Comprova o fluxo observado de análise, revisão e impressão. Não comprova um PDF
salvo, envio de WhatsApp ou precisão do modelo em outras fotos.

## Teste relatado após a queda: V01 + V02

V01 parte sem itens, carrega a foto, aciona nova análise por volta de 00:17 e
exibe um resultado entre 00:19 e 00:21. Depois mostra revisão e impressão.
V02 registra n2 Down e kayky Ready/Active/Leader. O autor informa que V01 foi
gravado com o worker desligado. Essa associação é indicada explicitamente nos
slides: os vídeos não exibem navegador e terminal ao mesmo tempo.

**Divergência preservada:** V02 continua exibindo 2/2 para frontend e backend com
n2 Down, nos quadros revistos. Isso não comprova duas tarefas saudáveis. Não foi
mostrada a listagem detalhada de tarefas para explicar a contagem. Não substituímos
esse resultado por um 1/2 esperado, nem atribuímos uma causa sem evidência.
P06, de outro momento, mostra uma tarefa de cada serviço no manager.

Active é a configuração de disponibilidade para agendamento; pode coexistir com
Down, que informa o estado de comunicação do nó.

## Conferência do enunciado

| Requisito | Situação observada | Complemento necessário |
|---|---|---|
| Dockerfiles dos serviços | Frontend, backend e monitor próprios; Visualizer oficial por digest | Apontar os arquivos na fala |
| Swarm em VMs ou DinD | Duas VMs reais, manager e worker documentados | Não exige terceira VM |
| Compose como infraestrutura como código | YAMLs e APP_REPLICAS configurados | Registrar escala aplicada pelo Compose |
| Variação de réplicas | Estado 2/2, comando CLI de redução e Visualizer com uma réplica | Ciclo declarativo ainda não registrado |
| Docker Visualizer | Prints originais de escala e falha incorporados | Requisito visual documentado |

## O que ainda falta

1. **Escala pelo Compose:** os registros mostram `docker service scale`, que não
   altera o YAML. Falta execução documentada de `scripts/demo-replicas.sh` ou
   dos deploys com APP_REPLICAS variável.
2. **Recuperação do worker:** n2 voltando a Ready, serviços 2/2 e gráfico recuperado.
3. **Para tornar o teste de continuidade inequívoco:** captura conjunta de n2 Down
   e uma nova análise concluída, ou um vídeo contínuo alternando ambas as telas.
4. **Para explicar a divergência de V02:** listar tarefas, estados e erros com
   `docker stack ps --no-trunc autobudget` e `docker service ps --no-trunc`.

Os itens 2–4 complementam a demonstração de falha; não são requisitos extras
impostos ao enunciado. Não há medição de indisponibilidade, prova da cronologia de
migração ou redundância do controle: existe somente um manager.

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
A versão atual contém os três vídeos, capturas extraídas e seis prints originais do ZIP. Não inclui tokens, chaves ou credenciais.
