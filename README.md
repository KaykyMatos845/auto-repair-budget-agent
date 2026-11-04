# AutoBudget AI

## Desenvolvimento

Requer Node 22+ e Python 3.12. A interface atual está em `src/standalone.jsx`,
com estilos em `src/styles.css`. `index.html` carrega esse único ponto de entrada.
O build inclui React de produção: não baixa React/Babel de CDN nem compila JSX no navegador.
Fontes Google continuam opcionais, com fontes de sistema como fallback.

```sh
npm ci
# terminal 1: API Python na porta 5000
npm run server
# terminal 2: Vite na porta 3000, proxy /api para 5000
npm run dev
```

Para servir o build pelo Python:

```sh
npm run build
PORT=3000 npm start
# outro terminal, mesma pasta
python3 stress_test.py
```

O Python serve `dist/` (ou `STATIC_DIR`), e só precisa da biblioteca padrão.
Não use `node server.js` para a interface atual: ele é uma implementação antiga,
com respostas simuladas e rotas diferentes. `src/main.jsx`, `src/App.jsx` e os
componentes importados por eles pertencem à interface anterior e não entram no
bundle atual. Foram preservados nesta revisão, assim como suas dependências.
Scripts antigos de patch que editam JSX dentro de `index.html` não se aplicam à nova estrutura.

Sem `GEMINI_API_KEY`, análises retornam dados simulados. Isso não valida IA real.
Use variável de ambiente ou `.env` local ignorado. A chave de contingência que
estava embutida no servidor foi removida. A chave informada na interface segue em
cada requisição de análise, sem depender de sessão no nó do Swarm. Não é necessário
chamar `/api/set-key`, uma rota legada que ainda existe para compatibilidade.
O histórico permanece no navegador: não há banco de dados compartilhado.

## Swarm em duas VMs

Topologia: **1 manager + 1 worker**, ambos disponíveis para tarefas. Não é um
control plane de alta disponibilidade: perder o manager impede agendamentos e
atualizações até recuperá-lo. As réplicas usam `max_replicas_per_node: 1`; se uma
VM cair, as réplicas dela ficam pendentes e a outra continua atendendo.

Pré-requisitos em ambas as VMs:

- Linux com Docker Engine instalado e iniciado; usuário autorizado a usar Docker.
- IPs privados estáveis, comunicação bidirecional e horário sincronizado.
- Entre os IPs privados: TCP 2377 (worker para manager), TCP/UDP 7946 e UDP 4789.
  Restrinja essas portas às VMs. Porta TCP 80 apenas aos clientes autorizados.
- Acesso HTTPS ao mesmo registro de imagens e `docker login` quando privado.
- Recursos por VM para frontend e backend: limites somados de 320 MiB de RAM
  e 0,75 CPU, além dos recursos do sistema e Docker. Ajuste após medir carga real.

Não execute `setup-swarm-dind.sh`: é uma simulação legada em um único host que
remove containers, não configura duas VMs.

Na VM manager, usando o IP privado real:

```sh
bash scripts/swarm-node.sh manager IP_PRIVADO_MANAGER
(umask 077; docker swarm join-token -q worker > worker-token.txt)
```

Transfira o token por canal seguro ao worker. Não coloque o token no Git ou chat.
Na VM worker:

```sh
bash scripts/swarm-node.sh worker IP_PRIVADO_WORKER IP_PRIVADO_MANAGER < worker-token.txt
rm worker-token.txt
```

Apague a cópia do token no manager depois da associação. No manager, `docker node ls`
deve mostrar exatamente as duas VMs como `Ready` e `Active`.

### Imagens e implantação

Use registro acessível **pelas duas VMs**, com tags de versão imutáveis.
`127.0.0.1:5000` não é um registro compartilhado entre hosts.

```sh
export BACKEND_IMAGE=SEU_REGISTRO/SEU_NAMESPACE/autobudget-backend:v1
export FRONTEND_IMAGE=SEU_REGISTRO/SEU_NAMESPACE/autobudget-frontend:v1
docker build -f Dockerfile.backend -t "$BACKEND_IMAGE" .
docker build -f Dockerfile.frontend -t "$FRONTEND_IMAGE" .
docker push "$BACKEND_IMAGE"
docker push "$FRONTEND_IMAGE"
# executar no manager com as mesmas variáveis exportadas
bash scripts/deploy-swarm.sh
```

No ambiente gerenciado, o build frontend precisa também de
`--secret id=proxy_ca,src="$CODEX_PROXY_CERT"`. Não desative verificação TLS.
`.env` e arquivos de credenciais não são copiados para as imagens.

Para IA no cluster, forneça `GEMINI_API_KEY` no ambiente do comando de deploy,
sem gravá-la no compose. Esse valor passa a fazer parte da configuração do serviço,
legível aos administradores Docker; restrinja o acesso. A imagem backend executa
sem root. TLS público deve ser terminado em um balanceador/proxy autorizado.

Validação após implantar:

```sh
docker stack services autobudget
docker stack ps autobudget --no-trunc
curl --fail http://IP_PRIVADO_MANAGER/api/health
curl --fail http://IP_PRIVADO_WORKER/api/health
```

Espere `2/2` em ambos os serviços e confira a interface e o carregamento de uma
amostra pelos dois IPs. Um deploy aceito não prova que as réplicas iniciaram.
O healthcheck confirma a API local, não autenticação Gemini. Para validar IA real,
confirme `aiPowered: true` numa análise com imagens e credencial própria.

A configuração foi preparada para duas VMs, mas a associação e o deploy remoto
aguardam os IPs e acesso às máquinas. Nenhuma VM foi modificada por esta revisão.
