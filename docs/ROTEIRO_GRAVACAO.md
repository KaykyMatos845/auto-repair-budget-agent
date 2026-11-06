# Auto Repair — gravação da aplicação e indisponibilidade da worker

Objetivo: começar mostrando rapidamente uma análise real, desligar a VM worker,
observar o cluster e repetir a análise pelo endereço da manager. Duração sugerida:
3 a 5 minutos, conforme o tempo de detecção e recuperação dos nós.

Endereços informados para este ambiente:

- Manager: **192.168.165.135**.
- Worker: **192.168.165.140**.
- Aplicação: **http://192.168.165.135:8080**.
- Docker Visualizer: **http://192.168.165.135:8081**.

## Preparar antes de começar a gravar

Faça login no registro e a implantação antes da gravação. No terminal da manager,
com o usuário que possui acesso ao Docker e às credenciais do registro:

```bash
cd /home/kayky/auto-repair-budget-agent
source .env.swarm
APP_REPLICAS=2 bash scripts/deploy-swarm.sh
docker node ls
docker stack services autobudget
docker service ps autobudget_frontend
docker service ps autobudget_backend
```

Só comece quando os dois nós estiverem Ready/Active, frontend e backend em **2/2**
e Visualizer e proxy em **1/1**. Confira que existe uma tarefa em execução de cada
serviço da aplicação em cada VM. O roteiro de escala 1 → 2 → 1 termina com uma
réplica: é obrigatório voltar a duas antes deste teste de indisponibilidade.

Deixe abertas a aplicação, o Visualizer, um terminal da manager e o console da
VM worker. Separe uma foto que já tenha testado por upload. Não use apenas o
botão de exemplo simulado como comprovação de inferência real.

Mantenha o navegador no endereço **da manager** durante todo o teste. O endereço
da própria worker deixa de responder quando essa VM é desligada; não há um
balanceador externo ou um IP virtual que torne esse endereço disponível.

## Cena 1 — aplicação, aproximadamente 40 segundos

Mostre a página inicial, envie uma foto e clique em analisar. Aponte uma região
sugerida e os campos de revisão do item. Evite preencher um orçamento inteiro.

Fala sugerida:

> Este é o Auto Repair. A aplicação recebe fotos do veículo, executa um detector
> local em CPU e apresenta sugestões para revisão. Os preços e a decisão de
> reparo precisam ser conferidos. Agora vou verificar a continuidade do serviço
> quando uma das VMs ficar indisponível.

## Cena 2 — estado inicial do cluster, aproximadamente 20 segundos

Mostre os dois nós no Visualizer e as tarefas distribuídas. No terminal da
manager, acompanhe os estados em tempo real:

```bash
watch -n 2 'docker node ls && docker stack services autobudget'
```

Fala sugerida:

> Temos duas VMs: uma manager e uma worker. Frontend e backend estão com duas
> réplicas, uma em cada nó. O Visualizer e seu proxy executam na manager.

## Cena 3 — tornar a worker indisponível

No console **da VM worker, 192.168.165.140**, confira a máquina e desligue-a:

```bash
hostname
hostname -I
sudo poweroff
```

Isso demonstra um desligamento da VM. Para representar uma falha abrupta,
desligue a mesma VM pelo comando Power Off do hipervisor, em vez do comando
acima. Escolha uma das formas e descreva no vídeo o que foi feito. Não desligue
a manager nem o computador que está gravando.

Fala sugerida:

> Vou desligar somente a worker. O acesso à aplicação continuará sendo feito
> pela manager, que permanece ligada.

Volte ao Visualizer e ao terminal da manager. Aguarde o nó aparecer **Down**;
a detecção não é instantânea. Registre também eventuais erros ou interrupções
durante essa transição, sem prometer tempo de recuperação fixo.

## Cena 4 — provar a continuidade com capacidade reduzida

O resultado esperado nesta configuração é:

| Item | Com as duas VMs | Worker desligada |
| --- | --- | --- |
| Manager | Ready | Ready |
| Worker | Ready | Down |
| Frontend | 2/2 | 1/2 |
| Backend | 2/2 | 1/2 |
| Visualizer e proxy | 1/1 cada | 1/1 cada |

O Compose limita a **uma réplica de cada serviço por nó**. A manager mantém suas
tarefas, mas não recebe a segunda réplica. Portanto, 1/2 é a contagem esperada,
e a tarefa que falta pode ficar pendente. Não apresente esse cenário como
recriação das duas réplicas no mesmo nó ou recuperação da capacidade total.

Fala sugerida:

> A worker ficou indisponível e o cluster está operando com capacidade reduzida.
> Uma réplica do frontend e uma do backend continuam na manager. Como limitamos
> cada serviço a uma réplica por nó, as réplicas restantes aguardam a recuperação
> da worker.

Mostre uma resposta real da API. Use outro terminal da manager ou encerre o watch
com Ctrl+C:

```bash
curl --fail --show-error -w '\nHTTP %{http_code}\n' \
  http://192.168.165.135:8080/api/health
```

Confira **HTTP 200** e **modelLoaded: true**. Depois volte à aplicação e faça
**uma nova análise por upload**, enquanto a worker ainda estiver desligada.
Só mostrar uma página que já estava aberta não comprova que o backend continua
funcionando. O navegador pode exibir conteúdo carregado anteriormente.

Fala sugerida, somente depois de obter uma nova resposta:

> A API respondeu e uma nova análise foi executada com a worker desligada.
> Isso mostra continuidade da aplicação pelo nó que permaneceu disponível.

Podem ocorrer respostas com erro durante a detecção da falha e a atualização do
roteamento. Registre o comportamento observado. Não afirme interrupção zero ou
um tempo de recuperação que não tenha sido medido na gravação.

## Cena 5 — recuperar a worker e encerrar

Ligue novamente a VM worker pelo hipervisor. O Docker deve iniciar junto com o
Ubuntu, se a instalação recomendada foi usada. Se necessário, dentro da worker:

```bash
sudo systemctl start docker
```

A VM original conserva sua associação ao Swarm. Não é necessário gerar outro
token de entrada nem recriar o cluster. Na manager, acompanhe novamente:

```bash
watch -n 2 'docker node ls && docker stack services autobudget'
```

Aguarde a worker ficar Ready e ambos os serviços da aplicação retornarem a
**2/2**. Confira as tarefas no Visualizer e faça uma última chamada à API.

Fala sugerida:

> Após a recuperação da worker, o Swarm volta a atender ao estado desejado de
> duas réplicas. A demonstração mostrou a aplicação em funcionamento, a perda de
> um nó, o atendimento com capacidade reduzida e a recuperação das réplicas.

## Se o resultado não for o esperado

Se frontend ou backend não estavam em 2/2 antes da falha, não prossiga: a única
réplica pode estar na worker e a aplicação pode parar ao desligá-la. Se a API
continuar falhando depois de o nó estar Down e as tarefas restantes estabilizarem,
consulte na manager:

```bash
docker stack ps --no-trunc autobudget
docker service ps autobudget_backend
docker service ps autobudget_frontend
docker service logs --tail 60 autobudget_backend
docker service logs --tail 60 autobudget_frontend
```

Este roteiro não altera as regras de posicionamento. Ele demonstra a continuidade
do serviço com as réplicas sobreviventes, e não alta disponibilidade do plano de
controle: existe somente um manager.
