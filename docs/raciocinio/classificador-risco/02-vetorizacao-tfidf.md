# II. Vetorização TF-IDF

## O que o TF-IDF faz

O `TfidfVectorizer` do scikit-learn transforma frases em vetores numéricos que os
modelos de classificação consomem. O processo executa 4 etapas internas:

1. **Tokenização** — segmenta cada frase em tokens via regex `\w+` e extrai
   n-grams na faixa especificada
2. **Contagem TF** — calcula a frequência de cada termo em cada documento
3. **Cálculo IDF** — para cada termo t: `idf(t) = log((1 + n) / (1 + df(t))) + 1`,
   onde n = 160 documentos e df(t) = número de documentos que contêm t
4. **Normalização L2** — normaliza cada vetor-documento para norma unitária

## Hiperparâmetros escolhidos

### `ngram_range=(1, 2)`

O vetorizador extrai unigramas ("dor", "peito") e bigramas ("dor peito",
"falta ar"). Em frases médicas curtas, bigramas capturam relações semânticas
que unigramas isolados perdem. O unigrama "peito" aparece em frases de alto
risco ("dor forte no peito") e de baixo risco ("leve queimação no peito após
comer pizza"). O bigrama "no peito" combinado com contexto permite ao modelo
ponderar a coocorrência, não apenas a presença individual.

Trigramas (`ngram_range=(1, 3)`) não justificam inclusão: com 160 frases de
10-20 palavras, a maioria dos trigramas apareceria em menos de 2 documentos e o
`min_df=2` os eliminaria.

### `min_df=2`

Descarta termos que aparecem em apenas 1 documento dentre 160. Um hapax
legomenon (termo de ocorrência única) carrega zero poder de generalização.

### `max_df=0.95`

Descarta termos que aparecem em mais de 95% dos documentos. Termos ubíquos
("sinto", "estou", "com") funcionam como stopwords implícitas — o IDF atribui
peso próximo de zero a esses termos.

## Resultado: matriz 160x379

O vetorizador extraiu 379 termos (unigramas + bigramas) de 160 documentos. A
razão features/amostras (p/n = 2.37) excede 1.0 — o número de features supera
o de observações. Essa configuração favorece modelos com regularização:
- Logistic Regression: regularização L2 (C=1.0) encolhe coeficientes
- Naive Bayes: suavização Laplaciana (alpha=1.0) previne probabilidades zero
- Decision Tree: sofre overfitting severo sem regularização suficiente

A matriz armazena-se em formato CSR (Compressed Sparse Row) porque frases curtas
preenchem no máximo ~30 das 379 colunas — a maioria das células contém zero.
