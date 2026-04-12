# I. Da inspeção ao entendimento: como o dataset revela suas propriedades

## O primeiro ato de qualquer engenheiro diante de dados desconhecidos

Nenhum modelo deve ser construído antes que o engenheiro compreenda a estrutura,
a escala, a distribuição e as anomalias dos dados que o alimentam. Este princípio
não admite exceção. Um modelo treinado sobre dados mal compreendidos produz
resultados numericamente corretos e clinicamente inúteis — a distinção entre ambos
exige que o engenheiro conheça o terreno antes de construir sobre ele.

O script [`scripts/explorar_heartbeat.py`](../../../scripts/explorar_heartbeat.py)
materializa esse princípio. Antes de escrever uma única linha do notebook, o
engenheiro executa o script de exploração para extrair nove categorias de
informação do dataset. O script existe como artefato reproduzível no repositório —
qualquer pessoa pode executá-lo e obter os mesmos achados que determinaram as
decisões subsequentes:

```bash
python scripts/explorar_heartbeat.py
```

Cada operação do script responde a uma pergunta específica, e cada resposta
condiciona uma decisão de design. As subseções seguintes documentam essa cadeia
causal completa.

---

## Operação 1 — Carregamento sem cabeçalho

```python
treino = pd.read_csv(ARQUIVO_TREINO, header=None)
teste = pd.read_csv(ARQUIVO_TESTE, header=None)
```

O MIT-BIH Heartbeat do Kaggle distribui os dados em formato tabular bruto:
nenhuma coluna possui nome, nenhum metadado acompanha o arquivo. O parâmetro
`header=None` instrui o Pandas a tratar todas as linhas como dados, sem promover
a primeira linha a nomes de colunas. O engenheiro que omite `header=None` em um
CSV sem cabeçalho corrompe a primeira linha de dados (um batimento cardíaco real)
como nomes de colunas — erro silencioso que destrói uma amostra e contamina
o schema de tipos de todo o DataFrame.

O script [`exemplos/demo_header_none.py`](exemplos/demo_header_none.py)
demonstra esse efeito no dataset MIT-BIH: o Pandas consome o primeiro batimento
(um registro clínico real de classe Normal, com amplitude inicial de 0.978) como
string de nomes de colunas, reduzindo o dataset de 87.554 para 87.553 amostras
sem emitir nenhum erro ou warning. No caso do MIT-BIH, perder 1 amostra de
87.554 é ruído estatístico — o modelo treina praticamente igual.

A gravidade real do erro, porém, não se mede pelo MIT-BIH. O script
[`exemplos/demo_header_none_catastrofico.py`](exemplos/demo_header_none_catastrofico.py)
demonstra 3 cenários onde a mesma omissão causa resultado catastrófico:

1. **Primeira linha é o único outlier** — um dataset com 100 pacientes onde o
   primeiro é o único caso de arritmia rara. Omitir `header=None` elimina essa
   amostra. O modelo treina com 99 pacientes normais, reporta 100% de acurácia
   (porque só existem amostras normais), e classifica como normal todo batimento
   anormal que encontra em produção. O engenheiro celebra métricas perfeitas. O
   sistema falha em 100% dos casos que justificam sua existência.

2. **Primeira linha contém inteiros que corrompem referências** — um CSV clínico
   onde o primeiro paciente possui valores inteiros (idade=65, pressão=140). O
   Pandas promove esses inteiros como strings de nomes de colunas. Qualquer código
   que acessa colunas por índice inteiro (`df[0]`) falha com `KeyError` porque as
   colunas agora chamam `"65"`, `"140"` — o código quebra em produção sem warning
   prévio.

3. **Dataset pequeno onde 1 amostra é classe inteira** — um dataset com 10
   amostras onde a primeira é o único exemplo de fusão ventricular (classe 3). Ao
   omitir `header=None`, a classe 3 desaparece completamente do dataset. O modelo
   nunca vê um exemplo de fusão. Em datasets clínicos com 50-200 amostras (como o
   Ir Além 2b com 50 imagens de ECG), perder 1 amostra significa perder 2-6% do
   dataset e potencialmente 100% de uma variante clínica rara.

O princípio que justifica sempre usar `header=None` em CSVs sem cabeçalho não
deriva da gravidade do caso MIT-BIH. Deriva do fato de que o engenheiro não sabe,
no momento do carregamento, se a primeira linha é dispensável ou insubstituível. A
verificação custa uma keyword. A omissão custa, no pior caso, um modelo que
reporta métricas perfeitas sobre dados corrompidos.

---

## Operação 2 — Verificação de dimensões

```
Dimensões:
  Treino: 87,554 amostras x 188 colunas
  Teste:  21,892 amostras x 188 colunas
  Features (sinal ECG): 187 amostras por batimento
  Última coluna: classe (target)
```

O treino contém 87.554 linhas e 188 colunas; o teste contém 21.892 linhas e 188
colunas. As 188 colunas dividem-se em 187 amostras do sinal ECG (features) e 1
coluna de classe (target). Este fato não consta na documentação do Kaggle com
clareza suficiente — o engenheiro deduz pela inspeção direta: a última coluna
contém valores discretos (0.0, 1.0, 2.0, 3.0, 4.0) enquanto as 187 primeiras
contêm valores contínuos entre 0 e 1.

**Consequência para a arquitetura:** o `input_dim` da MLP será 187. O `input_dim`
define quantos valores numéricos cada neurônio da primeira camada recebe como
entrada — cada batimento possui 187 amostras do sinal ECG, portanto a rede deve
esperar exatamente 187 valores. A MLP (Perceptron Multicamadas) é uma rede neural
composta por camadas de neurônios totalmente conectados: cada neurônio calcula uma
soma ponderada das entradas, aplica uma função de ativação e passa o resultado à
camada seguinte. Se o `input_dim` não coincide com o número de colunas dos dados,
duas coisas podem acontecer:

Se o engenheiro define `input_dim=187` mas alimenta a rede com 188 colunas
(incluindo a classe), o TensorFlow lança um `ValueError` de shape incompatível —
a rede espera arrays de 187 valores e recebeu 188. O shape é a forma dimensional
do array: um dataset com 100 amostras e 187 features possui shape `(100, 187)`. O
erro interrompe a execução e o engenheiro percebe o problema. Este é o melhor caso.

Se o engenheiro "resolve" definindo `input_dim=188`, o TensorFlow aceita
silenciosamente. A coluna 188 — que contém a classe (0 para Normal, 1 para
Anormal) — entra como feature. A rede descobre em poucas épocas que a coluna 188
prediz perfeitamente o resultado: se o valor é 1.0, a resposta é 1.0. A rede
ignora as 187 features reais (o sinal ECG) e usa exclusivamente a resposta que o
engenheiro entregou como input. A acurácia atinge 100% no treino. O engenheiro
celebra.

Em produção, o paciente chega ao hospital e o médico precisa do diagnóstico — a
coluna de classe não existe no input porque é exatamente o que o modelo deveria
predizer. O TensorFlow recusa o input (shape incompatível) ou, se o engenheiro
preenche a coluna faltante com um valor arbitrário (0.0 ou 1.0), o modelo repete
esse valor como predição. As 187 features do sinal ECG são irrelevantes para a
decisão. O modelo não analisa o paciente — ecoa a resposta que recebeu.

Esse fenômeno chama-se **data leakage** (vazamento de dados): informação do
resultado (target) vaza para as features de entrada, permitindo que o modelo "cole"
em vez de aprender. O leakage é insidioso porque produz métricas perfeitas durante
o desenvolvimento — nenhum erro, nenhum warning, acurácia de 100% — e falha
completamente em produção, onde a resposta não está disponível.

O script [`exemplos/demo_data_leakage.py`](exemplos/demo_data_leakage.py)
demonstra os 4 cenários com código executável: (1) modelo correto com ~50% de
acurácia sobre ruído puro, (2) modelo com leakage atingindo 100% sobre o mesmo
ruído, (3) modelo com leakage em produção produzindo predições que dependem
exclusivamente do valor arbitrário da coluna fantasma, e (4) o erro de shape que
o TensorFlow lança quando `input_dim` e dados possuem dimensões incompatíveis. O
leitor executa `python docs/raciocinio/mlp-heartbeat/exemplos/demo_data_leakage.py`
e verifica que um modelo com 100% de acurácia pode ser completamente inútil.

---

## Operação 3 — Distribuição de classes

O script computa a contagem e o percentual de cada classe, apresentando barras
de frequência proporcional para tornar o desbalanceamento visualmente inequívoco:

```
Distribuição de classes (treino):
--------------------------------------------------
  Classe 0 Normal (N)               : 72,471 ( 82.8%) #################################
  Classe 1 Supraventricular (S)     :  2,223 (  2.5%) #
  Classe 2 Ventricular (V)          :  5,788 (  6.6%) ##
  Classe 3 Fusão (F)                :    641 (  0.7%)
  Classe 4 Desconhecido (Q)         :  6,431 (  7.3%) ##
```

A barra visual cumpre uma função que a tabela numérica sozinha não cumpre: torna
impossível não perceber que a classe 0 domina o dataset com 33 caracteres de barra,
enquanto a classe 3 (Fusão) não produz sequer um caractere. A desproporção é de
113:1 entre Normal e Fusão (72.471 vs 641). Nenhum engenheiro que visualize essa
distribuição pode defender um treinamento sem compensação de classe.

---

## Operação 4 — Distribuição binária

```
Distribuição binária (Normal vs Anormal):
  Normal:  72,471 (82.8%)
  Anormal: 15,083 (17.2%)
  Razão Normal/Anormal: 4.8x
```

A binarização (classes 1-4 agrupadas como "Anormal") produz razão de 4.8:1. Cada
amostra Normal representa uma fração 4.8 vezes menor do sinal de aprendizado que
cada amostra Anormal deveria representar. O número 4.8x é o fator que o
`class_weight` do scikit-learn precisa compensar — e o script calcula exatamente
esse valor na operação 9.

---

## Operação 5 — Range dos valores

```
Range dos valores do sinal:
  Mínimo global: 0.000000
  Máximo global: 1.000000
  Média global:  0.174283
  Desvio padrão: 0.226327
```

O mínimo de 0.000000 e o máximo de 1.000000 confirmam que o dataset já chega
normalizado. A média de 0.174 (próxima de zero) e o desvio padrão de 0.226
revelam que a maioria das amostras concentra-se em valores baixos — os sinais
ECG possuem um pico rápido (complexo QRS) seguido de retorno à linha de base. Essa
distribuição assimétrica informa que os inputs da MLP são predominantemente
próximos de zero, o que favorece ativações ReLU (que operam no regime linear para
valores positivos e zerificam valores negativos — sem negativos, sem dying ReLU).

**Consequência para o pré-processamento:** nenhuma transformação de escala é
necessária. Aplicar MinMaxScaler sobre dados já em [0, 1] seria uma operação
idempotente que revelaria desconhecimento do engenheiro sobre os dados que
manipula. Aplicar StandardScaler (z-score) centraria a média em zero, introduzindo
valores negativos que poderiam ativar o regime de zerificação do ReLU em parte dos
neurônios — uma transformação que prejudicaria em vez de ajudar.

---

## Operação 6 — Amostra concreta

```
Amostra do primeiro batimento (primeiras 10 de 187 amostras):
  [0.97794116 0.92647058 0.68137252 0.24509804 0.15441176 0.19117647
   0.15196079 0.08578432 0.05882353 0.04901961]
```

A amostra concreta revela o formato do sinal: começa em valor alto (~0.98), cai
rapidamente para ~0.05 e permanece baixo. Esse padrão corresponde à despolarização
ventricular (complexo QRS) seguida pela linha de base. O engenheiro que inspeciona
ao menos uma amostra confirma que os dados possuem estrutura temporal coerente
com fisiologia cardíaca — não são ruído, não estão corrompidos, não possuem
artefatos de padding ou truncamento visíveis.

---

## Operação 7 — Valores ausentes

```
Valores ausentes:
  Treino: 0
  Teste:  0
```

Zero valores ausentes em ambos os conjuntos. Esta verificação elimina a necessidade
de estratégias de imputação (média, mediana, KNN, interpolação). Datasets clínicos
reais frequentemente possuem dados faltantes — o MIT-BIH já passou por curadoria
que eliminou ou interpolou ausências. O engenheiro que assume completude sem
verificar arrisca NaN propagados silenciosamente pelo pipeline inteiro, produzindo
losses de treino iguais a NaN e um modelo que retorna NaN para toda predição.

---

## Operação 8 — Consistência treino/teste

```
Consistência treino/teste (proporções devem ser similares):
  Classe                      Treino    Teste     Diff
  -------------------------------------------------
  Normal (N)                   82.8%    82.8%     0.0%
  Supraventricular (S)          2.5%     2.5%     0.0%
  Ventricular (V)               6.6%     6.6%     0.0%
  Fusão (F)                     0.7%     0.7%     0.0%
  Desconhecido (Q)              7.3%     7.3%     0.0%
```

A diferença de 0.0% entre treino e teste em todas as 5 classes confirma que o
split do Kaggle é estratificado — a proporção de cada classe permanece idêntica
em ambos os conjuntos. Esta informação possui duas consequências:

**Primeira:** o engenheiro pode confiar que as métricas do conjunto de teste
refletem a mesma distribuição do treino. Se o split não fosse estratificado (ex:
teste com 90% Normal e 10% Anormal), as métricas do teste seriam enviesadas em
relação ao treino.

**Segunda:** não há necessidade de re-estratificar manualmente. O `train_test_split`
do scikit-learn com `stratify=y` seria necessário se o engenheiro precisasse criar
sua própria divisão — o Kaggle já fornece essa divisão pronta.

---

## Operação 9 — Class weight

```
class_weight calculado (para compensar desbalanceamento):
  Normal (0):  0.6041
  Anormal (1): 2.9024
  Fator de amplificação Anormal: 4.8x
```

O scikit-learn calcula `class_weight("balanced")` pela fórmula
`n_amostras / (n_classes * n_amostras_classe)`. Para o MIT-BIH binarizado:
- Normal (72.471 amostras): 87.554 / (2 × 72.471) = 0.6041
- Anormal (15.083 amostras): 87.554 / (2 × 15.083) = 2.9024

O peso 2.9024 amplifica o gradiente de cada amostra anormal por 2.9x. O peso
0.6041 atenua o gradiente de cada amostra normal por 0.4x. O efeito líquido: a
rede trata o dataset como se ambas as classes possuíssem representação igual. O
fator 4.8x (2.9024 / 0.6041) é exatamente a razão Normal/Anormal calculada na
operação 4 — a aritmética fecha.

---

## Síntese: as 6 conclusões que o script produz

O script encerra com uma seção de conclusões que o notebook herda como premissas:

```
CONCLUSÕES PARA O NOTEBOOK
============================================================
  1. Dados já normalizados [0, 1] — MinMaxScaler desnecessário
  2. Sem valores ausentes — nenhuma imputação necessária
  3. Desbalanceamento severo (82.8% vs 17.2%) — class_weight obrigatório
  4. Proporções treino/teste consistentes — split do Kaggle é estratificado
  5. 187 features por batimento — input_dim=187 na MLP
  6. Acurácia baseline (sempre Normal): 82.8%
     Qualquer modelo deve superar 82.8% para ter valor
```

A conclusão 6 estabelece o limiar de utilidade do modelo: 82.8% de acurácia é o
piso que qualquer classificador trivial atinge ao predizer sempre "Normal".
Qualquer acurácia abaixo ou igual a esse valor demonstra que o modelo não aprendeu
nenhum padrão discriminativo. Qualquer acurácia acima desse valor — e somente
acima — constitui evidência de que o modelo distingue Normal de Anormal com base
nas features do sinal, não na prevalência de classe.

---

## Como interpretar o desbalanceamento

O desbalanceamento possui três implicações que o engenheiro deve internalizar
antes de prosseguir:

**Primeira implicação: a acurácia mente.** Uma métrica que atribui peso igual a
cada amostra reflete a classe majoritária. Com 82.8% de amostras normais, um
modelo perfeito na classe Normal e completamente cego à classe Anormal obtém 82.8%
de acurácia. A métrica não distingue entre "modelo que aprendeu" e "modelo que
memoriza a base rate". Portanto, o recall da classe minoritária (Anormal) é a
métrica que revela se o modelo possui capacidade discriminativa real.

**Segunda implicação: o gradiente é dominado pela classe majoritária.** Durante o
treinamento, a loss function (binary crossentropy) soma os erros de todas as
amostras. Com 82.8% de amostras normais, 82.8% do gradiente orienta os pesos na
direção que classifica corretamente amostras normais — a classe minoritária
contribui com apenas 17.2% do sinal de aprendizado. Sem compensação, a rede
converge para um mínimo local onde prediz "Normal" para quase tudo, porque esse
mínimo possui loss baixa na maioria das amostras.

**Terceira implicação: o custo clínico é assimétrico.** Um falso negativo
(classificar batimento anormal como normal) significa que uma arritmia
potencialmente fatal passa despercebida. Um falso positivo (classificar batimento
normal como anormal) dispara uma investigação desnecessária — custo operacional,
não clínico. Em triagem cardiológica, o sistema deve errar no sentido da cautela:
é preferível investigar 100 alarmes falsos a deixar passar 1 arritmia ventricular.
