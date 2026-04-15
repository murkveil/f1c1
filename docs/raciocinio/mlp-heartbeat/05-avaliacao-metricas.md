# V. Avaliação: cada métrica responde a uma pergunta diferente

## Acurácia: responde "quanto do total o modelo acerta?"

A acurácia conta a fração de predições corretas sobre o total. Com desbalanceamento
de 82.8%/17.2%, a acurácia isolada não distingue entre "modelo que aprendeu" e
"modelo que replica a base rate". Uma acurácia de 90% pode significar que o modelo
é excelente ou que classifica tudo como Normal e acerta os 82.8% normais mais
alguns anormais por sorte. A acurácia informa, mas não decide.

---

## Precision da classe Anormal: responde "dos que o modelo classificou como Anormal, quantos realmente são?"

Precision alta significa poucos falsos positivos — quando o modelo diz "Anormal",
o batimento provavelmente é anormal. Precision baixa significa que o modelo dispara
alarmes demais. Em triagem, precision baixa causa fadiga de alarme: profissionais
de saúde ignoram alertas após excesso de falsos positivos. Portanto, precision não
pode ser arbitrariamente baixa.

---

## Recall da classe Anormal: responde "dos batimentos realmente anormais, quantos o modelo detecta?"

Recall alta significa poucos falsos negativos — a maioria dos batimentos anormais
é identificada. Recall baixa significa que arritmias reais passam despercebidas.
Em triagem cardiológica, recall é a métrica com maior custo de falha: um batimento
ventricular não detectado pode preceder morte súbita. Portanto, recall da classe
Anormal é a métrica mais crítica do sistema.

---

## F1-score: responde "qual o equilíbrio entre precision e recall?"

O F1 é a média harmônica de precision e recall: `F1 = 2 * (P * R) / (P + R)`.
A média harmônica penaliza assimetria: se precision é 0.95 e recall é 0.30, o
F1 cai para 0.46 — expondo que o modelo sacrifica detecção por precisão. O F1
resume o trade-off em um número, mas não substitui a análise individual de
precision e recall.

---

## Matriz de confusão: responde "onde exatamente o modelo erra?"

A matriz 2x2 decompõe os resultados em quatro quadrantes:

```
                    Predito Normal    Predito Anormal
Real Normal         TN                FP
Real Anormal        FN                TP
```

Cada quadrante possui significado clínico:
- **TN (Verdadeiro Negativo):** batimento normal classificado como normal — correto.
- **FP (Falso Positivo):** batimento normal classificado como anormal — alarme falso,
  custo operacional.
- **FN (Falso Negativo):** batimento anormal classificado como normal — arritmia
  ignorada, risco clínico.
- **TP (Verdadeiro Positivo):** batimento anormal classificado como anormal — detecção
  correta.

A taxa de falsos negativos `FN / (FN + TP)` é a métrica que determina se o sistema
é seguro para uso clínico. Uma taxa de 5% significa que 5 em cada 100 arritmias
passam despercebidas — inaceitável para monitoramento contínuo, possivelmente
aceitável para triagem de primeiro nível.

---

## Análise por classe original: responde "o modelo trata todas as arritmias igualmente?"

A binarização agrupa 4 tipos de arritmia em uma classe. Mas nem todas as arritmias
possuem a mesma morfologia no ECG: batimentos ventriculares (classe 2) possuem
complexo QRS largo e deformado que a MLP distingue facilmente de normal; batimentos
supraventriculares (classe 1) possuem morfologia semelhante ao normal com diferenças
sutis na onda P que a MLP pode não capturar. A análise de recall por classe original
revela se o modelo detecta igualmente todas as arritmias ou favorece as
morfologicamente mais distintas.
