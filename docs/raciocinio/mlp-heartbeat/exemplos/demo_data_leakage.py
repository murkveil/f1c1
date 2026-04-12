"""Demonstração: data leakage por inclusão da coluna de classe como feature.

Este script complementa a Operação 2 do capítulo I do documento
docs/raciocinio/mlp-heartbeat/01-inspecao-dataset.md. O documento afirma que incluir
a coluna de classe como feature causa "acurácia perfeita no treino e zero no teste
(data leakage)". Este script prova a afirmação com 4 cenários concretos e reproduzíveis.

Conceitos que o script demonstra na prática:

- input_dim: o número de features que a rede neural recebe como entrada. Cada
  batimento do MIT-BIH possui 187 amostras do sinal ECG. O input_dim correto é
  187. Se o engenheiro usa 188 (incluindo a coluna de classe), o input_dim está
  errado — a rede recebe a resposta como pergunta.

- MLP (Perceptron Multicamadas): uma rede neural composta por camadas de neurônios
  totalmente conectados (Dense). Cada neurônio calcula uma soma ponderada das
  entradas, aplica uma função de ativação e passa o resultado adiante. A MLP
  aprende os pesos que minimizam o erro entre predição e realidade.

- shape: a forma dimensional de um array. Um dataset com 100 amostras e 5 features
  possui shape (100, 5). A MLP espera que o input tenha shape (n_amostras,
  input_dim). Se input_dim não coincide com o número de colunas do input, o
  TensorFlow lança um erro de shape incompatível.

- data leakage: quando informação do resultado (target) vaza para as features de
  entrada. A rede aprende a "colar" — em vez de descobrir padrões no sinal ECG,
  ela descobre que a coluna 188 contém a resposta diretamente. O resultado:
  performance perfeita no treino (a resposta está no input), performance nula em
  dados novos (onde a resposta não está disponível).

Uso:
    python docs/raciocinio/mlp-heartbeat/exemplos/demo_data_leakage.py

Referência:
    docs/raciocinio/mlp-heartbeat/01-inspecao-dataset.md — Operação 2
"""

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
np.random.seed(42)

# importar tensorflow com warnings suprimidos
import tensorflow as tf
tf.get_logger().setLevel("ERROR")
from tensorflow import keras
from tensorflow.keras import layers


def fabricar_dataset(n_treino: int = 500, n_teste: int = 200, n_features: int = 10):
    """Fabrica dataset sintético onde as features NÃO predizem a classe.

    As features são ruído aleatório puro — não possuem nenhuma relação com
    a classe. Qualquer modelo que atinja acurácia acima de 50% está
    necessariamente usando informação espúria (leakage), não padrões reais.
    """
    X_treino = np.random.randn(n_treino, n_features).astype(np.float32)
    y_treino = np.random.randint(0, 2, size=n_treino).astype(np.float32)

    X_teste = np.random.randn(n_teste, n_features).astype(np.float32)
    y_teste = np.random.randint(0, 2, size=n_teste).astype(np.float32)

    return X_treino, y_treino, X_teste, y_teste


def construir_mlp(input_dim: int) -> keras.Model:
    """Constrói uma MLP simples para classificação binária."""
    modelo = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(32, activation="relu"),
        layers.Dense(16, activation="relu"),
        layers.Dense(1, activation="sigmoid"),
    ])
    modelo.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return modelo


def cenario_1_correto():
    """Cenário correto: features e classe separados."""
    print("=" * 70)
    print("CENÁRIO 1: SEPARAÇÃO CORRETA (features sem a classe)")
    print("=" * 70)

    X_treino, y_treino, X_teste, y_teste = fabricar_dataset()

    print(f"\n  As features são ruído aleatório puro (np.random.randn).")
    print(f"  A classe é aleatória (np.random.randint).")
    print(f"  Não existe nenhuma relação entre features e classe.")
    print(f"  Um modelo honesto não consegue acurácia acima de ~50%.")

    print(f"\n  X_treino shape: {X_treino.shape} (500 amostras, 10 features)")
    print(f"  y_treino shape: {y_treino.shape} (500 rótulos)")
    print(f"  input_dim da MLP: {X_treino.shape[1]}")

    modelo = construir_mlp(X_treino.shape[1])
    modelo.fit(X_treino, y_treino, epochs=20, batch_size=32, verbose=0)

    _, acc_treino = modelo.evaluate(X_treino, y_treino, verbose=0)
    _, acc_teste = modelo.evaluate(X_teste, y_teste, verbose=0)

    print(f"\n  Resultado após 20 épocas:")
    print(f"    Acurácia treino: {acc_treino:.4f} ({acc_treino*100:.1f}%)")
    print(f"    Acurácia teste:  {acc_teste:.4f} ({acc_teste*100:.1f}%)")
    print(f"\n  INTERPRETAÇÃO:")
    print(f"    Ambas as acurácias flutuam em torno de 50% — exatamente o")
    print(f"    esperado quando as features não contêm informação sobre a classe.")
    print(f"    O modelo não aprendeu nada. Isso é o comportamento correto")
    print(f"    para dados sem sinal.")


def cenario_2_leakage():
    """Cenário com leakage: classe incluída como feature."""
    print(f"\n{'=' * 70}")
    print("CENÁRIO 2: DATA LEAKAGE (classe incluída como feature)")
    print("=" * 70)

    X_treino, y_treino, X_teste, y_teste = fabricar_dataset()

    # o engenheiro comete o erro: concatena a classe como última coluna do X
    # simulando o que acontece quando não separa X e y corretamente
    X_treino_vazado = np.column_stack([X_treino, y_treino])
    X_teste_vazado = np.column_stack([X_teste, y_teste])

    print(f"\n  O engenheiro concatenou a classe como coluna 11 do input.")
    print(f"  X_treino_vazado shape: {X_treino_vazado.shape} (500 amostras, 11 features)")
    print(f"  A coluna 11 É a resposta que o modelo tenta predizer.")
    print(f"  input_dim da MLP: {X_treino_vazado.shape[1]} (deveria ser 10)")

    print(f"\n  Verificação — a coluna 11 é idêntica a y_treino?")
    print(f"    np.array_equal(X_treino_vazado[:, -1], y_treino) = "
          f"{np.array_equal(X_treino_vazado[:, -1], y_treino)}")

    modelo = construir_mlp(X_treino_vazado.shape[1])
    modelo.fit(X_treino_vazado, y_treino, epochs=20, batch_size=32, verbose=0)

    _, acc_treino = modelo.evaluate(X_treino_vazado, y_treino, verbose=0)
    _, acc_teste = modelo.evaluate(X_teste_vazado, y_teste, verbose=0)

    print(f"\n  Resultado após 20 épocas:")
    print(f"    Acurácia treino: {acc_treino:.4f} ({acc_treino*100:.1f}%)")
    print(f"    Acurácia teste:  {acc_teste:.4f} ({acc_teste*100:.1f}%)")

    print(f"\n  INTERPRETAÇÃO:")
    print(f"    A acurácia é ~100% em AMBOS os conjuntos. Por que ambos?")
    print(f"    Porque a coluna vazada existe tanto no treino quanto no teste")
    print(f"    (o engenheiro cometeu o mesmo erro nos dois). A rede aprendeu:")
    print(f"    'se a coluna 11 é 1.0, a resposta é 1.0'. Ela ignora as 10")
    print(f"    features reais (que são ruído) e usa exclusivamente a resposta")
    print(f"    que o engenheiro entregou de bandeja.")
    print(f"\n    Este modelo nunca funcionaria em produção, onde a coluna de")
    print(f"    classe NÃO EXISTE no input — o paciente chega ao hospital e o")
    print(f"    médico precisa do diagnóstico, não possui o diagnóstico para")
    print(f"    alimentar o modelo.")


def cenario_3_producao():
    """Cenário de produção: modelo treinado com leakage recebe dados reais."""
    print(f"\n{'=' * 70}")
    print("CENÁRIO 3: O MODELO COM LEAKAGE EM PRODUÇÃO")
    print("=" * 70)

    X_treino, y_treino, X_teste, y_teste = fabricar_dataset()

    # treinar com leakage
    X_treino_vazado = np.column_stack([X_treino, y_treino])
    modelo = construir_mlp(X_treino_vazado.shape[1])
    modelo.fit(X_treino_vazado, y_treino, epochs=20, batch_size=32, verbose=0)

    _, acc_vazado = modelo.evaluate(X_treino_vazado, y_treino, verbose=0)
    print(f"\n  Modelo treinado com leakage: acurácia {acc_vazado:.4f}")
    print(f"  O engenheiro publica o modelo com orgulho de {acc_vazado*100:.0f}% de acurácia.")

    # em produção, os dados NÃO contêm a coluna de classe
    # o engenheiro tenta alimentar com 10 features (sem a classe)
    print(f"\n  Em produção, chega um novo paciente com 10 features (sem diagnóstico).")
    print(f"  O modelo espera 11 features (10 + a classe vazada).")
    print(f"  O que acontece?")

    novo_paciente = np.random.randn(1, 10).astype(np.float32)

    print(f"\n  novo_paciente shape: {novo_paciente.shape}")
    print(f"  modelo espera shape: (1, 11)")

    try:
        pred = modelo.predict(novo_paciente, verbose=0)
        print(f"  Predição: {pred}")
    except Exception as e:
        nome_erro = type(e).__name__
        msg = str(e)
        # extrair apenas a parte relevante da mensagem
        if "expected shape" in msg.lower() or "input" in msg.lower():
            print(f"\n  ERRO: {nome_erro}")
            print(f"  O TensorFlow recusa o input porque o shape não corresponde.")
            print(f"  A rede espera 11 features, recebeu 10.")

    print(f"\n  E se o engenheiro 'resolve' preenchendo a coluna faltante com 0?")
    novo_paciente_preenchido = np.column_stack([novo_paciente, [[0.0]]])
    pred = modelo.predict(novo_paciente_preenchido, verbose=0)
    print(f"  Predição com coluna extra = 0.0: {pred[0][0]:.4f}")
    print(f"  Classe predita: {'Anormal' if pred[0][0] >= 0.5 else 'Normal'}")

    novo_paciente_preenchido_1 = np.column_stack([novo_paciente, [[1.0]]])
    pred_1 = modelo.predict(novo_paciente_preenchido_1, verbose=0)
    print(f"  Predição com coluna extra = 1.0: {pred_1[0][0]:.4f}")
    print(f"  Classe predita: {'Anormal' if pred_1[0][0] >= 0.5 else 'Normal'}")

    print(f"\n  INTERPRETAÇÃO:")
    print(f"    O modelo produz predições completamente diferentes dependendo do")
    print(f"    valor que o engenheiro coloca na coluna fantasma. Se preenche com")
    print(f"    0.0, prediz Normal. Se preenche com 1.0, prediz Anormal. O modelo")
    print(f"    não analisa o sinal do paciente — repete o valor da coluna fantasma.")
    print(f"    As 10 features reais são irrelevantes para a decisão.")
    print(f"\n    Nenhum erro de Python. Nenhum warning do TensorFlow. O modelo")
    print(f"    responde com confiança a qualquer input. O resultado é lixo.")


def cenario_4_erro_shape():
    """Demonstra o erro de shape quando input_dim está errado."""
    print(f"\n{'=' * 70}")
    print("CENÁRIO 4: ERRO DE SHAPE (input_dim incompatível)")
    print("=" * 70)

    print(f"\n  Uma MLP definida com input_dim=187 espera arrays de 187 colunas.")
    print(f"  Se o engenheiro alimenta com 188 colunas (incluindo a classe),")
    print(f"  existem dois desfechos possíveis dependendo de QUANDO o erro ocorre:")

    # desfecho 1: erro no treino
    print(f"\n  Desfecho A — Erro no treino:")
    modelo_187 = construir_mlp(187)
    X_errado = np.random.randn(100, 188).astype(np.float32)
    y = np.random.randint(0, 2, size=100).astype(np.float32)

    try:
        modelo_187.fit(X_errado, y, epochs=1, verbose=0)
        print(f"    O TensorFlow aceitou silenciosamente (ajustou o input_dim).")
    except Exception as e:
        print(f"    ERRO: {type(e).__name__}")
        print(f"    O TensorFlow recusa porque o modelo espera 187 colunas")
        print(f"    e recebeu 188.")

    # desfecho 2: o engenheiro define input_dim=188 (errado mas compatível)
    print(f"\n  Desfecho B — O engenheiro 'corrige' com input_dim=188:")
    print(f"    O modelo treina sem erro — mas a coluna 188 É a classe.")
    print(f"    Isso é o data leakage do Cenário 2.")
    print(f"    Nenhum erro. Nenhum warning. Acurácia perfeita. Modelo inútil.")


def main():
    """Executa os 4 cenários de demonstração."""
    cenario_1_correto()
    cenario_2_leakage()
    cenario_3_producao()
    cenario_4_erro_shape()

    print(f"\n{'=' * 70}")
    print("SÍNTESE")
    print("=" * 70)
    print(f"""
  O MIT-BIH Heartbeat possui 188 colunas: 187 de sinal ECG + 1 de classe.
  O input_dim correto da MLP é 187. Se o engenheiro usa 188:

    Cenário A (input_dim=187, dados com 188 colunas):
      TensorFlow lança erro de shape. O engenheiro percebe e corrige.
      Este é o melhor caso — o erro é visível.

    Cenário B (input_dim=188, dados com 188 colunas):
      TensorFlow aceita silenciosamente. A coluna 188 (classe) entra como
      feature. A rede aprende a copiar a coluna 188 como output. Acurácia
      de 100%. O engenheiro publica o modelo. Em produção, onde a coluna
      de classe não existe, o modelo falha ou produz lixo.

  A verificação de dimensões (Operação 2 do script de exploração) existe
  para garantir que o engenheiro sabe EXATAMENTE quantas colunas são
  features e qual coluna é target ANTES de construir a rede. O custo da
  verificação é uma linha de print. O custo da omissão é um modelo que
  parece perfeito e não funciona.""")


if __name__ == "__main__":
    main()
