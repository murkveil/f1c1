# notebooks

Notebooks Jupyter do projeto CardioIA.

## Classificador de Risco (Fase 2 - Parte 2)

| Arquivo | Descrição |
|---------|-----------|
| [`classificador_risco.ipynb`](classificador_risco.ipynb) | TF-IDF + Logistic Regression, Decision Tree e Naive Bayes para classificação de frases médicas (alto/baixo risco). F1-macro: 0.856. |

Documentação técnica: [`docs/classificador-risco-cardiovascular.md`](../docs/classificador-risco-cardiovascular.md)

## MLP Heartbeat (Ir Além 2a)

| Arquivo | Versão | Recall Anormal | Descrição |
|---------|--------|---------------|-----------|
| [`mlp_heartbeat_v2.ipynb`](mlp_heartbeat_v2.ipynb) | **v2 (atual)** | 93.3% | Modelo funcional com dados embaralhados, lr=0.0005, patience=10. |
| [`mlp_heartbeat_v1.ipynb`](mlp_heartbeat_v1.ipynb) | v1 (falho) | 5.17% | Preservado como artefato pedagógico — documenta a falha e sua causa. |

Documentação técnica: [`docs/raciocinio/mlp-heartbeat/`](../docs/raciocinio/mlp-heartbeat/)

### Dataset

O dataset MIT-BIH Heartbeat não está versionado no repositório (~570MB, idêntico ao Kaggle):

```bash
kaggle datasets download -d shayanfazeli/heartbeat -p data/numericos/heartbeat --unzip
```

### Imagens geradas

| Arquivo | Gerado por |
|---------|-----------|
| `batimentos_exemplo.png` | `mlp_heartbeat_v2.ipynb` |
| `curvas_treinamento.png` | `mlp_heartbeat_v2.ipynb` |
| `distribuicao_classes.png` | `mlp_heartbeat_v2.ipynb` |
| `matriz_confusao_mlp.png` | `mlp_heartbeat_v2.ipynb` |
| `matrizes_confusao.png` | `classificador_risco.ipynb` |
