# Raciocínio Técnico: MLP para Classificação de Batimentos Cardíacos

Documento que expõe a cadeia completa de raciocínio por trás de cada decisão tomada
no desenvolvimento do notebook `mlp_heartbeat_v2.ipynb` — da inspeção inicial do dataset
à escolha de cada hiperparâmetro, passando pela interpretação dos dados que revelaram
o desbalanceamento e pelas consequências que cada achado impôs sobre a arquitetura.

## Estrutura

| Capítulo | Arquivo | Conteúdo |
|----------|---------|----------|
| I | [01-inspecao-dataset.md](01-inspecao-dataset.md) | Da inspeção ao entendimento: como o dataset revela suas propriedades. 9 operações do script de exploração, cada uma com output, interpretação e consequência para o design. |
| II | [02-decisoes-preprocessamento.md](02-decisoes-preprocessamento.md) | Da inspeção à decisão: binarização de classes (5→2) e compensação de desbalanceamento via class_weight. |
| III | [03-arquitetura-mlp.md](03-arquitetura-mlp.md) | Arquitetura da MLP: cada camada responde a uma restrição. Input 187D, padrão piramidal 128→64→32, BatchNorm, Dropout, sigmoid de saída. |
| IV | [04-treinamento.md](04-treinamento.md) | Treinamento: cada decisão previne uma falha específica. Adam, binary crossentropy, early stopping, validation split, batch size, épocas. |
| V | [05-avaliacao-metricas.md](05-avaliacao-metricas.md) | Avaliação: cada métrica responde a uma pergunta diferente. Acurácia, precision, recall, F1, matriz de confusão, análise por classe original. |
| VI | [06-curvas-treinamento.md](06-curvas-treinamento.md) | Curvas de treinamento: o que cada padrão visual significa. Convergência saudável, overfitting, underfitting. |
| VII | [07-decisoes-descartadas.md](07-decisoes-descartadas.md) | Decisões que não tomei e por quê. CNN 1D, LSTM/GRU, data augmentation, threshold otimizado. |
| VIII | [08-analise-falha-v1.md](08-analise-falha-v1.md) | Análise de falha do modelo v1. Diagnóstico das 4 causas convergentes (class_weight insuficiente, validation split não estratificado, BatchNorm vs class_weight, learning rate), evidências numéricas, correções planejadas para v2. |
| IX | [09-experimentos-v2.md](09-experimentos-v2.md) | Experimentos para o modelo v2. 3 variantes testadas, resultados comparativos, decisão pela variante B (BatchNorm + lr=0.0005). Melhoria de 18x no recall Anormal. A causa raiz era o embaralhamento dos dados. |

## Scripts complementares

O diretório [`exemplos/`](exemplos/) contém scripts executáveis que demonstram
concretamente as afirmações feitas nos capítulos. Cada script produz output
verificável — o leitor executa e observa o efeito descrito no documento.

| Script | Referência | O que demonstra |
|--------|-----------|-----------------|
| [`demo_header_none.py`](exemplos/demo_header_none.py) | Cap. I, Op. 1 | Efeito de omitir `header=None` no MIT-BIH: perda de 1 amostra (benigno). |
| [`demo_header_none_catastrofico.py`](exemplos/demo_header_none_catastrofico.py) | Cap. I, Op. 1 | 3 cenários onde a mesma omissão causa resultado catastrófico. |
| [`demo_data_leakage.py`](exemplos/demo_data_leakage.py) | Cap. I, Op. 2 | 4 cenários de data leakage: modelo com 100% de acurácia completamente inútil. |
| [`demo_experimentos_v2.py`](exemplos/demo_experimentos_v2.py) | Cap. IX | 3 variantes de correção do v1: comprova que embaralhar dados resolve recall de 5% para 94%. |

```bash
# executar qualquer script complementar
python docs/raciocinio/mlp-heartbeat/exemplos/demo_header_none.py
python docs/raciocinio/mlp-heartbeat/exemplos/demo_header_none_catastrofico.py
python docs/raciocinio/mlp-heartbeat/exemplos/demo_data_leakage.py
```

## Artefatos relacionados

| Artefato | Caminho | Relação |
|----------|---------|---------|
| Script de exploração | [`scripts/explorar_heartbeat.py`](../../../scripts/explorar_heartbeat.py) | Gera os achados que os capítulos I e II interpretam |
| Notebook v1 (falhou) | [`notebooks/mlp_heartbeat_v1.ipynb`](../../../notebooks/mlp_heartbeat_v1.ipynb) | Modelo com recall Anormal de 5.17% — análise de falha no capítulo VIII |
| Notebook v2 (atual) | [`notebooks/mlp_heartbeat_v2.ipynb`](../../../notebooks/mlp_heartbeat_v2.ipynb) | Modelo com correções do capítulo VIII |
