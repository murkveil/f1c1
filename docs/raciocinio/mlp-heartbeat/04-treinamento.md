# IV. Treinamento: cada decisão previne uma falha específica

## Optimizer: Adam com learning rate 0.001

O Adam combina momentum (média exponencial dos gradientes) com RMSprop (média
exponencial dos quadrados dos gradientes). Para redes feedforward com
BatchNormalization, o Adam converge mais rápido que SGD puro porque adapta a
learning rate por parâmetro — neurônios com gradientes grandes recebem passos
menores, neurônios com gradientes pequenos recebem passos maiores. O valor 0.001
é o padrão do Keras e funciona bem para a maioria das arquiteturas MLP com BatchNorm.

---

## Loss: binary crossentropy

A binary crossentropy `L = -[y·log(p) + (1-y)·log(1-p)]` penaliza predições
confiantes e erradas exponencialmente mais que predições incertas e erradas. Quando
o modelo prediz 0.99 para uma amostra que é 0 (Normal), a loss é `-log(0.01) = 4.6`.
Quando prediz 0.6, a loss é `-log(0.4) = 0.92`. Essa propriedade força o modelo
a ser cauteloso: atribuir alta confiança apenas quando a evidência justifica.

Com class_weight, a loss de cada amostra é multiplicada pelo peso da sua classe
antes da soma. Uma amostra Anormal com peso 2.9 contribui 2.9x mais para a loss
total que uma Normal com peso 0.6. O gradiente herda essa ponderação, direcionando
os pesos na direção que reduz erros na classe minoritária.

---

## Early stopping: patience=5, restore_best_weights

O early stopping monitora a `val_loss` (loss no conjunto de validação separado
automaticamente) e interrompe o treinamento se a val_loss não melhorar por 5 épocas
consecutivas. Quando a loss de treino continua caindo mas a val_loss estagna ou
sobe, a rede está memorizando o treino sem generalizar — overfitting. O
`restore_best_weights=True` garante que os pesos finais são os da época com menor
val_loss, não os da última época executada.

O valor patience=5 concede ao optimizer 5 oportunidades de escapar de platôs
temporários. Patience menor (2-3) interromperia prematuramente em platôs legítimos
que o Adam resolveria com mais iterações. Patience maior (10-15) arriscaria
overfitting prolongado antes da interrupção.

---

## Validation split: 15%

O `validation_split=0.15` separa as últimas 15% das amostras de treino (~13.000)
como conjunto de validação interna. O Keras utiliza essas amostras para calcular
`val_loss` e `val_accuracy` ao final de cada época, sem incluí-las no cálculo do
gradiente. Essa separação permite monitorar a generalização em tempo real.

O valor 15% equilibra dois objetivos: amostras suficientes para validação
estatisticamente estável (~13.000) e amostras suficientes para treino (~74.000).
Com 87K amostras totais, 15% não empobrece o treino significativamente. A
alternativa de usar 20-30% reduziria o treino sem ganho de informação na
validação — 13.000 amostras já estimam métricas com margem de erro inferior a 1%.

---

## Batch size: 256

O batch size de 256 determina quantas amostras o Keras processa antes de atualizar
os pesos. Com 74.000 amostras de treino (após validation split), cada época contém
~289 atualizações de gradiente (74.000 / 256). O BatchNorm requer batches
suficientemente grandes para que a estatística do batch (média, variância)
aproxime a estatística da população — batches de 256 satisfazem essa condição.

A alternativa de batch size 32 (padrão do Keras) produziria ~2.312 atualizações
por época com gradientes mais ruidosos — potencialmente melhor para escapar de
mínimos locais, mas mais lento computacionalmente. A alternativa de batch size
1024 aceleraria o treino mas reduziria o ruído estocástico que ajuda a
generalização. O valor 256 equilibra velocidade e qualidade do gradiente.

---

## Épocas: 50 (com early stopping)

O número máximo de épocas (50) funciona como teto de segurança — o early stopping
interrompe antes se detectar overfitting. Na prática, redes MLP com BatchNorm e
Dropout convergem em 15-30 épocas neste dataset. As épocas restantes servem como
margem para arquiteturas que convergem mais lentamente.
