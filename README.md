# AutoBudget AI — análise local em CPU

O sistema agora usa **ONNX Runtime + OpenCV + Pillow**, sem OpenAI, Gemini ou outra
API de IA. Fotos não são enviadas a provedores externos. Não há chave de IA nem
cobrança por análise. É necessário baixar as dependências e os pesos uma vez;
depois, a análise funciona sem internet. Links de pesquisa de peças continuam
abrindo sites externos quando você clicar neles.

## Instalar no Windows

Instale **Python 3.12 de 64 bits** e **Node.js 22 ou superior**. Extraia o ZIP,
abra o terminal dentro da pasta do projeto e execute:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\download_model.py
npm ci
npm run build
.venv\Scripts\python.exe server.py
```

Abra **http://localhost:5000**. Para iniciar nas próximas vezes, basta executar
`.venv\Scripts\python.exe server.py` na mesma pasta. Não é necessário ativar o
ambiente no PowerShell nem alterar a política de execução.

## Instalar no Linux/macOS

Requer Python 3.12 e Node.js 22+. Ambiente validado: Linux x86-64, Python 3.12, CPU.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/download_model.py
npm ci
npm run build
.venv/bin/python server.py
```

A implementação usa `CPUExecutionProvider`, sem GPU, CUDA ou PyTorch. A disponibilidade
dos pacotes ONNX Runtime varia por sistema e arquitetura; macOS/Windows precisam de
wheels compatíveis. Recomenda-se 4 GB de RAM para o computador ou VM, incluindo o
sistema operacional. Hardware mais antigo pode levar mais tempo para analisar.

O download do modelo tem **10,6 MB**. O instalador fixa a revisão e confere tamanho
e SHA-256; executá-lo novamente reutiliza um arquivo íntegro. Os pesos ficam em
`models/`, ignorado pelo Git. Não altere o checksum para contornar falhas de download.
O download usa Hugging Face apenas como repositório de arquivo, não como API de IA.

## Como usar

1. Envie de 1 a 4 fotos JPEG, PNG ou WebP (até 8 MB e 24 megapixels cada).
2. Use uma visão geral e detalhes próximos, com boa luz e foco.
3. O OpenCV verifica iluminação, resolução e detalhes/foco. Fotos claramente
   inadequadas são recusadas e não passam pelo detector.
4. O modelo sugere regiões suspeitas, com caixas na foto correspondente.
5. Preencha marca, modelo, ano e cor manualmente. Revise as sugestões, descarte
   falsos positivos e remova duplicados quando várias fotos mostrarem a mesma peça.
6. Ajuste decisão de reparo, modalidade de compra, preços e horas. Marque a revisão
   por item e a confirmação geral antes de salvar, compartilhar ou imprimir.

As amostras pré-carregadas continuam sendo **DEMONSTRAÇÃO**, com dados simulados
identificados no documento e no histórico. Para rodar o detector numa dessas fotos,
envie o arquivo correspondente de `public/samples/` pelo upload.

O detector conhece 14 classes de possíveis danos por peça, incluindo para-brisas,
faróis, lanternas, retrovisores, capô, portas, paralamas e para-choques. **Não é um
perito automático**: há falsos positivos e danos não detectados. O modelo não
reconhece riscos finos, marca/ano do carro, defeitos mecânicos ou danos internos.
Ausência de detecção não significa carro intacto. Não determina segurança para
circulação nem troca versus recuperação. Leia [MODEL_CARD.md](MODEL_CARD.md).

Os preços iniciais são referências estimadas por regras locais, sem estoque,
compatibilidade ou procedência verificados. A IA não calcula preços nem horas de
serviço. O histórico fica no navegador; não existe banco compartilhado entre VMs.

## Configuração e desenvolvimento

Copie `.env.example` para `.env` somente se precisar alterar padrões:

```dotenv
LOCAL_CONFIDENCE=0.60
# LOCAL_MODEL_DIR=models
# PORT=5000
```

O limiar 0,60 é conservador, mas não foi calibrado no seu conjunto de fotos.
Reduzi-lo mostra mais sugestões e pode aumentar falsos positivos. Ele não é uma
probabilidade de acerto. O backend serializa inferências para limitar consumo de
memória; requisições concorrentes podem retornar `LOCAL_BUSY` e devem ser repetidas
após a análise atual. Erros de dependência, peso ausente ou integridade aparecem na
interface; nunca viram danos simulados.

A interface atual está em `src/standalone.jsx` e `src/styles.css`. `npm run dev`
inicia Vite em 3000, com proxy para o Python em 5000. O build de produção fica em
`dist/`, servido pelo Python. O tema é claro, com fontes de sistema, sem CDN de
React, Babel ou fontes externas. Para iniciar o backend em desenvolvimento, use
o Python do ambiente virtual, não `node server.js` (implementação legada simulada).
Os antigos `src/main.jsx`, `src/App.jsx` e componentes relacionados não são o ponto
de entrada do build atual. Scripts antigos de patch de `index.html` são obsoletos.

Para testar com dependências e pesos instalados:

```sh
.venv/bin/python -m unittest discover -s tests -v
# no Windows, use .venv\Scripts\python.exe no lugar de .venv/bin/python
# com o servidor na porta 3000 (PORT=3000 no .env):
.venv/bin/python stress_test.py
```

A suíte inclui inferência real com chamadas de rede bloqueadas. Esse teste é
explicitamente pulado se o peso não estiver instalado; não confunda o skip com
validação do modelo. As demais verificações cobrem qualidade, NMS, coordenadas,
integridade dos pesos, contrato HTTP e ausência dos endpoints de credenciais.

## Swarm em duas VMs

Topologia: **1 manager + 1 worker**. Ambos executam tarefas. Não há alta disponibilidade
do controle: perder o manager impede agendamentos e atualizações. Há uma réplica de
cada serviço por VM (`max_replicas_per_node: 1`); uma VM indisponível deixa as
réplicas correspondentes pendentes. O histórico continua sendo local ao navegador.

Pré-requisitos:

- Linux com Docker Engine iniciado em ambas as VMs e IPs privados estáveis.
- Entre as VMs: TCP 2377 (worker para manager), TCP/UDP 7946 e UDP 4789.
  Restrinja essas portas aos IPs privados. Abra TCP 80 apenas aos clientes autorizados.
- Acesso ao mesmo registro HTTPS de imagens. Faça `docker login` quando necessário.
- Backend limitado a 768 MiB/1 CPU por VM; frontend a 64 MiB/0,25 CPU. Reserve
  capacidade para Docker e o sistema; recomenda-se VM com pelo menos 2 GB de RAM,
  preferencialmente 4 GB para desenvolver e construir imagens.

### Associar os nós

No manager:

```sh
bash scripts/swarm-node.sh manager IP_PRIVADO_MANAGER
(umask 077; docker swarm join-token -q worker > worker-token.txt)
```

Transfira o token por canal seguro ao worker. No worker:

```sh
bash scripts/swarm-node.sh worker IP_PRIVADO_WORKER IP_PRIVADO_MANAGER < worker-token.txt
rm worker-token.txt
```

Apague também a cópia do token no manager. `docker node ls` deve mostrar os dois
nós `Ready/Active`. Não use `setup-swarm-dind.sh`: ele é uma simulação antiga em
um único host que remove containers.

### Instalar os pesos em ambas as VMs

O modelo é montado **somente leitura** em cada réplica. Execute o instalador com
`LOCAL_MODEL_DIR=/opt/autobudget/models`, ou copie a pasta `models/` já verificada
para esse diretório **nas duas VMs**. O diretório deve ser acessível (0755) e o
arquivo `model.onnx` legível (0644) pelo usuário 65534 dos containers. Na pasta
exclusiva de pesos públicos, ajuste se necessário:

```sh
sudo chmod 755 /opt/autobudget/models
sudo chmod 644 /opt/autobudget/models/model.onnx
```

A imagem não contém nem baixa pesos ao iniciar. A variável `LOCAL_MODEL_HOST_DIR`
(padrão `/opt/autobudget/models`) deve apontar para o mesmo caminho em ambas as VMs.
O preload verifica SHA-256 e carrega ONNX antes de abrir a porta; modelo ausente ou
inválido impede inicialização. O healthcheck exige que o modelo esteja carregado.

### Construir e implantar

```sh
export BACKEND_IMAGE=SEU_REGISTRO/SEU_NAMESPACE/autobudget-backend:v2-local
export FRONTEND_IMAGE=SEU_REGISTRO/SEU_NAMESPACE/autobudget-frontend:v2-local
docker build -f Dockerfile.backend -t "$BACKEND_IMAGE" .
docker build -f Dockerfile.frontend -t "$FRONTEND_IMAGE" .
docker push "$BACKEND_IMAGE"
docker push "$FRONTEND_IMAGE"
# no manager, com as mesmas variáveis:
bash scripts/deploy-swarm.sh
```

Não use `127.0.0.1:5000` como registro compartilhado: ele aponta para máquinas
diferentes. No ambiente gerenciado, passe também ao build backend
`--secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt` para o pip; no frontend,
`--secret id=proxy_ca,src="$CODEX_PROXY_CERT"`. Mantenha TLS habilitado.

Valide `docker stack services autobudget` e `docker stack ps autobudget`: espere
`2/2` para cada serviço. Teste `/api/health` e uma análise real pelos dois IPs.
Implantar uma stack não comprova que as réplicas iniciaram. TLS público deve ser
terminado em um balanceador/proxy autorizado. Os IPs e o acesso remoto às VMs ainda
não foram fornecidos; esta revisão não modificou nenhuma VM.
