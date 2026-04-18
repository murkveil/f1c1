# XII. Não-determinismo do TensorFlow em GPU e estratégia de reprodutibilidade

## Contexto do problema

Durante uma auditoria dos valores numéricos citados no roteiro de vídeo,
observei que os valores de métricas finais do `mlp_heartbeat_v2.ipynb`
**variavam entre execuções** mesmo com sementes fixadas. Dois exemplos concretos
registrados em execuções consecutivas:

| Métrica | Execução N | Execução N+1 | Diferença |
|---------|-----------|--------------|-----------|
| Supraventricular (recall) | 0.766 | 0.743 | 0.023 |
| Fusão ventricular (recall) | 0.852 | 0.821 | 0.031 |
| Recall Anormal global | 0.946 | 0.937 | 0.009 |
| Taxa de falsos negativos | 5.352% | 6.253% | 0.9 pp |

Todas as outras condições de execução foram idênticas: mesmo commit, mesmo
hardware, mesmas bibliotecas, mesma ordem de células. A reprodutibilidade
estrita falhou.

## Por que falhou, apesar das sementes fixadas

O notebook fixa três sementes:

```python
np.random.seed(42)          # NumPy: permutação dos dados, inits pontuais
tf.random.set_seed(42)      # TensorFlow: inicializações de pesos
```

Com `np.random.seed`, o embaralhamento de `X_treino` é determinístico —
produz sempre a mesma permutação de índices. Com `tf.random.set_seed`, a
inicialização dos pesos de cada camada é reproduzível.

O que **não** é controlado por essas sementes: a ordem de execução de
operações paralelas na GPU. Os kernels CUDA do cuDNN usam reduções
paralelas (soma de milhares de valores distribuídos entre threads) e
atômicos (operações concorrentes sobre a mesma posição de memória). A
ordem em que as threads terminam cada redução **não é determinística** —
depende de escalonamento do scheduler da GPU, estado do cache, pressão
de memória, e outros fatores físicos do momento da execução.

E aritmética de ponto flutuante **não é associativa**:

```
(a + b) + c ≠ a + (b + c)   em geral, pra floats
```

Quando a ordem das somas parciais muda entre execuções, o resultado
final difere em bits menos significativos. Esses erros se propagam
pelas camadas da rede, pelo backprop, e pelo otimizador. Ao fim de 50
épocas de treino, pequenas diferenças na terceira casa decimal nas
primeiras iterações viram diferenças na primeira casa decimal nas
métricas finais.

## Evidência: o problema é específico da GPU

Antes da habilitação da GPU (documentada no capítulo X), o notebook
rodava em CPU. Em CPU, a mesma operação com mesmo seed produzia o
mesmo resultado em execuções consecutivas — nenhuma variação observada.
O não-determinismo apareceu exatamente quando o TensorFlow passou a
usar os kernels CUDA do cuDNN.

Isso é coerente com o comportamento documentado pela equipe do TF: a
CPU executa operações sequencialmente em uma única thread (ou em threads
paralelas com redução determinística, pra BLAS single-threaded). A GPU
executa tudo em paralelo, e a redução paralela não-determinística é a
fonte principal de divergência.

## Opções para impor determinismo

O TensorFlow oferece dois mecanismos:

### Opção 1: variável de ambiente

```bash
export TF_DETERMINISTIC_OPS=1
export TF_CUDNN_DETERMINISTIC=1
```

Desabilita implementações não-determinísticas dos kernels cuDNN. O TF
passa a usar versões que garantem saída idêntica entre execuções.

### Opção 2: API Python

```python
tf.config.experimental.enable_op_determinism()
```

Equivalente funcional à opção 1, aplicado em código em vez de ambiente.
Disponível a partir do TF 2.9.

## Trade-off da determinismo estrito

Ambas as opções têm custo:

- **Performance**: kernels determinísticos são, em geral, **20-40% mais
  lentos** do que os não-determinísticos. Operações com redução paralela
  (softmax, batchnorm, attention) perdem mais; operações pontuais
  (ReLU, dropout) não mudam muito.
- **Cobertura incompleta**: nem todas as operações do TF têm versão
  determinística. Se o modelo usa uma op sem suporte, o flag levanta
  erro em vez de silenciosamente executar a versão não-determinística.
- **Interação com outros backends**: em sistemas com múltiplas GPUs ou
  paralelização por `tf.distribute`, o determinismo precisa de
  configuração adicional.

## Decisão tomada neste projeto

**Não habilitar o determinismo estrito por padrão.** Razões:

1. O objetivo acadêmico da atividade é demonstrar o funcionamento da
   MLP, não reproduzir bit-a-bit um experimento. Variação de ±1-2 pp em
   métricas finais não altera a conclusão ("v2 é dramaticamente melhor
   que v1").

2. O treino da MLP já leva ~2 minutos na RTX 4070. Uma penalidade de
   30% de tempo implica em mais atrito pra re-execução durante
   desenvolvimento e ensaio do vídeo.

3. A falha dramática do v1 (recall de 3% vs 94% do v2) é **robusta**
   a essa variação. A variação observada é uma ou duas ordens de
   magnitude menor que o salto demonstrado.

4. Os valores específicos citados em documentação (roteiro de vídeo,
   capítulos de raciocínio) são fotografados **de uma execução
   específica**. Quando uma re-execução produz valores diferentes, os
   documentos são atualizados em seguida — tratando as discrepâncias
   como caducidade controlada, não como bugs.

5. Forçar determinismo no código do notebook imporia o custo de
   performance a todos os executores, inclusive aqueles que não se
   importam com a variação. Deixar o determinismo como **opção
   documentada via variáveis de ambiente** transfere a escolha pra
   quem executa, sem custo por padrão.

## Opção opt-in para usuário final

A seção *Reprodutibilidade* no [README principal do projeto](../../../README.md#reprodutibilidade)
orienta o avaliador ou qualquer executor a habilitar o determinismo
estrito quando desejarem comparar exatamente os valores citados em
documentação. As variáveis de ambiente recomendadas são:

```bash
export TF_DETERMINISTIC_OPS=1
export TF_CUDNN_DETERMINISTIC=1
```

Esse capítulo permanece como referência técnica profunda sobre o
fenômeno; o README entrega a orientação prática de uso.

## Protocolo de atualização de valores

Quando uma re-execução do `mlp_heartbeat_v2.ipynb` produzir valores
materialmente diferentes dos citados em documentação, o procedimento é:

1. Capturar os novos valores exatos dos outputs das células 20
   (recall por classe) e 22 (tabela comparativa e resumo).
2. Atualizar o roteiro `docs/roteiro-video-ir-alem-2a.md` — tanto as
   seções "Na tela" (que citam o output literal) quanto as "Falar"
   (que narram os valores com arredondamento).
3. Atualizar `09-experimentos-v2.md` se os valores de recall global
   em qualquer variante sair da faixa declarada (>1 pp de mudança).
4. Registrar a re-execução em log breve neste capítulo.

Esse protocolo é mais barato a longo prazo que habilitar determinismo
estrito e absorver a penalidade de performance em todas as execuções
futuras.

## Referências

- [TensorFlow docs — `tf.config.experimental.enable_op_determinism`](https://www.tensorflow.org/api_docs/python/tf/config/experimental/enable_op_determinism)
- [NVIDIA — Determinismo em cuDNN e cuBLAS](https://docs.nvidia.com/deeplearning/cudnn/developer-guide/index.html#reproducibility)
- Capítulo [X — Aceleração GPU no Fedora](10-aceleracao-gpu-fedora-secure-boot.md)
  (quando a GPU foi habilitada, introduzindo a estocasticidade)
