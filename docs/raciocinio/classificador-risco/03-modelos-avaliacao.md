# III. Modelos, avaliação e análise de coeficientes

## Escolha dos 3 modelos

| Modelo | Razão da escolha |
|--------|-----------------|
| Logistic Regression | Baseline linear robusto para classificação binária de texto. Modela diretamente P(y=classe\|x) via sigmoide. Regularização L2 por padrão previne overfitting com p/n > 1. |
| Decision Tree | Modelo interpretável que permite visualizar quais termos o classificador considera decisivos em cada split. |
| Naive Bayes (Multinomial) | Modelo probabilístico clássico para texto com TF-IDF. A premissa de independência condicional entre features é violada (bigramas dependem de unigramas), mas a decisão de classificação permanece correta na prática. |

## Stratified 5-Fold Cross-Validation

Com 160 frases, um train/test split simples (80/20) produziria um conjunto de
teste com 32 frases — intervalo de confiança de 95% para acurácia: +/- 12.4%.
Essa incerteza torna comparação entre modelos estatisticamente inútil.

O Stratified 5-Fold resolve: cada fold testa em ~32 frases, mas as 5 estimativas
independentes produzem média com desvio padrão mensurável. A estratificação
garante que cada fold mantém a proporção 51/49 do dataset completo.

## Resultados

| Modelo | Acurácia | F1-macro | Desvio padrão |
|--------|----------|----------|---------------|
| Logistic Regression | 0.856 | 0.856 | 0.037 |
| Decision Tree | 0.662 | 0.658 | 0.049 |
| Naive Bayes | 0.856 | 0.856 | 0.051 |

A Decision Tree atinge F1 de 0.658 vs 0.856 dos outros modelos. A causa: a
árvore cria fronteiras de decisão axiais em espaço de 379 dimensões. Para aprender
a combinação "dor + peito + irradia + braço", a árvore precisa de múltiplos splits
sequenciais, cada split reduzindo as amostras nos nós filhos. Com 160 amostras, os
nós profundos contêm poucas observações e as estimativas de classe tornam-se
instáveis (alta variância).

## Análise de coeficientes da Logistic Regression

O scikit-learn ordena as classes lexicograficamente: `classes_ = ["alto risco",
"baixo risco"]`, logo `alto risco = índice 0` e `baixo risco = índice 1`. A
atribuição interna do `LogisticRegression` faz `coef_[0]` mapear para a classe
de índice 1 — por convenção da implementação. Consequência:

- Coeficientes **positivos** apontam para a classe de índice 1 ("baixo risco")
- Coeficientes **negativos** apontam para a classe de índice 0 ("alto risco")

**Termos indicativos de alto risco (coeficientes negativos):**
- "no peito" (-0.937), "sinto dor" (-0.892), "esforço" (-0.644), "forte" (-0.550),
  "falta de" (-0.539), "de ar" (-0.539)

**Termos indicativos de baixo risco (coeficientes positivos):**
- "leve" (+1.190), "uma leve" (+0.785), "depois" (+0.746), "nas costas" (+0.527)

### Histórico: inversão de rótulos corrigida

A primeira versão do notebook invertia os rótulos — rotulava a lista ordenada
por coeficiente decrescente (positivos) como "Top-15 termos indicativos de ALTO
RISCO", o que contradizia a convenção da scikit-learn. O bug foi corrigido
aplicando `np.argsort(coeficientes)[:15]` (mais negativos) à lista de alto
risco e `np.argsort(coeficientes)[::-1][:15]` (mais positivos) à lista de
baixo risco, invertendo-se a convenção original. A célula Markdown que
descreve os coeficientes foi reescrita para declarar explicitamente a
convenção de indexação.

## Custo assimétrico de erros

Em triagem cardiovascular, um falso negativo (classificar "alto risco" como
"baixo risco") significa que um paciente com possível emergência cardiovascular
não receberia avaliação urgente — risco de morte. Um falso positivo (classificar
"baixo risco" como "alto risco") significa encaminhamento desnecessário — custo
operacional sem risco clínico. O recall da classe "alto risco" mede a proporção
de pacientes verdadeiramente em risco que o modelo identifica corretamente.
