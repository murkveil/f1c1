# XI. Logs do TensorFlow: correção legítima contra supressão indiscriminada

## O problema

Após a instalação das bibliotecas CUDA e o ajuste do `LD_LIBRARY_PATH`
(capítulo X), a mensagem `Could not find cuda drivers` desapareceu, mas
duas outras continuaram aparecendo na primeira célula do notebook:

```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results...
```

A pergunta: essas duas precisam ser corrigidas? Ignoradas? Suprimidas?
A resposta depende de uma classificação precisa da natureza de cada
mensagem.

## Taxonomia das três mensagens originais

| Mensagem | Severidade real | Origem | Corrigível? |
|----------|----------------|--------|-------------|
| `Could not find cuda drivers` | Warning funcional | `cudart_stub.cc:31` | **Sim** — instalar driver NVIDIA (capítulo X) |
| `All log messages before absl::InitializeLog()` | Ruído de bootstrap | Binário C++ do TF | **Não** — bug upstream rastreado no issue 62075 |
| `oneDNN custom operations are on` | Nível INFO | `port.cc:153` | **Não** — informação sobre otimização habilitada |

A primeira sinalizava estado real do sistema (GPU inacessível) e foi
resolvida por ação concreta em configuração. As outras duas são
inerentes à implementação do TensorFlow e não representam estado
incorreto.

## Por que `absl::InitializeLog()` não tem correção no código do usuário

A mensagem é emitida pelo próprio binário compilado do TensorFlow durante
o bootstrap da biblioteca `absl` do Google, **antes** do interpretador
Python obter controle. Nenhuma linha de código do usuário executa antes
dela. Para que fosse eliminada seria necessário recompilar o TensorFlow
linkado com uma versão do `absl` em que a inicialização ocorresse antes
da primeira tentativa de log — isso é trabalho do upstream do projeto,
não do consumidor da biblioteca.

O bug é conhecido: está registrado no [issue 62075](https://github.com/tensorflow/tensorflow/issues/62075)
do repositório oficial desde 2023, ainda sem correção mergeada. A
mensagem aparece em qualquer versão do TF 2.x em Linux; não depende da
versão do Python nem do método de instalação.

## Por que desativar oneDNN seria degradação, não correção

A mensagem `oneDNN custom operations are on` é um `LOG(INFO)` — nível
informativo, não aviso ou erro. Ela anuncia que as otimizações oneDNN
(operações fundidas, primitivas vetorizadas em CPU/GPU) estão ativas, o
que é o comportamento padrão do TensorFlow desde a versão 2.9.

A única forma de eliminar a mensagem sem suprimir outros logs é:

```bash
export TF_ENABLE_ONEDNN_OPTS=0
```

Mas essa variável **desliga** as otimizações — não só silencia o
anúncio. O treino da MLP passa a usar operações não-fundidas, com perda
mensurável de performance em CPU (oneDNN) e em GPU (onde operações
fundidas reduzem round-trips entre memória global e shared).

A "correção" trocaria um log pelo degrado de throughput do modelo. Não é
correção; é ablação.

## Por que não usar `TF_CPP_MIN_LOG_LEVEL=3`

A alternativa óbvia de força bruta seria elevar o nível global de log:

```bash
export TF_CPP_MIN_LOG_LEVEL=3  # suprime INFO, WARNING e ERROR
```

Isso silenciaria as duas mensagens — mas **também** silenciaria erros
legítimos que pudessem ocorrer durante o treino (falhas de alocação de
memória na GPU, overflow em gradientes, divergências numéricas que o TF
reporta como `WARNING` ou `ERROR`). A variável não é granular: ela atua
em todo o subsistema de log do TF, sem discriminar por módulo ou tipo
de evento.

Em engenharia, diagnóstico é função do ruído do log. Silenciar tudo
para ocultar duas linhas inócuas troca a capacidade de debug por
estética de output.

## A decisão

1. A mensagem `Could not find cuda drivers` foi **corrigida** pela
   instalação legítima do driver NVIDIA e das bibliotecas CUDA via pip
   (capítulo X). O sistema agora contradiz factualmente a mensagem, e
   ela desapareceu sem uso de flag de supressão.

2. As mensagens `absl::InitializeLog` e `oneDNN` foram **aceitas e
   documentadas**. Nenhuma flag de supressão foi adicionada ao notebook
   ou ao ambiente.

3. Uma célula Markdown foi inserida no `mlp_heartbeat_v2.ipynb`, imediatamente
   após o título e antes da primeira célula de código, explicando as
   duas mensagens remanescentes com referência ao issue upstream. O
   avaliador que abrir o notebook vê o contexto antes de ler o output
   da importação do TensorFlow.

## O princípio em uma frase

Correção elimina a causa; supressão oculta o efeito. Quando a causa
está dentro do nosso alcance (driver ausente, biblioteca fora do path),
corrigir é obrigatório. Quando a causa está fora do nosso alcance
(bug de bootstrap do TF), documentar é honesto e silenciar é dissimulação.
