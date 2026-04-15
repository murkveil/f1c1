# VI. Curvas de treinamento: o que cada padrão visual significa

## Convergência saudável

As curvas de loss (treino e validação) devem:
- Ambas decrescer nas primeiras épocas (a rede aprende padrões reais)
- A curva de validação estabilizar após 10-20 épocas (a generalização atingiu seu
  limite)
- O gap entre treino e validação permanecer pequeno e estável (sem overfitting
  crescente)

---

## Overfitting

Se a loss de treino continua caindo enquanto a loss de validação sobe, a rede
memoriza o treino. O early stopping interrompe nesse ponto, mas as curvas revelam
a severidade: um gap grande (treino: 0.05, validação: 0.30) indica que a rede
possui capacidade excessiva para o volume de dados. A solução: aumentar Dropout,
reduzir neurônios ou adicionar regularização L2.

---

## Underfitting

Se ambas as curvas estabilizam em valores altos de loss (treino: 0.40,
validação: 0.45), a rede não possui capacidade suficiente para aprender os padrões.
A solução: aumentar neurônios, adicionar camadas ou reduzir Dropout/regularização.
