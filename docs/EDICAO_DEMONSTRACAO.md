# Edição da demonstração e apresentação para o público

Arquivos de entrega:

- `public/auto-repair-demonstracao-editada.mp4` — cerca de 43 segundos, H.264/AAC,
  1920×1080, 15 fps, com áudio dos trechos aproveitados.
- `public/auto-repair-apresentacao-final.pptx` — 33 slides, com cinco vídeos
  incorporados (os quatro anteriores e a nova demonstração editada).
- `public/auto-repair-apresentacao-final.pdf` — cópia estática dos slides.

A apresentação de revisão anterior foi preservada. A versão para o público
exclui páginas de preparação, inventário de vídeos, pendências e checklist do
apresentador. As notas internas foram removidas. As limitações técnicas do
cluster foram mantidas como conteúdo da apresentação.

## Tratamento do novo ZIP

O arquivo recebido contém três gravações independentes. Duas registram terminal
e Docker Visualizer; a terceira contém orientações e não foi incorporada nem
publicada. Os arquivos originais permanecem fora do Git.

Foram aproveitados estes intervalos, na ordem indicada:

| Fonte | Intervalo original | Conteúdo |
|---|---|---|
| Terminal, gravação 20-42-14 | 00:05–00:11,5 | Preparação e comando de execução |
| Terminal, gravação 20-42-14 | 00:20–00:24 | Atualização dos serviços |
| Terminal, gravação 20-42-14 | 00:39–00:47 | Tabela de serviços em 1/1 |
| Visualizer, gravação 20-44-33 | 00:01–00:25 | Painel de duas para uma réplica por serviço |

O terminal foi recortado para manter comando e saída, retirando a barra superior,
áreas vazias e as instruções abaixo da tabela. O Visualizer foi recortado para
manter os nós e containers, excluindo a interface do navegador e outras abas.
Foram adicionados títulos editoriais fora da área original de conteúdo e a
identificação discreta de demonstração editada. Não foram alterados comandos,
contagens, estados de nós ou resultados.

Esta montagem contém cortes entre gravações independentes. Não é prova de uma
execução contínua nem de um ciclo completo 1 → 2 → 1. O resultado observado é
**aplicação declarativa de uma réplica e mudança do painel de duas para uma**.
Isso complementa as evidências da variação do número de réplicas pelo Compose.

## Validação

A edição foi revisada em uma sequência de quadros a cada segundo e em quadros de
resolução completa. Foram conferidos os recortes e a preservação da tabela de
serviços e dos estados do Visualizer. A integridade do MP4 foi conferida por
decodificação; o PPTX foi aberto e renderizado em PDF, e os vídeos incorporados
foram comparados com os arquivos locais. A reprodução interativa dos vídeos ainda
deve ser conferida no PowerPoint da máquina que será usada na apresentação.

## Reprodução dos arquivos

Extraia somente as duas gravações técnicas em uma pasta local com os nomes
`terminal-original.mp4` e `visualizer-original.mp4`. Em seguida:

```bash
python3 scripts/edit_scale_demo.py --source-dir /caminho/das/gravações
python3 scripts/build_final_presentation.py
```

O gerador final lê a apresentação de revisão de 37 slides e usa as capturas
`assets/demonstracao/v05-*.jpg` incluídas no repositório. Para o PDF, use o
LibreOffice em modo headless. A apresentação final não referencia os originais
nem depende de acesso à rede para reproduzir os cinco vídeos incorporados.
