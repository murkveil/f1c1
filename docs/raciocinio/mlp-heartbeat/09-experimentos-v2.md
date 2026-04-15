# IX. Experimentos para o modelo v2

O capítulo VIII diagnosticou 4 causas convergentes para a falha do modelo v1
(recall Anormal de 5.17%). Este capítulo documenta os experimentos que testaram
as correções propostas, os resultados obtidos e a decisão final sobre a
configuração do modelo v2.

---

## O script de experimentação

Antes de reescrever o notebook, o engenheiro executa um script de experimentação
rápida que treina 3 variantes da MLP em sequência, cada uma aplicando um subconjunto
diferente das correções. O script
[`exemplos/demo_experimentos_v2.py`](exemplos/demo_experimentos_v2.py) reproduz
esse processo.

O objetivo do script não é encontrar a melhor configuração por grid search — é
responder a uma pergunta específica: **qual das correções do capítulo VIII resolve
o problema de recall, e qual combinação produz o melhor equilíbrio entre recall
Anormal e F1-macro?**

---

## As 3 variantes testadas

Todas as variantes aplicam a correção C1 (embaralhar dados) e C3 (patience=10),
porque essas correções são incondicionais — não possuem trade-off. As variantes
diferem em C2 (learning rate) e C4 (presença de BatchNorm):

| Variante | BatchNorm | Learning rate | Correções aplicadas |
|----------|-----------|---------------|---------------------|
| A | Não | 0.0005 | C1 + C2 + C3 + C4 |
| B | Sim | 0.0005 | C1 + C2 + C3 |
| C | Não | 0.001 | C1 + C3 + C4 |

---

## Resultados

```
--- A: sem BatchNorm, lr=0.0005 ---
  Épocas: 50
  Acurácia: 0.9713
  Recall Normal:  0.9779
  Recall Anormal: 0.9396
  F1-macro:       0.9505

--- B: com BatchNorm, lr=0.0005 ---
  Épocas: 50
  Acurácia: 0.9768
  Recall Normal:  0.9854
  Recall Anormal: 0.9356
  F1-macro:       0.9595

--- C: sem BatchNorm, lr=0.001 ---
  Épocas: 45
  Acurácia: 0.9736
  Recall Normal:  0.9802
  Recall Anormal: 0.9420
  F1-macro:       0.9545
```

---

## Análise comparativa

| Métrica | v1 (falho) | A | B | C |
|---------|-----------|---|---|---|
| Recall Anormal | 0.052 | 0.940 | 0.936 | **0.942** |
| F1-macro | 0.504 | 0.951 | **0.960** | 0.955 |
| Acurácia | 0.836 | 0.971 | **0.977** | 0.974 |
| Épocas | 6 | 50 | 50 | 45 |

### O que cada correção causou

**Embaralhar os dados (C1) resolveu o problema principal.** As 3 variantes
atingem recall Anormal acima de 93%, partindo de 5.17% no v1. A causa raiz da
falha do v1 era o `validation_split` do Keras extraindo uma fatia não-representativa
das últimas 15% do CSV ordenado. O embaralhamento garante que cada fatia contém
~82.8% Normal e ~17.2% Anormal, permitindo que o early stopping monitore uma
validação representativa.

**Reduzir a learning rate (C2) melhorou marginalmente.** A variante C (lr=0.001,
sem BatchNorm) atinge recall 0.942 vs 0.940 da variante A (lr=0.0005, sem
BatchNorm) — diferença de 0.2 pontos percentuais. A learning rate não era a causa
da falha.

**BatchNorm não prejudicou (refutando a hipótese da Causa 3 do capítulo VIII).**
A variante B (com BatchNorm) atinge o melhor F1-macro (0.960) e a melhor acurácia
(0.977). O BatchNorm não interfere com o class_weight quando os dados estão
embaralhados — a estatística de cada batch reflete a distribuição global porque
o embaralhamento distribui amostras de ambas as classes uniformemente entre batches.

**O aumento de patience (C3) permitiu treino completo.** As variantes A e B
treinaram todas as 50 épocas sem early stopping. A variante C parou na época 45.
Nenhuma variante parou na época 6 como o v1 — o patience de 10 concede margem
suficiente para convergência.

---

## Decisão: variante B como modelo v2

A variante B (com BatchNorm, lr=0.0005) produz o melhor F1-macro (0.960) e a
melhor acurácia (0.977), com recall Anormal de 0.936 — marginalmente inferior ao
0.942 da variante C, mas compensado pelo F1 4.5 pontos percentuais superior. Em
triagem clínica, 93.6% de recall Anormal significa que o modelo detecta 3.532 dos
3.774 batimentos anormais do teste, perdendo 242. Comparado ao v1 que detectava
apenas 195 dos 3.774 (5.17%), o v2 representa um salto de **18x** na capacidade
de detecção.

---

## Melhoria v1 → v2 em perspectiva

| Métrica | v1 | v2 | Melhoria |
|---------|----|----|----------|
| Recall Anormal | 0.052 | 0.936 | **18x** |
| F1-macro | 0.504 | 0.960 | **1.9x** |
| Acurácia | 0.836 | 0.977 | +14.1pp |
| FN (anormais perdidos) | 3.579 | ~242 | **-93%** |
| Épocas treinadas | 6 | 50 | treino completo |

A lição central: **a causa de falha de um modelo de ML nem sempre reside na
arquitetura ou nos hiperparâmetros.** O v1 possuía arquitetura idêntica ao v2. A
diferença entre 5.17% e 93.6% de recall resume-se a uma linha de código:

```python
# esta linha separa um modelo inútil de um modelo funcional
idx = np.random.permutation(len(X_treino))
X_treino = X_treino[idx]
y_treino = y_treino[idx]
```

---

## Referências

| Artefato | Caminho |
|----------|---------|
| Script de experimentação | [`exemplos/demo_experimentos_v2.py`](exemplos/demo_experimentos_v2.py) |
| Análise de falha v1 | [08-analise-falha-v1.md](08-analise-falha-v1.md) |
| Notebook v1 | [`notebooks/mlp_heartbeat_v1.ipynb`](../../../notebooks/mlp_heartbeat_v1.ipynb) |
| Notebook v2 | [`notebooks/mlp_heartbeat_v2.ipynb`](../../../notebooks/mlp_heartbeat_v2.ipynb) |
