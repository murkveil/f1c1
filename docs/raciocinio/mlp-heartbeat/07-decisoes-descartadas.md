# VII. Decisões que não tomei e por quê

## Por que não CNN 1D

O enunciado pede explicitamente uma MLP (Perceptron Multicamadas). Uma CNN 1D
capturaria padrões locais no sinal ECG (formato do complexo QRS, duração de
segmentos ST) com filtros convolucionais que preservam adjacência temporal — algo
que a MLP, ao tratar cada amostra como feature independente, ignora. A CNN 1D
provavelmente superaria a MLP neste dataset, mas atenderia a uma especificação
diferente da solicitada.

---

## Por que não LSTM/GRU

Redes recorrentes modelam dependências sequenciais — a amostra 100 depende das
amostras 1-99. Para sinais ECG, essa temporalidade é relevante (a onda T segue o
complexo QRS, a onda P precede o QRS). Porém, LSTMs exigiriam reshape do input
para formato (batch, timesteps, features), aumentariam o tempo de treino e
excederiam o escopo de "MLP" do enunciado.

---

## Por que não data augmentation

O dataset possui 87.554 amostras de treino — volume suficiente para uma MLP de 3
camadas. Data augmentation (adição de ruído, time warping, amplitude scaling)
beneficiaria mais um dataset com centenas de amostras (como o Ir Além 2b com 50
imagens). Aplicar augmentation em 87K amostras atrasaria o treino sem ganho
significativo de generalização.

---

## Por que não threshold otimizado

O threshold padrão de 0.5 divide o espaço de probabilidades ao meio. Em
classificação com custo assimétrico, reduzir o threshold para 0.3 ou 0.4 aumentaria
o recall de Anormal (mais batimentos classificados como anormais) ao custo de
precision (mais falsos positivos). O class_weight já compensa o desbalanceamento
na fase de treino; otimizar o threshold na fase de predição seria uma segunda
camada de ajuste que introduziria um hiperparâmetro adicional a calibrar. O
notebook mantém 0.5 por simplicidade e transparência, documentando que a otimização
de threshold seria o próximo passo em um sistema de produção.
