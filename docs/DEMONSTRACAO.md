# Auto Repair — roteiro da apresentação

O trabalho usa duas VMs Ubuntu: um manager e um worker. Não é necessário um
terceiro nó para variar entre uma e duas réplicas. Siga primeiro
[UBUNTU_SWARM.md](UBUNTU_SWARM.md) para formar o cluster e construir as três
imagens próprias. O Visualizer usa a imagem `dockersamples/visualizer` fornecida
no Compose, fixada por digest; não foi substituído por um diagrama estático.
Use VMs Linux amd64 para a imagem Visualizer de exemplo incluída nesta revisão.

## Preparação no manager

```sh
export BACKEND_IMAGE=ghcr.io/SEU_USUARIO/autobudget-backend:v5
export FRONTEND_IMAGE=ghcr.io/SEU_USUARIO/autobudget-frontend:v5
export MONITOR_IMAGE=ghcr.io/SEU_USUARIO/autobudget-monitor:v5
docker login ghcr.io
bash scripts/build-images.sh --push
bash scripts/deploy-swarm.sh
docker node ls
```

Use um registro/namespace real acessível às duas VMs. Execute todos os comandos
com o mesmo usuário que tem acesso ao Docker e às credenciais do registro.
Os IPs privados e o acesso às VMs ainda precisam ser configurados por você.

## Durante a apresentação

1. Abra `http://IP_DO_MANAGER:8080/slides.html`. Os slides descrevem o sistema
   atual, com detector ONNX local e revisão humana.
2. Mostre os Dockerfiles de frontend, backend e proxy de monitoramento. Mostre
   o uso da imagem Docker Visualizer em `docker-compose.demo.yml`.
3. Mostre `docker node ls`: precisam aparecer manager e worker Ready/Active.
4. Abra `http://IP_DO_MANAGER:8081` e confira que aparecem os dois nós reais.
5. Execute `bash scripts/demo-replicas.sh`. Em cada pausa, capture o Visualizer
   e mostre a saída de `docker stack services autobudget`:

| Etapa | APP_REPLICAS | Frontend | Backend | Visualizer | Proxy |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1/1 | 1/1 | 1/1 | 1/1 |
| 2 | 2 | 2/2 | 2/2 | 1/1 | 1/1 |
| 3 | 1 | 1/1 | 1/1 | 1/1 | 1/1 |

6. Salve as capturas junto das saídas reais em `artifacts/swarm-demo/`. Antes de
   avançar, espere o gráfico atualizar e confirme que não há tarefas pendentes.
7. Faça uma análise real na aplicação e mostre a revisão e o orçamento.

O roteiro termina com uma réplica de cada serviço da aplicação. Para retornar
ao padrão de duas, execute `APP_REPLICAS=2 bash scripts/deploy-swarm.sh`.
`--auto` executa as etapas sem pausas, mas não produz capturas automaticamente.

## Evidências e limites

- Dockerfiles e configurações podem ser revisados antes de ter as VMs.
- A demonstração do cluster e suas capturas só ficam concluídas após executar o
  roteiro nas duas VMs. Não apresente saídas de teste/mocks como evidência real.
- Uma réplica por nó limita a escala a duas nesta topologia. A perda de um nó
  pode deixar tarefas pendentes; não é prometido failover completo.
- O Visualizer e seu proxy estão restritos ao manager. O proxy bloqueia métodos
  de alteração e rotas de execução/arquivos; a porta do painel deve ficar privada.
- Não há autenticação no painel de exemplo e a montagem `:ro` do socket não é,
  por si só, uma restrição de leitura da API. O filtro é aplicado pelo proxy.
- Os identificadores técnicos legados `autobudget_*` foram mantidos para não
  criar uma segunda stack nem apagar o histórico. A marca é **Auto Repair**.

Critérios cobertos: Dockerfiles próprios, Swarm em VMs, infraestrutura declarada
em Compose, roteiro de variação de réplicas e uso da imagem Docker Visualizer.
A comprovação da execução depende dos registros e capturas coletados nas duas VMs.
