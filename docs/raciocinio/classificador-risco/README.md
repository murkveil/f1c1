# Raciocínio Técnico: Classificador de Risco Cardiovascular

Documento que expõe a cadeia de raciocínio por trás de cada decisão tomada no
desenvolvimento do notebook `classificador_risco.ipynb` — da construção do dataset
rotulado à escolha de cada hiperparâmetro do TF-IDF e dos 3 modelos de classificação.

## Estrutura

| Capítulo | Arquivo | Conteúdo |
|----------|---------|----------|
| I | [01-construcao-dataset.md](01-construcao-dataset.md) | Construção e rotulação do dataset `frases_risco.csv`: critérios clínicos, frases ambíguas intencionais, balanceamento 51/49. |
| II | [02-vetorizacao-tfidf.md](02-vetorizacao-tfidf.md) | Vetorização TF-IDF: ngram_range, min_df, max_df, fórmula IDF com suavização, normalização L2, formato CSR. |
| III | [03-modelos-avaliacao.md](03-modelos-avaliacao.md) | Escolha dos 3 modelos, Stratified K-Fold, análise de coeficientes, custo assimétrico de erros, correção da inversão de indexação. |
| IV | [04-correcao-matplotlib.md](04-correcao-matplotlib.md) | Correção do warning `FigureCanvasAgg is non-interactive`: causa, diagnóstico e solução. |

## Artefatos relacionados

| Artefato | Caminho | Relação |
|----------|---------|---------|
| Notebook | [`notebooks/classificador_risco.ipynb`](../../../notebooks/classificador_risco.ipynb) | Implementa as decisões documentadas |
| Dataset | [`data/textuais/frases_risco.csv`](../../../data/textuais/frases_risco.csv) | 160 frases rotuladas |
| Documentação técnica | [`docs/classificador-risco-cardiovascular.md`](../../classificador-risco-cardiovascular.md) | Análise completa de TF-IDF, modelos e limitações |
