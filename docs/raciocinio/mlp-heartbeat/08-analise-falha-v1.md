# VIII. Análise de falha do modelo v1

O notebook `mlp_heartbeat_v1.ipynb` produziu um modelo que atinge 83.6% de
acurácia mas detecta apenas 5.17% dos batimentos anormais. Este capítulo
documenta o diagnóstico da falha, as evidências que o sustentam e as correções
que o modelo v2 deve implementar.

---

## Resultados observados

```
              precision    recall  f1-score   support

      Normal       0.83      1.00      0.91     18118
     Anormal       0.96      0.05      0.10      3774

    accuracy                           0.84     21892
   macro avg       0.90      0.53      0.50     21892

Verdadeiros Negativos (Normal correto):  18,110
Falsos Positivos (Normal -> Anormal):          8
Falsos Negativos (Anormal -> Normal):      3,579
Verdadeiros Positivos (Anormal correto):    195

Taxa de Falsos Negativos: 94.83%
Taxa de Falsos Positivos: 0.04%

Recall por classe original:
  Normal (N)               : 18,110/18,118 = 1.000
  Supraventricular (S)     :   160/  556 = 0.288
  Ventricular (V)          :    35/1,448 = 0.024
  Fusão (F)                :     0/  162 = 0.000
  Desconhecido (Q)         :     0/1,608 = 0.000
```

O early stopping interrompeu o treino na época 6 de 50. A melhor `val_loss`
registrada foi 2.4007 com `val_accuracy` de 9.19%.

---

## Diagnóstico: 4 causas convergentes

### Causa 1 — O class_weight não compensou o gradiente suficientemente

O `class_weight` atribuiu peso 2.9x para a classe Anormal. Esse fator amplifica
o gradiente de cada amostra anormal por 2.9 vezes. Porém, a proporção
Normal/Anormal é 4.8:1. Mesmo com amplificação de 2.9x, o volume absoluto de
amostras normais (72.471) ainda domina o sinal de aprendizado: 72.471 × 0.6 =
43.483 unidades de gradiente Normal contra 15.083 × 2.9 = 43.741 unidades de
gradiente Anormal. O equilíbrio teórico é atingido, mas na prática o BatchNorm
e o Dropout introduzem ruído estocástico que perturba esse equilíbrio frágil.

A rede encontra o caminho de menor resistência: classificar quase tudo como
Normal produz loss moderada (porque o peso Normal é baixo) e acerta 82.8% das
amostras. Classificar corretamente os anormais exige aprender padrões sutis em
morfologia de ECG — tarefa mais difícil que o atalho de ignorar a classe
minoritária.

### Causa 2 — O validation split não é estratificado

O Keras implementa `validation_split=0.15` separando as **últimas** 15% das
amostras do array de treino. Se o dataset não foi embaralhado antes do `fit()`,
as últimas 15% podem conter distribuição de classes diferente das primeiras 85%.
No MIT-BIH, a ordenação interna do CSV não é aleatória — batimentos do mesmo
paciente tendem a ser consecutivos. O `val_loss` monitorado pelo early stopping
reflete a performance em uma fatia não-representativa, causando interrupção
prematura na época 6.

### Causa 3 — O BatchNorm interfere com o class_weight

O BatchNormalization normaliza as ativações pela estatística do mini-batch.
Com batch size de 256 e 82.8% de amostras normais, cada batch contém ~212
normais e ~44 anormais. A média e variância do batch são dominadas pelas
ativações de amostras normais. O BatchNorm "puxa" as ativações dos anormais na
direção da distribuição normal, contrabalançando o efeito do class_weight que
tenta amplificá-las.

### Causa 4 — A learning rate pode ser alta demais para a classe minoritária

O Adam com learning rate 0.001 atualiza os pesos com passos que refletem
predominantemente o gradiente da classe majoritária (mesmo com class_weight).
Para a classe minoritária, os passos podem ser grandes demais, causando
oscilações que impedem convergência nos padrões anormais. Uma learning rate
menor (0.0001 ou 0.0005) com mais épocas permitiria ajuste mais fino.

---

## Evidências numéricas da falha

| Indicador | Valor | Limiar aceitável | Diagnóstico |
|-----------|-------|------------------|-------------|
| Acurácia | 0.836 | > 0.828 (baseline) | Marginalmente acima — modelo quase trivial |
| Recall Anormal | 0.052 | > 0.70 | Catastroficamente baixo |
| F1-macro | 0.504 | > 0.70 | Inaceitável |
| Taxa FN | 94.83% | < 10% | 19x acima do aceitável |
| Épocas treinadas | 6/50 | > 15 | Early stopping prematuro |
| val_accuracy | 9.19% | > 80% | Validação degenerada |
| Recall Fusão (F) | 0.000 | > 0 | Classe completamente invisível |
| Recall Desconhecido (Q) | 0.000 | > 0 | Classe completamente invisível |

O modelo v1 é **pior que um classificador aleatório** para a classe Anormal:
um classificador aleatório com probabilidade 50/50 detectaria ~50% dos anormais.
O modelo v1 detecta 5.17%.

---

## Correções planejadas para o modelo v2

### C1 — Embaralhar os dados antes do treino

```python
indices = np.random.permutation(len(X_treino))
X_treino = X_treino[indices]
y_treino = y_treino[indices]
```

O embaralhamento garante que o `validation_split` do Keras extrai uma fatia
representativa (com proporção ~82.8%/17.2%) em vez de uma fatia enviesada pela
ordenação original do CSV.

### C2 — Reduzir a learning rate

```python
optimizer=keras.optimizers.Adam(learning_rate=0.0005)
```

A learning rate de 0.0005 (metade do padrão) permite passos menores que
convergem de forma mais estável para padrões da classe minoritária. O trade-off:
o treino leva mais épocas para convergir, mas o resultado final é mais robusto.

### C3 — Aumentar o patience do early stopping

```python
early_stop = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True,
)
```

O patience de 10 (em vez de 5) concede ao modelo mais tempo para escapar de
platôs de validação. O modelo v1 parou na época 6 — o v2 treina até pelo menos
a época 16 antes de considerar interrupção.

### C4 — Considerar remoção do BatchNorm

Se as correções C1-C3 não resolverem o conflito entre BatchNorm e class_weight,
o v2 remove o BatchNorm e compensa com:
- Inicialização He (`kernel_initializer="he_normal"`) para estabilizar ativações
  ReLU sem normalização de batch
- Learning rate mais baixa para compensar a perda de estabilidade

### C5 — Avaliar threshold inferior a 0.5

Após treinar o v2, testar thresholds de 0.3 e 0.4 para aumentar recall de
Anormal ao custo controlado de precision. Em triagem cardiológica, recall alto
com precision moderada é preferível ao oposto.

---

## Lição documentada

O modelo v1 demonstra que **class_weight sozinho não resolve desbalanceamento
severo**. O fator 2.9x equilibra o gradiente na teoria, mas o BatchNorm, a
ordenação dos dados e o early stopping agressivo conspiram para anular esse
equilíbrio na prática. A engenharia de machine learning exige que cada componente
do pipeline seja avaliado não isoladamente, mas em interação com todos os demais.

A preservação do modelo v1 como `mlp_heartbeat_v1.ipynb` cumpre função
pedagógica: demonstra que um pipeline aparentemente correto (pré-processamento
adequado, arquitetura razoável, regularização presente, class_weight ativado)
pode produzir resultado clinicamente inútil. O diagnóstico da falha é tão
valioso quanto o modelo funcional que o sucede.

---

## Referências

| Artefato | Caminho |
|----------|---------|
| Notebook v1 (com outputs) | [`notebooks/mlp_heartbeat_v1.ipynb`](../../../notebooks/mlp_heartbeat_v1.ipynb) |
| Notebook v2 (funcional) | [`notebooks/mlp_heartbeat_v2.ipynb`](../../../notebooks/mlp_heartbeat_v2.ipynb) |
