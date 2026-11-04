# AutoBudget AI — análise local em CPU

O sistema agora usa **ONNX Runtime + OpenCV + Pillow**, sem OpenAI, Gemini ou outra
API de IA. Fotos não são enviadas a provedores externos. Não há chave de IA nem
cobrança por análise. É necessário baixar as dependências e os pesos uma vez;
depois, a análise funciona sem internet. Links de pesquisa de peças continuam
abrindo sites externos quando você clicar neles.

## Instalar e abrir no Windows

Requer **Python 3.12 de 64 bits** e **Node.js 22.12 ou superior**. Extraia o ZIP e abra
**iniciar.bat** com dois cliques, ou execute na pasta do projeto:

```powershell
npm start
```

Na primeira abertura, o iniciador cria `.venv`, instala as bibliotecas e pacotes do
front, gera a interface e baixa/confere o modelo. Essa preparação precisa de
internet. O terminal só mostra o endereço do sistema depois que o detector carrega.
Abra **http://localhost:5000** e mantenha esse terminal aberto. Front e análise
funcionam juntos nesse endereço.

Nas próximas vezes, use o mesmo **iniciar.bat** ou **npm start**. A instalação pronta
é reutilizada: os pesos são conferidos e o front só é gerado novamente se seus
arquivos mudarem. Bibliotecas ausentes ou versões divergentes são reparadas antes
de iniciar. Ao atualizar o projeto, preserve `.venv`, `models/` e
`.autobudget-local.json` na mesma pasta. O histórico continua no navegador.

Não é necessário ativar o ambiente, executar `npm ci` ou `npm run build`
separadamente para usar esse iniciador. O comando antigo `python server.py` usa o
Python selecionado no terminal, que pode ser outro e não conter as bibliotecas.

Se o iniciador informar que Python está ausente, instale:

```powershell
winget install --exact --id Python.Python.3.12
```

Reabra o terminal e execute `npm start` novamente. Em caso de falha de importação,
o terminal informa o módulo e o erro real. Falhas de DLL no Windows podem exigir
o [Microsoft Visual C++ Runtime x64](https://aka.ms/vs/17/release/vc_redist.x64.exe).
Não confunda biblioteca instalada com biblioteca capaz de carregar.

Para verificar o ambiente sem instalar ou iniciar servidor, use `npm run check`.
Se a página abrir e a análise falhar, consulte também
**http://localhost:5000/api/health**; o diagnóstico inclui as bibliotecas que não
carregaram. Feche servidores de tentativas anteriores antes de iniciar de novo.

## Instalar no Linux/macOS

Requer Python 3.12 de 64 bits e Node.js 22.12+. Execute `npm start` na pasta do projeto.
A preparação é a mesma, com Python em `.venv/bin/python`. Ambiente validado: Linux
x86-64, Python 3.12, CPU. A seleção do interpretador Windows é coberta por testes e
os wheels Windows x64 foram conferidos; não houve execução nativa em Windows/macOS.

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
4. Escolha a leitura **detalhada** (padrão) ou **rápida**. A detalhada analisa a
   foto inteira e até quatro recortes sobrepostos para procurar detalhes que
   podem desaparecer ao reduzir a foto. Usa mais CPU, com o mesmo modelo e limiar.
   A rápida faz uma única leitura. Fotos de até 640 pixels não recebem recortes.
   O modelo sugere regiões suspeitas, com caixas na foto correspondente.
5. Preencha marca, modelo, ano e cor manualmente. Revise as sugestões, descarte
   falsos positivos e remova duplicados quando várias fotos mostrarem a mesma peça.
6. Cada sugestão mostra a foto de origem. Use **Corrigir identificação da peça**
   para ajustar o nome, ou **Descartar sugestão** se estiver incorreta. Corrigir
   a peça zera as cotações antigas e exige nova revisão. Acrescente manualmente
   danos que o modelo perdeu. Os detalhes do detector ficam em **Sobre esta análise**.
7. Ajuste decisão de reparo, modalidade de compra, preços e horas. Marque a revisão
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
Os recortes podem recuperar detalhes, mas também gerar falsos positivos. Eles não
adicionam classes ao modelo nem garantem precisão profissional.

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
inicia somente Vite em 3000, com proxy para o Python em 5000. Em outro terminal,
`npm run server` prepara e inicia apenas o backend pela `.venv`. O build de produção fica em
`dist/`, servido pelo Python. O tema é claro, com fontes de sistema, sem CDN de
React, Babel ou fontes externas. Para iniciar o backend em desenvolvimento, use
o Python do ambiente virtual, não `node server.js` (implementação legada simulada).
Os antigos `src/main.jsx`, `src/App.jsx` e componentes relacionados não são o ponto
de entrada do build atual. Scripts antigos de patch de `index.html` são obsoletos.

Para testar com dependências e pesos instalados:

```sh
.venv/bin/python -m unittest discover -s tests -v
# no Windows, use .\.venv\Scripts\python.exe no lugar de .venv/bin/python
# com o servidor na porta 3000 (PORT=3000 no .env):
.venv/bin/python stress_test.py
```

A suíte inclui inferência real com chamadas de rede bloqueadas. Esse teste é
explicitamente pulado se o peso não estiver instalado; não confunda o skip com
validação do modelo. As demais verificações cobrem qualidade, NMS, coordenadas,
integridade dos pesos, contrato HTTP e ausência dos endpoints de credenciais.

## Rodar no Ubuntu com Docker

Não precisa instalar Node, Python, bibliotecas ou pesos na VM. As imagens incluem
as dependências, o front compilado e o modelo com SHA-256 verificado. A análise
continua local em CPU, sem chave de IA e sem download durante a execução.

Após copiar ou clonar este projeto para o Ubuntu:

```sh
# Só se o Docker ainda não estiver instalado:
sudo bash scripts/install-docker-ubuntu.sh
# Construir e iniciar o sistema:
sudo bash scripts/ubuntu-up.sh
```

Abra **http://IP_DO_UBUNTU:8080**. O script espera os dois serviços ficarem
saudáveis. Para atualizar, atualize o código e execute o mesmo script novamente.
Para alterar a porta: `sudo APP_PORT=8090 bash scripts/ubuntu-up.sh`.

Se Docker já estiver configurado para seu usuário, os scripts não precisam de
`sudo`. O instalador usa o repositório apt assinado oficial do Docker e preserva
uma instalação existente; requer Ubuntu com acesso à internet para a construção.

Comandos úteis:

```sh
sudo docker compose -f compose.ubuntu.yml ps
sudo docker compose -f compose.ubuntu.yml logs --tail=100 backend frontend
sudo docker compose -f compose.ubuntu.yml down
```

Para duas VMs, siga **[o guia de Swarm no Ubuntu](docs/UBUNTU_SWARM.md)**. A stack
usa duas réplicas por serviço, uma por nó, imagens de um registro compartilhado,
healthchecks e rollback de atualização. Não é necessário copiar a pasta `models/`
nas VMs: os pesos fazem parte da imagem do backend.

O histórico das OS continua no navegador. Acessar por IPs/domínios diferentes ou
em outro dispositivo não compartilha o histórico. Os containers não armazenam
fotos permanentemente nem oferecem autenticação de usuários. Para acesso pela
internet, use um proxy com HTTPS e controle de acesso adequados à sua oficina.

## Visual e validação

A interface usa azul petróleo e verde, etapas de vistoria, painel de fotos e
veículo lado a lado no desktop, prévias por item e avisos na própria página. Os
efeitos de entrada, foco e carregamento respeitam a preferência de movimento
reduzido do navegador. Ícones são compilados junto do React; não há CDN ou fontes
externas. Vite e o plugin React foram atualizados e duas bibliotecas de exportação
não utilizadas foram removidas; a auditoria npm desta revisão não apontou vulnerabilidades. Fotos de uma análise cancelada não substituem uma nova vistoria.

As imagens são construídas em múltiplas etapas, executam sem root e usam sistema
de arquivos somente leitura com `/tmp` temporário. Apenas o Nginx publica uma
porta. O backend carrega e verifica o detector antes de abrir sua porta.

Os testes locais incluem interface desktop/celular, inferência real através do
Nginx e análise no backend sem rede externa. As duas VMs do usuário não foram
acessadas: os IPs e acesso remoto ainda não foram fornecidos. Limites de CPU/RAM
são configurados, mas a efetivação de cgroups no Docker aninhado deste ambiente
não comprova a efetivação nas VMs de destino.
