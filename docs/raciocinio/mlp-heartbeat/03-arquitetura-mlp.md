# III. Arquitetura da MLP: cada camada responde a uma restrição

## Input: 187 dimensões

Cada batimento é um vetor de 187 valores contínuos entre 0 e 1. A MLP recebe este
vetor como entrada sem reshape — diferente de uma CNN, que exigiria o vetor
reformatado como tensor 1D com dimensão de canal. A MLP trata cada amostra temporal
como uma feature independente. Esta simplificação perde a informação de adjacência
temporal (a amostra 50 é vizinha da 51, não da 100), mas o enunciado pede
explicitamente uma MLP, não uma CNN.

---

## Camada 1: Dense(128, ReLU) + BatchNorm + Dropout(0.3)

**Por que 128 neurônios:** a primeira camada deve ter dimensionalidade superior à
do input (187) ou comparável. Com 128 neurônios, a rede comprime levemente a
representação, forçando-a a aprender combinações de features em vez de memorizar
cada uma isoladamente. A alternativa de usar 256 ou 512 neurônios aumentaria a
capacidade de memorização sem ganho proporcional de generalização com 87K amostras.

**Por que ReLU:** a Rectified Linear Unit `f(x) = max(0, x)` possui três
propriedades que a tornam a escolha padrão para camadas intermediárias: (a) não
sofre de vanishing gradient para valores positivos, permitindo que gradientes
fluam sem atenuação para camadas anteriores; (b) produz ativações esparsas (cada
neurônio ou dispara ou é zero), o que funciona como regularização implícita;
(c) é computacionalmente trivial comparada a sigmoid ou tanh.

**Por que BatchNormalization:** o BatchNorm normaliza as ativações de cada camada
pela média e variância do mini-batch. Em uma rede com 3 camadas densas, as
distribuições de ativação intermediárias mudam a cada atualização de pesos
(internal covariate shift). O BatchNorm estabiliza essas distribuições, permitindo
learning rates mais altas sem divergência e acelerando a convergência em 2-5x
empiricamente.

**Por que Dropout(0.3):** o Dropout desativa 30% dos neurônios aleatoriamente
durante o treino. Com 128 neurônios na primeira camada, ~38 neurônios são zerados
a cada forward pass. A rede não pode depender de nenhum neurônio individual para
classificar corretamente — deve distribuir a representação entre múltiplos
neurônios. O valor 0.3 é conservador: alto o suficiente para prevenir memorização,
baixo o suficiente para não destruir a capacidade de aprendizado. Valores acima de
0.5 em camadas intermediárias degradariam o fluxo de informação em redes com apenas
3 camadas.

---

## Camada 2: Dense(64, ReLU) + BatchNorm + Dropout(0.3)

A segunda camada comprime de 128 para 64 neurônios. Essa redução progressiva força
a rede a extrair representações cada vez mais abstratas e compactas do sinal de
ECG. O padrão piramidal (128 → 64 → 32) reflete a heurística consolidada em redes
feedforward: camadas progressivamente menores atuam como gargalos informacionais
que filtram ruído e retêm apenas as features mais discriminativas.

---

## Camada 3: Dense(32, ReLU) + BatchNorm + Dropout(0.2)

A terceira camada reduz para 32 neurônios com Dropout menor (0.2 em vez de 0.3).
A justificativa para reduzir o Dropout na última camada hidden: com apenas 32
neurônios, desativar 30% (10 neurônios) reduziria a capacidade efetiva para 22
neurônios — insuficiente para representar 187 dimensões comprimidas. O Dropout
de 0.2 preserva ~26 neurônios ativos, mantendo regularização sem estrangular a
representação.

---

## Output: Dense(1, sigmoid)

A camada de saída possui 1 neurônio com ativação sigmoid, que mapeia a saída
para o intervalo (0, 1) interpretável como probabilidade de pertencer à classe
"Anormal". O threshold padrão de 0.5 divide o espaço: acima de 0.5 classifica
como Anormal, abaixo como Normal.

A alternativa de usar 2 neurônios com softmax produziria resultado matematicamente
equivalente para classificação binária — softmax com 2 classes degenera para
sigmoid — mas adicionaria um parâmetro desnecessário e complicaria a interpretação
de probabilidades (duas probabilidades que somam 1 vs. uma probabilidade direta).
