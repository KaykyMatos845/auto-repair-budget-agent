# Detector local: origem, limites e licença

- Modelo: [sosa123454321/cekicin-damage-yolo11n-onnx](https://huggingface.co/sosa123454321/cekicin-damage-yolo11n-onnx).
- Revisão fixada: `d1b028c3b7d7512d8da77497f283177bdb2cb86d`.
- Arquivo: `model.onnx`, 10.614.990 bytes, SHA-256 registrado em `model_manifest.json`.
- Exportação ONNX de [vineetsarpal/yolov11n-car-damage](https://huggingface.co/vineetsarpal/yolov11n-car-damage), arquitetura Ultralytics YOLO11-nano.
- Créditos: autores dos dois repositórios, Ultralytics e autores do conjunto Roboflow “Automobile Damage Detection”.
- Licença declarada da exportação: **AGPL-3.0**. O repositório de origem dos pesos
  tem uma indicação de licença diferente; a exportação documenta a herança AGPL de
  Ultralytics. Os pesos não são relicenciados por este projeto. Confira as obrigações
  da licença e os direitos do dataset antes de distribuir uma solução fechada.

## Por que este modelo

É um detector pequeno (10,6 MB em ONNX) que funciona em CPU sem PyTorch, GPU,
serviço externo ou código remoto do autor. O backend usa ONNX Runtime para inferir,
Pillow para orientação EXIF e redução da imagem e OpenCV para brilho/foco. Tamanho,
SHA-256 e revisão são fixos. Nenhum script dos repositórios do modelo é executado.
O runtime não baixa pesos ou faz chamadas a provedores de IA. No Docker, o modelo
é baixado e verificado durante a construção e incluído na imagem, somente leitura.
Na instalação local, o iniciador prepara e confere os pesos antes de abrir o servidor.

## O que ele faz

As 14 classes representam possíveis danos em para-brisa dianteiro, farol, vidro
traseiro, soleira, retrovisor, lanterna, capô, porta-malas, porta, paralama,
para-choque dianteiro, painel lateral traseiro, para-choque traseiro e teto.
Os seis primeiros grupos são classificados como dano na peça; os demais como
possível amassado. A saída não informa causa, gravidade, lado exato, marca/modelo,
horas, custo, necessidade de troca ou segurança para circulação.

Pré-processamento: RGB, orientação EXIF corrigida, imagem reduzida para no máximo
1600 pixels, letterbox 640×640 com padding 114 e divisão por 255. A saída é
`[1,18,8400]`; limiar padrão 0,60 e NMS por classe com IoU 0,45. Caixas são convertidas
para percentuais da foto correspondente. Imagens severamente escuras/claras,
pequenas ou com pouco detalhe/desfoque são excluídas antes da inferência. Esses
limiares de qualidade são heurísticos e também podem errar.

A leitura detalhada, padrão desde esta revisão, usa a foto inteira e quatro
recortes de 70% da largura e altura, com sobreposição. Só há recortes quando a
foto processada tem algum lado acima de 640 pixels. São no máximo cinco
inferências sequenciais por foto, com a mesma sessão, pesos e limiar. Caixas dos
recortes são remapeadas para a foto original; fragmentos que tocam bordas internas
do recorte são descartados. NMS por classe remove sobreposições entre as cinco
leituras da mesma foto. Não une caixas de fotos diferentes. O modo rápido usa
somente a foto inteira. O custo de CPU pode chegar a cerca de cinco vezes o da
inferência rápida; isso não significa cinco vezes a precisão. O consumo adicional
fica limitado pelo processamento sequencial, sem carregar cópias do modelo.

## Limitações conhecidas

A documentação da exportação registra falsos positivos relevantes em veículos
intactos: no teste externo descrito pelo autor, o pipeline original em limiar 0,25
marcou dano em cerca de 46% dos carros intactos. Esse número não é uma medição do
nosso limiar 0,60 nem prova desempenho na sua frota. Ele justifica mostrar apenas
**sugestões**, exigir revisão e não produzir laudo automático.

Não reconhece riscos finos, trincas genéricas, danos mecânicos ou internos. Algumas
peças comuns e outras classes não estão cobertas. Pode confundir reflexos,
sombras, junções de painéis e deformações. Fotos de cenas distantes e veículos
muito pequenos também podem falhar. Ausência de detecção não comprova carro íntegro.
Várias fotos podem duplicar a mesma peça no orçamento; o usuário precisa conferir.

## Validação desta integração

Na máquina de desenvolvimento, as três amostras existentes foram processadas em
CPU. Comparação funcional usando os mesmos pesos e limiar 0,60:

| Amostra | Leitura rápida | Leitura detalhada |
| --- | --- | --- |
| Civic | Para-choque dianteiro | Para-choque dianteiro |
| Corolla | Porta e paralama | Duas regiões de porta, paralama e para-choque dianteiro |
| Onix | Nenhuma sugestão | Lanterna e para-choque traseiro |

Essas três imagens do repositório não constituem um conjunto de avaliação anotado.
Encontrar mais caixas não comprova melhor precisão. A leitura detalhada ainda
perde danos visíveis, como o retrovisor no Corolla e a tampa do porta-malas no
Onix, e pode acrescentar erros. Não houve treinamento novo ou adição de classes.
O tempo observado com sessão carregada foi cerca de 0,09–0,10 segundo por foto no
modo rápido e 0,30–0,34 no detalhado, apenas nesta máquina e nessas imagens.

A suíte testa inferência real com rede bloqueada, geometria, NMS, qualidade,
integridade e estados de erro. Para avaliar precisão, reúna fotos próprias de
carros danificados **e intactos**, com anotações de um profissional. Meça falsos
positivos e danos perdidos por classe antes de ajustar o limiar ou usar os valores
para decisões de reparo. Não há garantia de precisão profissional neste modelo.

O container também processou uma foto real com `--network none`, sem credenciais.
O RSS do processo observado foi cerca de 177 MB. Os limites de 768 MiB/1 CPU foram
aceitos como configuração, mas o Docker aninhado deste ambiente compartilha os
cgroups do executor: a efetivação desses limites **não foi validada**. Confira-a
nas VMs de destino antes de dimensionar a implantação.
