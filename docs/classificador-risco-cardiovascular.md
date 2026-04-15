# Classificador de Risco Cardiovascular

Documento técnico sobre o pipeline de classificação binária de risco implementado em `notebooks/classificador_risco.ipynb`. O notebook transforma 160 frases clínicas em vetores TF-IDF e treina 3 modelos de Machine Learning (Logistic Regression, Decision Tree, Multinomial Naive Bayes) para classificação binária (alto risco vs. baixo risco).

---

## 1. Visão geral — Por que classificação binária de risco com TF-IDF

### Complementaridade, não redundância

O repositório contém duas abordagens de NLP clínico que resolvem problemas distintos:

O pipeline `cardio_extrator/` opera por regras determinísticas — identifica sintomas específicos via regex, qualifica-os semiologicamente, detecta negações contextuais e pontua diagnósticos via mapa de conhecimento JSON. O classificador TF-IDF opera por aprendizado estatístico — captura padrões lexicais emergentes que nenhum especialista antecipou durante a engenharia do vocabulário regex. Um profissional de domínio precisa escrever manualmente cada expressão regular do pipeline de extração; o classificador TF-IDF descobre automaticamente que o bigrama "últimos dias" coocorre predominantemente em frases de alto risco sem que ninguém tenha codificado essa relação.

O pipeline de extração responde "quais sintomas o paciente relata e qual doença eles sugerem" (diagnóstico multiclasse entre 8 doenças). O classificador TF-IDF responde "este paciente precisa de avaliação urgente?" (triagem binária). Protocolos de triagem como Manchester e ESI operam nessa lógica de faixas de risco antes de definir diagnóstico específico — o classificador replica esse nível de abstração.

### Coerência com o enunciado da atividade

A Parte 2 da Fase 2 exige explicitamente "aplicar o método TF-IDF para transformar frases em vetores numéricos" e "escolher um modelo de classificação simples do Scikit-learn". O notebook cumpre o enunciado e excede em 5 dimensões:

1. Treina 3 modelos em vez de 1 (custo marginal mínimo com scikit-learn)
2. Avalia com Stratified 5-Fold em vez de train/test split simples
3. Reporta precision, recall e F1 por classe em vez de apenas acurácia
4. Analisa coeficientes da Logistic Regression para identificar termos discriminativos
5. Testa com 10 frases fora do dataset incluindo casos ambíguos

### Por que classificação binária e não multiclasse

O pipeline de extração já cobre diagnóstico multiclasse (8 doenças cardiovasculares). A classificação binária de risco resolve um problema ortogonal: decidir se um paciente precisa de avaliação urgente independente do diagnóstico específico. Um paciente com suspeita de SCA (Síndrome Coronariana Aguda) e um paciente com IC descompensada pertencem ambos à classe "alto risco" apesar de diagnósticos diferentes — o nível de urgência, não a etiologia, determina a decisão de triagem.

### Por que TF-IDF e não embeddings

A matriz TF-IDF de 160 frases curtas resulta em 160x379 dimensões que 3 classificadores simples consomem em milissegundos. Word2Vec ou FastText exigiriam corpus de pré-treino em português clínico ou modelo pré-treinado de centenas de megabytes que a stdlib do Python não fornece. BERTimbau (BERT-base em português) exigiria ~440MB de modelo mais GPU para fine-tuning com apenas 160 exemplos — a razão amostras/parâmetros (~160/110M) garantiria overfitting catastrófico. TF-IDF captura frequências de termos e coocorrências de bigramas que, para frases curtas com vocabulário médico restrito, contém informação discriminativa suficiente para F1-macro de 0.856 — performance que embeddings densos dificilmente superariam neste volume de dados.

---

## 2. Engenharia do dataset — Construção e rotulação de `frases_risco.csv`

### Estrutura

O arquivo contém 160 frases em 2 colunas (`frase`, `situacao`), com distribuição 81 alto risco (50.6%) e 79 baixo risco (49.4%). O balanceamento quase perfeito (51/49) elimina o viés de classe majoritária: com distribuição desbalanceada (ex: 80/20), um classificador trivial que sempre prediz a classe majoritária obteria 80% de acurácia sem aprender nenhum padrão discriminativo. O balanceamento 50/50 força o modelo a discriminar com base no conteúdo lexical, não na prevalência de classe.

### Critérios de rotulação

| Rótulo | Critério clínico |
|--------|-----------------|
| **alto risco** | Sintomas sugestivos de emergência cardiovascular: dor torácica opressiva ou com irradiação (MSE, mandíbula, trapézio), dispneia aguda, síncope, palpitações com instabilidade hemodinâmica, sinais de IC descompensada (ortopneia, DPN, edema), combinação dor torácica + sudorese/náusea (tríade de SCA) |
| **baixo risco** | Queixas benignas ou crônicas estáveis: dor musculoesquelética localizada e reprodutível à palpação, cansaço leve que resolve com repouso, incômodo passageiro (segundos), sintomas inespecíficos sem urgência (azia, câimbra, dor articular) |
| **ambíguas (~15-20%)** | Sintomas na fronteira clínica: dor torácica atípica, palpitações isoladas sem instabilidade, tontura posicional sem contexto cardiovascular, dispneia crônica leve em sedentário, dor que o paciente não sabe classificar |

### Exemplos representativos

**Alto risco (inequívoco):**

| Frase | Justificativa clínica |
|-------|----------------------|
| "sinto dor no peito acompanhada de suor frio e náusea" | Tríade clássica de SCA: dor torácica + sudorese + náusea |
| "acordo no meio da noite sufocado sem conseguir respirar" | Dispneia paroxística noturna — critério maior de Framingham para IC |
| "tive perda de consciência e quando voltei sentia dor no peito" | Síncope com dor torácica sugere arritmia grave ou SCA |
| "estou com inchaço nas pernas e não consigo deitar para dormir" | Edema periférico + ortopneia — sinais de IC descompensada |
| "sinto dor no peito que vai para a mandíbula e o pescoço" | Irradiação para mandíbula tem alta especificidade para DAC (LR+ ~5.0) |

**Baixo risco (inequívoco):**

| Frase | Justificativa clínica |
|-------|----------------------|
| "tive um leve incômodo nas costas depois de carregar peso" | Dor musculoesquelética com causa mecânica identificável |
| "sinto uma fisgada rápida no peito que passou em segundos" | Dor fugaz (segundos) sem relação com esforço — baixo valor preditivo para isquemia |
| "estou com dor no joelho que piora ao descer escada" | Queixa articular sem componente cardiovascular |
| "tenho sentido azia frequente depois do jantar" | Sintoma gastrointestinal típico (refluxo pós-prandial) |
| "sinto as juntas doendo quando muda o tempo" | Artralgia meteorotrópica — sem relevância cardiovascular |

**Ambíguas (rotulação deliberada):**

| Frase | Rótulo | Justificativa |
|-------|--------|---------------|
| "sinto uma dor no peito que aparece quando faço esforço mas não sei se é grave" | alto risco | Dor torácica desencadeada por esforço satisfaz critério Diamond-Forrester para angina típica, independente da percepção subjetiva do paciente |
| "tenho palpitações de vez em quando mas não sinto mais nada" | baixo risco | Palpitações isoladas sem instabilidade hemodinâmica, sem síncope e sem sintomas associados possuem baixo valor preditivo positivo para arritmia maligna |
| "sinto uma pressão no peito que vai e vem sem padrão definido" | alto risco | Desconforto torácico recorrente sem padrão claro exige investigação — o critério clínico favorece sensibilidade sobre especificidade em triagem |
| "estou com palpitações que aparecem depois de tomar café em excesso" | baixo risco | Cafeína provoca extrassístoles benignas; o gatilho identificável e a ausência de sintomas associados reduzem a probabilidade de etiologia maligna |
| "sinto uma dor no braço esquerdo que não sei se é muscular ou do coração" | alto risco | Dor em membro superior esquerdo de etiologia incerta requer investigação cardiovascular — o erro de classificar como baixo risco (falso negativo) tem custo assimétrico inaceitável |

### Limitações da rotulação

Um único rotulador (estudante de IA, não cardiologista) classificou todas as 160 frases com base em critérios semiológicos documentados na referência clínica do projeto. O Cohen's Kappa interanotador não pode ser calculado sem segundo anotador independente. Em NLP clínico de produção, o padrão mínimo exige 2-3 anotadores com concordância Kappa >= 0.80. O viés do rotulador único pode manifestar-se como consistência artificial — frases que um cardiologista rotularia diferentemente (ex: "tontura ao levantar rápido" como alto risco por suspeita de hipotensão ortostática) podem estar rotuladas como baixo risco por interpretação não-especializada.

---

## 3. Vetorização TF-IDF — Transformação de texto em representação numérica

### Configuração do vetorizador

```python
TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.95)
```

### `ngram_range=(1, 2)`: unigramas e bigramas

O vetorizador extrai tokens individuais (unigramas: "dor", "peito", "falta") e pares de tokens adjacentes (bigramas: "dor peito", "falta ar", "braço esquerdo"). Em frases médicas curtas, bigramas capturam relações semânticas que unigramas isolados perdem. O unigrama "peito" aparece em frases de alto risco ("dor forte no peito") e de baixo risco ("leve queimação no peito após comer pizza"). O bigrama "no peito" combinado com contexto ("dor forte no peito" vs. "queimação no peito") permite ao modelo ponderar a coocorrência, não apenas a presença individual.

Trigramas (`ngram_range=(1, 3)`) não justificam inclusão neste dataset: com 160 frases de 10-20 palavras, a maioria dos trigramas apareceria em menos de 2 documentos e o `min_df=2` os eliminaria, desperdiçando memória na construção do vocabulário sem contribuir com features que sobrevivam ao filtro.

### `min_df=2`: frequência mínima de documento

O vetorizador descarta termos que aparecem em apenas 1 documento dentre 160. Um hapax legomenon (termo de ocorrência única) carrega zero poder de generalização — o modelo não pode aprender padrão de risco a partir de uma única ocorrência. Sem este filtro, o vocabulário incluiria dezenas de termos raros que inflariam a dimensionalidade da matriz sem contribuir para a discriminação entre classes.

### `max_df=0.95`: frequência máxima de documento

O vetorizador descarta termos que aparecem em mais de 95% dos documentos (mais de 152 das 160 frases). Termos ubíquos ("sinto", "estou", "com", "uma") funcionam como stopwords implícitas — o cálculo de IDF atribui peso próximo de zero a esses termos (`log((1 + 160) / (1 + 152)) + 1 ≈ 1.05`), e incluí-los na matriz desperdiça colunas com informação negligenciável. O threshold de 0.95 em vez de 0.90 preserva termos médicos frequentes mas potencialmente discriminativos (ex: "peito" aparece em ~40% das frases e carrega forte sinal de risco); o threshold de 1.0 (sem filtro) manteria stopwords puras que o modelo precisaria aprender a ignorar.

### Dimensões resultantes: 160x379

O vetorizador extraiu 379 termos (unigramas + bigramas) de 160 documentos. A razão features/amostras (p/n = 379/160 = 2.37) excede 1.0, indicando que o número de features supera o de observações. Esta configuração favorece modelos com regularização implícita ou explícita: a Logistic Regression aplica regularização L2 por padrão (C=1.0) que encolhe coeficientes de features pouco informativas; o Naive Bayes aplica suavização Laplaciana que previne probabilidades zero. A Decision Tree sem regularização suficiente (max_depth=10 permite 1024 folhas para 160 amostras) sofre overfitting severo — exatamente o que os resultados confirmam (66.2% F1 vs 85.6%).

### Mecanismo interno do TF-IDF

O scikit-learn executa 4 etapas internas ao chamar `fit_transform()`:

1. **Tokenização**: segmenta cada frase em tokens via regex `\w+` e extrai n-grams na faixa especificada
2. **Contagem TF**: calcula a frequência de cada termo em cada documento (term frequency bruta)
3. **Cálculo IDF**: para cada termo t no vocabulário, calcula `idf(t) = log((1 + n) / (1 + df(t))) + 1`, onde n = número de documentos (160) e df(t) = número de documentos que contêm t. A constante +1 no numerador e denominador aplica suavização Laplaciana; o +1 final evita que termos ausentes recebam peso zero
4. **Normalização L2**: para cada documento d, normaliza o vetor TF-IDF para norma unitária (`||v_d||_2 = 1`), garantindo que documentos longos e curtos contribuam igualmente

O resultado é uma matriz esparsa CSR (Compressed Sparse Row). Para 160x379 = 60.640 células teóricas, a maioria contém zero (frases curtas de 10-20 palavras preenchem no máximo ~30 das 379 colunas). O formato CSR armazena apenas valores não-zero com seus índices de coluna, reduzindo o consumo de memória de ~480KB (denso, float64) para ~20-30KB (esparso).

### Top-20 termos por IDF

Os termos com maior IDF aparecem em poucos documentos, o que eleva o denominador `(1 + df(t))` e consequentemente o logaritmo. Termos como "aguda" (idf=4.98), "últimos dias" (idf=4.98), "batimentos" (idf=4.98) e "cardíaco" (idf=4.98) aparecem em 1-2 documentos cada — termos raros que, quando presentes, atuam como sinais fortemente discriminativos.

---

## 4. Modelos de classificação — Escolha, hiperparâmetros e mecanismo interno

### 4.1 Logistic Regression

**Baseline para classificação binária de texto.** A Logistic Regression modela diretamente a probabilidade posterior P(y=classe|x) aplicando a função sigmoide a uma combinação linear dos 379 termos TF-IDF. A linearidade é uma força para representações TF-IDF de alta dimensionalidade — o teorema de Cover estabelece que dados em espaço de alta dimensão tendem a ser linearmente separáveis.

**Hiperparâmetros:**
- `max_iter=1000`: garante convergência do solver L-BFGS em espaço de 379 dimensões. O padrão de 100 iterações pode não bastar para convergência quando p > n.
- `random_state=42`: reprodutibilidade.
- `C=1.0` (padrão): inverso da força de regularização L2. A regularização L2 encolhe coeficientes de features pouco informativas em direção a zero sem eliminá-los. Com p/n = 2.37, a regularização L2 previne overfitting distribuindo peso entre features correlacionadas em vez de concentrar em uma única.

**Análise de coeficientes:**

O scikit-learn ordena as classes lexicograficamente: `sorted(["alto risco", "baixo risco"])` produz `classes_ = ["alto risco", "baixo risco"]`, logo `alto risco = índice 0` e `baixo risco = índice 1`. Na classificação binária, `coef_[0]` contém um único vetor: **coeficientes positivos apontam para a classe de índice 1 ("baixo risco")** e **coeficientes negativos apontam para a classe de índice 0 ("alto risco")**.

O notebook original exibe "Top-15 termos indicativos de ALTO RISCO" ordenando por coeficiente decrescente (positivo). Essa rotulação inverte a interpretação real — os coeficientes positivos indicam "baixo risco", não "alto risco". A tabela correta:

**Termos indicativos de BAIXO RISCO (coeficientes positivos, classe índice 1):**

| Termo | Coeficiente | Interpretação |
|-------|-------------|---------------|
| leve | +1.190 | Adjetivo minimizador: "dor leve", "cansaço leve", "leve desconforto" |
| na | +0.827 | Preposição em contextos de baixo risco: "dor na lombar", "dor na costela" |
| com uma | +0.805 | Bigrama em queixas benignas: "estou com uma dor leve" |
| uma leve | +0.785 | Bigrama minimizador: "uma leve queimação", "uma leve falta de ar" |
| quando | +0.776 | Condicional em contextos benignos: "piora quando levanto peso" |
| depois | +0.746 | Temporalidade pós-evento benigno: "depois de academia", "depois de comer" |

**Termos indicativos de ALTO RISCO (coeficientes negativos, classe índice 0):**

| Termo | Coeficiente | Interpretação |
|-------|-------------|---------------|
| no peito | -0.937 | Bigrama cardinal de sintoma cardiovascular |
| peito | -0.935 | Unigrama complementar ao bigrama |
| sinto dor | -0.892 | Bigrama de relato ativo de dor |
| tive | -0.835 | Verbo em relato de evento agudo: "tive um desmaio", "tive dor" |
| para | -0.787 | Preposição em irradiação: "irradia para o braço" |
| esforço | -0.644 | Desencadeante cardiovascular: dor ou dispneia ao esforço |
| não | -0.607 | Termos de gravidade: "não melhora", "não para", "não alivia" |
| forte | -0.550 | Intensificador: "dor forte", "palpitações fortes" |
| falta de | -0.539 | Bigrama de dispneia: "falta de ar" |
| de ar | -0.539 | Complemento de "falta de ar" |
| há | -0.513 | Temporalidade de persistência: "há três dias", "há semanas" |

A colinearidade entre bigramas e unigramas distribui o peso: "falta" (-0.539), "de ar" (-0.539), "falta de" (-0.539) e "ar" (-0.539) medem parcialmente o mesmo fenômeno ("falta de ar"). A regularização L2 distribui o coeficiente entre features correlacionadas, evitando que um único termo receba peso extremo.

### 4.2 Decision Tree

**Modelo interpretável com splits axiais.** A árvore cria fronteiras de decisão perpendiculares a cada feature em espaço de 379 dimensões. Para aprender que a combinação "dor + peito + irradia + braço" indica alto risco, a árvore precisa de múltiplos splits sequenciais (um por termo), cada split reduzindo o número de amostras nos nós filhos.

**Hiperparâmetros:**
- `max_depth=10`: permite até 2^10 = 1024 folhas para 160 amostras — restrição insuficiente. A árvore cresce até perto de pureza total, memorizando padrões específicos do dataset.
- `random_state=42`: reprodutibilidade na seleção de features para split quando há empate.

**Por que F1 de 0.658 vs 0.856:** com 160 amostras em 379 dimensões, nós profundos contêm poucas observações e as estimativas de classe tornam-se instáveis (alta variância). A Logistic Regression e o Naive Bayes combinam todas as 379 features em uma única decisão global — abordagem intrinsecamente mais adequada para dados textuais esparsos de alta dimensionalidade. A árvore operaria melhor com `max_depth=3` ou `max_depth=5` (bias mais alto, variância menor), mas o overfitting com `max_depth=10` demonstra didaticamente o trade-off bias-variância.

### 4.3 Multinomial Naive Bayes

**Modelo probabilístico para dados de contagem.** O MultinomialNB assume independência condicional entre features dado a classe — premissa que o TF-IDF viola (bigramas dependem dos unigramas que os compõem). Apesar dessa violação teórica, o Naive Bayes classifica texto com performance competitiva na prática porque o viés na estimativa de probabilidade afeta ambas as classes proporcionalmente — a decisão de classificação (argmax) permanece correta mesmo quando as probabilidades absolutas estão incorretas.

**Suavização Laplaciana (alpha=1.0):** o parâmetro padrão adiciona 1 pseudocontagem a cada feature em cada classe. Sem suavização, uma feature que aparece em documentos de uma classe mas nunca na outra geraria probabilidade zero, e o produtório bayesiano colapsaria para zero independente de todas as outras features. Com 379 features e 160 documentos, muitas features possuem contagem zero em uma classe, tornando a suavização obrigatória. A suavização cumpre papel análogo à regularização L2 da Logistic Regression — encolhe as estimativas de probabilidade em direção à distribuição uniforme, prevenindo overfitting a features raras.

---

## 5. Estratégia de avaliação — Stratified K-Fold Cross-Validation

### Por que não train/test split simples

Com 160 frases, um split 80/20 produziria um conjunto de teste com 32 frases. O intervalo de confiança de 95% para acurácia com n=32, assumindo acurácia verdadeira de 85%: `1.96 * sqrt(0.85 * 0.15 / 32) = 0.124` — incerteza de 12.4 pontos percentuais. Essa margem torna qualquer comparação entre modelos estatisticamente inútil.

### Por que Stratified

Sem estratificação, a aleatoriedade da divisão poderia concentrar desproporcionalmente uma classe em um fold (ex: 25 alto risco e 7 baixo risco), inflando métricas da classe majoritária naquele fold. A estratificação força cada fold a manter a proporção 51/49 do dataset completo — cada fold de teste contém ~16 frases de alto risco e ~16 de baixo risco.

### Por que k=5 e não k=10

Com 160 amostras, k=10 produziria folds de teste com 16 amostras — poucos para estimativa confiável por fold. k=5 produz folds de teste com 32 amostras e folds de treino com 128 amostras. k=160 (Leave-One-Out) eliminaria viés de estimação mas produziria alta variância entre folds e custo computacional desnecessário.

### `shuffle=True, random_state=42`

O CSV contém frases parcialmente ordenadas por rótulo (as primeiras ~56 frases pertencem a "alto risco", as ~54 seguintes a "baixo risco", as últimas ~50 intercalam ambíguas). O shuffle aleatoriza a ordem antes de dividir em folds, eliminando viés de ordenação. O `random_state=42` garante reprodutibilidade.

### Resultados completos

| Modelo | Acurácia | Precision (macro) | Recall (macro) | F1-macro |
|--------|----------|-------------------|----------------|----------|
| Logistic Regression | 0.856 +/- 0.037 | 0.856 +/- 0.038 | 0.856 +/- 0.037 | 0.856 +/- 0.037 |
| Decision Tree | 0.662 +/- 0.050 | 0.670 +/- 0.055 | 0.661 +/- 0.049 | 0.658 +/- 0.049 |
| Naive Bayes | 0.856 +/- 0.051 | 0.857 +/- 0.051 | 0.857 +/- 0.051 | 0.856 +/- 0.051 |

O desvio padrão maior do Naive Bayes (0.051 vs 0.037 da LR) indica maior sensibilidade à composição de cada fold — as estimativas de probabilidade bayesianas flutuam mais com conjuntos de treino pequenos porque a suavização Laplaciana domina quando as contagens por classe por feature são baixas.

---

## 6. Matrizes de confusão — Análise de erros

### Treino completo vs Cross-Validation

| Modelo | F1 treino | F1 CV | Gap (overfitting) |
|--------|-----------|-------|-------------------|
| Logistic Regression | 0.97 | 0.856 | 11.4 pp |
| Decision Tree | 0.97 | 0.658 | 31.2 pp |
| Naive Bayes | 0.96 | 0.856 | 10.4 pp |

A Decision Tree apresenta overfitting severo (31.2 pontos percentuais de gap): memoriza splits específicos do dataset que não transferem para dados novos. A Logistic Regression apresenta overfitting moderado (11.4pp). O Naive Bayes apresenta o menor gap (10.4pp) porque seus parâmetros (probabilidades condicionais suavizadas) possuem menor capacidade de memorização que coeficientes livres.

### Custo assimétrico de erros

Em triagem cardiovascular, um falso negativo (classificar "alto risco" como "baixo risco") significa que um paciente com possível emergência cardiovascular não receberia avaliação urgente — risco de morte. Um falso positivo (classificar "baixo risco" como "alto risco") significa encaminhamento desnecessário — custo operacional sem risco clínico. O recall da classe "alto risco" mede a proporção de pacientes verdadeiramente em risco que o modelo identifica corretamente. No treino completo, a Logistic Regression alcança recall de 0.96 para "alto risco" e o Naive Bayes alcança 0.95 — ambos aceitáveis para triagem.

---

## 7. Teste com frases fora da distribuição

| # | Frase | LR | DT | NB | Consenso |
|---|-------|----|----|-----|----------|
| 1 | "sinto uma dor forte no peito que irradia para o braço e tenho suor frio" | alto (0.73) | alto (0.89) | alto (0.87) | 3/3 correto |
| 2 | "tenho uma dor leve no ombro depois de jogar bola" | baixo (0.74) | baixo (1.00) | baixo (0.85) | 3/3 correto |
| 3 | "acordo com falta de ar intensa e preciso sentar para respirar" | alto (0.81) | alto (1.00) | alto (0.91) | 3/3 correto |
| 4 | "sinto uma leve queimação no peito após comer pizza" | baixo (0.67) | baixo (1.00) | baixo (0.81) | 3/3 correto |
| 5 | "tive um desmaio durante uma corrida e meu pai morreu do coração" | alto (0.65) | alto (0.89) | alto (0.77) | 3/3 correto |
| 6 | "estou com dor nas costas que piora quando levanto peso" | baixo (0.66) | baixo (1.00) | baixo (0.78) | 3/3 correto |
| 7 | "sinto palpitações fortes com dor no peito e tontura" | alto (0.67) | alto (1.00) | alto (0.68) | 3/3 correto |
| 8 | "tenho um cansaço leve no final do dia que melhora com repouso" | baixo (0.66) | baixo (1.00) | baixo (0.81) | 3/3 correto |
| 9 | "sinto uma pressão estranha no peito mas não sei se é do estômago" | alto (0.60) | alto (1.00) | alto (0.66) | 3/3 correto (baixa confiança) |
| 10 | "estou com falta de ar e inchaço nas pernas que não melhora" | alto (0.74) | alto (1.00) | alto (0.85) | 3/3 correto |

### Análise da frase mais desafiadora (frase 9)

"sinto uma pressão estranha no peito mas não sei se é do estômago" — a Logistic Regression classifica como alto risco com confiança de apenas 0.60. O termo "pressão" e o bigrama "no peito" contribuem com coeficientes negativos fortes (apontando para alto risco), mas "estômago" puxa para baixo risco (associado a queixas gastrointestinais no dataset). O conflito entre features produz probabilidade próxima de 0.50, demonstrando que o modelo captura corretamente a incerteza clínica da frase. A classificação como alto risco é clinicamente defensável: em triagem, desconforto torácico de etiologia incerta exige investigação — o custo de ignorar uma SCA supera o de investigar refluxo gastroesofágico.

### Validação clínica

- **Frases 1, 3, 7, 10**: alto risco correto — combinam múltiplos critérios de emergência cardiovascular (dor torácica + irradiação, dispneia aguda, palpitações + dor + tontura, dispneia + edema)
- **Frases 2, 4, 6, 8**: baixo risco correto — queixas musculoesqueléticas com causa mecânica, sintomas gastrointestinais, cansaço fisiológico
- **Frase 5**: alto risco correto com confiança moderada (0.65 LR) — síncope de esforço com histórico familiar positivo satisfaz critérios de investigação cardiológica urgente
- **Frase 9**: alto risco correto com baixa confiança (0.60 LR) — a incerteza reflete a ambiguidade real da queixa

---

## 8. Relação entre o classificador TF-IDF e o pipeline de extração

### O que o TF-IDF captura que o regex não captura

O vetorizador descobre automaticamente que bigramas como "últimos dias", "com uma" e "uma leve" possuem poder discriminativo sem que ninguém tenha escrito expressões regulares para eles. Padrões estatísticos emergentes — coocorrências de termos que nenhum especialista antecipou — constituem a força do aprendizado supervisionado. O pipeline regex exige engenharia manual de cada padrão.

### O que o regex captura que o TF-IDF não captura

O pipeline `cardio_extrator` distingue "tenho dor no peito" (positivo) de "não tenho dor no peito" (negado) via motor de negação contextual com janela de tokens e delimitadores de escopo. O TF-IDF trata "não" como token independente que pode coocorrer com "dor" no mesmo documento sem modelar a relação posicional de negação. Bigramas como "não tenho" e "não sinto" capturam parte da negação, mas não o escopo: na frase "não tenho dor no peito, mas sinto falta de ar", o motor de negação do `cardio_extrator` nega apenas "dor" (escopo encerrado pela vírgula), enquanto o TF-IDF trata todos os termos como bag-of-words sem distinção de escopo.

### Hipótese de ensemble

As duas abordagens poderiam combinar-se em um sistema futuro: o pipeline de extração produz features estruturadas (presença/ausência de 22 sintomas, 16 qualificadores, 3 contextos, 6 fatores de risco) que poderiam concatenar-se ao vetor TF-IDF de 379 dimensões, criando uma representação híbrida regras+estatística de ~420 features que capturaria tanto padrões lexicais emergentes quanto relações clínicas explícitas.

---

## 9. Limitações honestas do sistema

**Tamanho do dataset (160 frases):** insuficiente para generalização robusta. Classificadores de texto em produção exigem milhares a dezenas de milhares de exemplos. Com 160 frases, a fronteira de decisão varia entre folds (desvio padrão de 3.7-5.1%), indicando sensibilidade à composição amostral.

**Viés do rotulador único:** todas as 160 frases receberam rótulo de uma única pessoa sem validação cruzada por especialista. O Cohen's Kappa interanotador não pode ser calculado. Em NLP clínico, o padrão mínimo exige 2-3 anotadores com Kappa >= 0.80.

**Ausência de validação externa:** o modelo treinou e avaliou frases do mesmo domínio escritas pelo mesmo autor. Frases de pacientes reais conteriam erros ortográficos, gírias regionais e construções frasais que o modelo nunca viu.

**Ausência de calibração de probabilidade:** o notebook exibe probabilidades via `predict_proba`, mas não verifica se essas probabilidades estão calibradas (quando o modelo reporta 0.70 de confiança, o paciente pertence à classe predita em 70% dos casos?). O `CalibratedClassifierCV` do scikit-learn corrigiria essa limitação via calibração isotônica ou Platt scaling.

**Independência da posição e ordem dos termos:** TF-IDF trata cada documento como bag-of-words/bigrams — a ordem além de pares adjacentes se perde. "Dor no peito que irradia para o braço" e "dor no braço que irradia para o peito" recebem representações TF-IDF idênticas apesar de significados clínicos diferentes.

**Confusão entre correlação lexical e causalidade clínica:** frases de alto risco tendem a ser mais longas e descritivas que frases de baixo risco (média de ~15 palavras vs ~11). Termos genéricos como "que" e "com" podem receber peso discriminativo não por relevância clínica, mas por artefato de comprimento. O modelo não distingue entre padrão clínico real e padrão estilístico do autor.

---

## 10. Performance computacional

| Operação | Tempo | Observação |
|----------|-------|------------|
| `fit_transform` (160 frases) | < 10ms | Tokenização + contagem + IDF + normalização L2 |
| Treino LR (160x379) | < 50ms | ~100-200 iterações L-BFGS |
| Treino DT (160x379) | < 10ms | Construção recursiva da árvore |
| Treino NB (160x379) | < 5ms | Contagem de probabilidades condicionais (1 passada) |
| Predição (10 frases) | < 1ms/modelo | Multiplicação vetor esparso x coeficientes (LR/NB) ou travessia de árvore (DT) |
| Memória total | < 1MB | Matriz CSR ~30KB + 3 modelos ~200KB |

---

## 11. Tabela-resumo do pipeline completo

| Etapa | Componente | Entrada | Saída | Hiperparâmetros-chave |
|-------|-----------|---------|-------|-----------------------|
| 1. Carregamento | `csv.DictReader` | `frases_risco.csv` | 160 frases + 160 rótulos | — |
| 2. Vetorização | `TfidfVectorizer` | 160 strings | Matriz CSR 160x379 | `ngram_range=(1,2)`, `min_df=2`, `max_df=0.95` |
| 3. Avaliação CV | `cross_validate` | X (160x379), y (160) | Métricas por fold | `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` |
| 4. Treino LR | `LogisticRegression` | X, y | Vetor de 379 coeficientes | `max_iter=1000`, `C=1.0` (L2), `random_state=42` |
| 5. Treino DT | `DecisionTreeClassifier` | X, y | Árvore de decisão | `max_depth=10`, `random_state=42` |
| 6. Treino NB | `MultinomialNB` | X, y | 379 probabilidades condicionais por classe | `alpha=1.0` (Laplace) |
| 7. Predição | `.predict()` + `.predict_proba()` | 10 frases vetorizadas | Classe + probabilidade | — |

---

## 12. Comparação final dos modelos — Recomendação

| Critério | Logistic Regression | Decision Tree | Naive Bayes |
|----------|---------------------|---------------|-------------|
| F1-macro (CV) | 0.856 | 0.658 | 0.856 |
| Desvio padrão | 0.037 | 0.049 | 0.051 |
| Gap treino/CV | 11.4pp | 31.2pp | 10.4pp |
| Interpretabilidade | Coeficientes por termo | Árvore visualizável | Probabilidades por classe |
| Probabilidades calibradas | Razoável (sigmoide) | Não (proporções em folhas) | Enviesadas (independência) |
| Recomendação clínica | **Recomendado** | Não recomendado | Alternativa viável |

**Recomendação: Logistic Regression.**

A LR e o NB empatam em F1-macro (0.856), mas a LR apresenta menor desvio padrão entre folds (0.037 vs 0.051), indicando maior estabilidade. A LR produz probabilidades melhor calibradas (via sigmoide) que o NB (cujas probabilidades são enviesadas pela premissa de independência). Em cenário de triagem clínica real onde a confiança da predição informa a urgência do encaminhamento, probabilidades calibradas possuem valor operacional direto. O menor gap treino/CV do NB (10.4pp vs 11.4pp) não compensa a instabilidade entre folds. A Decision Tree não atinge performance aceitável para triagem médica (66.2% F1 implica ~34% de erros de classificação).
