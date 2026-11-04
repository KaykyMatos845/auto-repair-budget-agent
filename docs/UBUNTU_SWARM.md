# Auto Repair no Ubuntu: duas VMs com Docker Swarm

Use **1 manager e 1 worker**, ambos Ubuntu 64 bits com Docker Engine, Compose v2
e curl. Recomendação: 2 vCPUs e 4 GB de RAM por VM. Não exige placa de vídeo,
Node.js ou Python instalados no host. Os comandos abaixo precisam de acesso ao
Docker; use `sudo` ou uma sessão administrativa conforme sua instalação.

Os IPs abaixo são campos para substituir pelos IPs privados reais das suas VMs.
Para encontrá-los: `hostname -I` ou `ip -4 addr`. Use endereços estáveis.

## 1. Preparar as VMs

Copie o projeto para as VMs ou clone o repositório. Se não houver Docker, execute
em cada VM:

```sh
sudo bash scripts/install-docker-ubuntu.sh
```

Permita entre **somente os IPs privados das VMs**: TCP 2377 (worker para manager),
TCP/UDP 7946 e UDP 4789. Preserve o acesso SSH ao ajustar o firewall. A porta
8080 deve estar acessível aos computadores que usarão o Auto Repair. O backend
5000 não é publicado. O mesmo registro HTTPS de imagens deve ser acessível aos
dois nós. Não use `localhost` ou `127.0.0.1` como registro entre VMs.

## 2. Criar o cluster

No manager, substitua `IP_PRIVADO_MANAGER`:

```sh
bash scripts/swarm-node.sh manager IP_PRIVADO_MANAGER
(umask 077; docker swarm join-token -q worker > worker-token.txt)
```

Transfira `worker-token.txt` por um canal seguro para o worker. No worker:

```sh
bash scripts/swarm-node.sh worker IP_PRIVADO_WORKER IP_PRIVADO_MANAGER < worker-token.txt
rm worker-token.txt
```

Apague a cópia do token também no manager. No manager, `docker node ls` precisa
mostrar **dois nós Ready/Active**. Os scripts podem ser repetidos para o mesmo nó
e função. Eles não abandonam nem substituem um cluster diferente.

## 3. Construir e enviar as imagens

Escolha um registro HTTPS que você controla, como GHCR ou Docker Hub. Defina
imagens com uma tag de versão nova a cada atualização. Exemplo no manager ou
noutra máquina com Docker e o projeto:

```sh
export BACKEND_IMAGE=ghcr.io/SEU_USUARIO/autobudget-backend:v4
export FRONTEND_IMAGE=ghcr.io/SEU_USUARIO/autobudget-frontend:v4
export MONITOR_IMAGE=ghcr.io/SEU_USUARIO/autobudget-monitor:v4
docker login ghcr.io
bash scripts/build-images.sh --push
```

Troque `SEU_USUARIO` pelo seu namespace. As imagens **não são publicadas por este
repositório**: o comando acima envia para o registro que você escolheu. Para
registro privado, use credencial com permissão de leitura nas VMs e login no
manager antes da implantação. `--with-registry-auth` transmite a autorização às
tarefas. Não coloque tokens em arquivos versionados.

Os pesos de 10,6 MB já fazem parte da imagem do backend. São conferidos no build
e antes de carregar o detector; não há bind mount, download no boot ou instalação
Python em cada VM. A primeira construção precisa de internet. Para executar sem
um registro, comece com a opção Compose em um único Ubuntu descrita no README;
Swarm em duas VMs exige que ambas consigam obter as mesmas imagens.

## 4. Implantar no manager

Exporte as mesmas variáveis no manager, se as imagens foram construídas noutra
máquina. Em seguida:

```sh
export APP_PORT=8080
bash scripts/deploy-swarm.sh
```

O script exige dois nós prontos, valida a stack e aguarda duas réplicas por
serviço e API com modelo carregado. Se não convergir em 180 segundos, mostra os
erros e sai com falha. Isso não substitui um teste com suas próprias fotos.

Abra **http://IP_DO_MANAGER:8080** ou **http://IP_DO_WORKER:8080**. A routing mesh
encaminha as requisições às réplicas disponíveis. Prefira um IP/domínio fixo para
usar o sistema: o histórico fica no navegador e não é compartilhado entre origens.

```sh
docker stack services autobudget
docker stack ps --no-trunc autobudget
docker service logs --tail=100 autobudget_backend
curl --fail http://IP_DO_MANAGER:8080/api/health
curl --fail http://IP_DO_WORKER:8080/api/health
```

Espere `2/2` em ambos os serviços e `modelLoaded: true` na API. Envie uma foto em
cada endereço e confira a análise. Para atualização, construa novas tags, altere
as variáveis e execute novamente `deploy-swarm.sh`. A stack atualiza uma réplica
por vez, com rollback em falha. Para reverter manualmente:

```sh
docker service rollback autobudget_backend
docker service rollback autobudget_frontend
```

## Capacidade e limites

- Backend por nó: limite de 1 CPU/768 MiB, reserva de 256 MiB; inferência
  serializada e pesos somente leitura. Análises concorrentes podem pedir espera.
- Frontend por nó: limite de 0,25 CPU/128 MiB; Nginx sem root, porta interna 8080.
  Até duas análises simultâneas por frontend; excesso recebe HTTP 429 em JSON.
  O endpoint de saúde continua disponível durante uploads.
- Uma réplica de cada serviço por nó. A perda de uma VM deixa suas réplicas
  pendentes por causa de `max_replicas_per_node: 1`.
- Um único manager **não fornece alta disponibilidade do controle**. Se ele cair,
  o worker pode continuar atendendo, mas não haverá agendamento/atualização até a
  recuperação do manager. Não remova/recrie o Swarm para solucionar erros comuns.
- Histórico local ao navegador; sem banco compartilhado, login ou fotos persistidas.
  Para acesso público, termine HTTPS e controle de acesso num proxy autorizado.

Este ambiente validou as imagens, o Compose com Nginx e inferência real e a
configuração da stack. As duas VMs remotas não foram acessadas. Confira a
efetivação dos limites por cgroup no Ubuntu: a configuração aceita pelo Docker
aninhado dos testes não comprova que os limites sejam aplicados naquele ambiente.

## Ambiente com proxy HTTPS

Se uma rede exigir CA própria, use um bundle de CAs completo e confiável, sem
desabilitar TLS. No ambiente gerenciado de desenvolvimento:

```sh
export PROXY_CA_FILE=/etc/ssl/certs/ca-certificates.crt
bash scripts/build-images.sh
# Ou, para Compose:
bash scripts/ubuntu-up.sh
```

O bundle entra somente como segredo de build, não fica nas imagens. Fora de redes
com proxy, não é necessário configurar essa variável.

## Visualizer e demonstração acadêmica

O deploy inclui por padrão `docker-compose.demo.yml`: Docker Visualizer na porta
8081 e proxy de consultas da API Docker, ambos no manager. A porta 2375 do proxy
não é publicada. Restrinja 8081 à rede privada ou use um túnel SSH; o painel de
exemplo não possui autenticação. O socket real só é montado no proxy.

Defina MONITOR_IMAGE junto das outras duas imagens e execute
`bash scripts/demo-replicas.sh` para aplicar **1 → 2 → 1** réplicas pelo Compose.
O roteiro pausa para capturar cada gráfico e salva as saídas reais do Docker em
`artifacts/swarm-demo/`. Veja [DEMONSTRACAO.md](DEMONSTRACAO.md).

Use `WITH_VISUALIZER=0` para executar só a aplicação. Os nomes técnicos legados
`autobudget_*` e a chave do histórico foram preservados; a marca é Auto Repair.
