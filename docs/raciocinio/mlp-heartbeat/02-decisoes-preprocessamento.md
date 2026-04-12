# II. Da inspeção à decisão: como cada achado determina uma escolha

## Binarização de classes: de 5 para 2

O enunciado exige classificação binária: "identificar se o sinal indica um ritmo
cardíaco normal ou alguma anomalia". As 5 classes do MIT-BIH (N, S, V, F, Q)
constituem subtipos de anomalia que a tarefa não pede para distinguir.

A binarização agrupa classes 1-4 em "Anormal":

```python
y_treino = (y_treino_original > 0).astype(int)
```

A operação `> 0` retorna True para qualquer classe diferente de Normal. O cast
para int produz 0 (Normal) e 1 (Anormal). O resultado: 72.471 normais (82.8%)
e 15.083 anormais (17.2%).

A alternativa de manter 5 classes exigiria uma camada de saída com 5 neurônios
e softmax, complicaria a interpretação de métricas (precision e recall por classe
entre 5 categorias com desbalanceamento severo em cada uma) e não atenderia ao
enunciado. A binarização simplifica o problema para sua forma essencial: o sinal
deste paciente requer atenção ou não?

---

## Class weight: compensação aritmética do desbalanceamento

O scikit-learn oferece `compute_class_weight("balanced")`, que calcula o peso de
cada classe como `n_amostras / (n_classes * n_amostras_classe)`:

```python
pesos_classes = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_treino)
class_weight = {0: pesos_classes[0], 1: pesos_classes[1]}
```

Para o MIT-BIH binarizado:
- Classe 0 (Normal, 72.471 amostras): peso = 87.554 / (2 * 72.471) = 0.6038
- Classe 1 (Anormal, 15.083 amostras): peso = 87.554 / (2 * 15.083) = 2.9023

O peso 2.9023 para a classe Anormal significa que cada erro em uma amostra anormal
custa 2.9x mais que um erro em uma amostra normal. O gradiente proveniente de
amostras anormais é amplificado por esse fator, compensando a inferioridade numérica
da classe. O efeito líquido: a rede trata o dataset como se ambas as classes
tivessem representação igual.

A alternativa de não usar class_weight produziria um modelo com acurácia ~83% e
recall de Anormal próximo de zero — numericamente impressionante, clinicamente
inútil. A alternativa de undersampling (reduzir Normal para 15.083 amostras)
descartaria 57.388 amostras de treino — 79% dos dados —, empobrecendo a
representação da classe Normal sem garantia de melhoria na Anormal. A alternativa
de oversampling (SMOTE ou duplicação) inflaria artificialmente a classe minoritária,
introduzindo correlações espúrias entre amostras sintéticas. O class_weight resolve
o problema no nível da função de custo, sem alterar os dados.
