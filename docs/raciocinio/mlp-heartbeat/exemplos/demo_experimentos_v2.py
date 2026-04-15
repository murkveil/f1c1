"""Demonstração: experimentos para correção do modelo v1.

Este script complementa o capítulo IX do documento
docs/raciocinio/mlp-heartbeat/09-experimentos-v2.md. O capítulo VIII diagnosticou
4 causas para a falha do modelo v1 (recall Anormal de 5.17%). Este script testa
3 variantes de correção e demonstra que embaralhar os dados antes do treino
resolve o problema principal — a diferença entre 5.17% e ~94% de recall resume-se
a 3 linhas de código (np.random.permutation).

As 3 variantes testadas:
  A: sem BatchNorm, lr=0.0005 — aplica C1+C2+C3+C4
  B: com BatchNorm, lr=0.0005 — aplica C1+C2+C3
  C: sem BatchNorm, lr=0.001  — aplica C1+C3+C4

Uso:
    python docs/raciocinio/mlp-heartbeat/exemplos/demo_experimentos_v2.py

Referência:
    docs/raciocinio/mlp-heartbeat/09-experimentos-v2.md
"""

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import pandas as pd
from pathlib import Path

import tensorflow as tf
tf.get_logger().setLevel("ERROR")
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import precision_recall_fscore_support

RAIZ = Path(__file__).resolve().parent.parent.parent.parent.parent
TREINO = RAIZ / "data" / "numericos" / "heartbeat" / "mitbih_train.csv"
TESTE = RAIZ / "data" / "numericos" / "heartbeat" / "mitbih_test.csv"


def main() -> None:
    """Executa os 3 experimentos comparativos."""
    train = pd.read_csv(TREINO, header=None)
    test = pd.read_csv(TESTE, header=None)

    X_treino = train.iloc[:, :-1].values
    y_treino = (train.iloc[:, -1].values > 0).astype(int)
    X_teste = test.iloc[:, :-1].values
    y_teste = (test.iloc[:, -1].values > 0).astype(int)

    # C1: embaralhar — a correção mais importante
    np.random.seed(42)
    idx = np.random.permutation(len(X_treino))
    X_treino = X_treino[idx]
    y_treino = y_treino[idx]

    pesos = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_treino)
    cw = {0: pesos[0], 1: pesos[1]}

    print("=" * 70)
    print("EXPERIMENTOS: CORREÇÕES DO MODELO V1")
    print("=" * 70)
    print(f"\nclass_weight: Normal={cw[0]:.4f}, Anormal={cw[1]:.4f}")
    print(f"Dados embaralhados: Sim (C1 aplicada em todas as variantes)")

    configs = [
        {"nome": "A: sem BatchNorm, lr=0.0005", "batchnorm": False, "lr": 0.0005},
        {"nome": "B: com BatchNorm, lr=0.0005", "batchnorm": True, "lr": 0.0005},
        {"nome": "C: sem BatchNorm, lr=0.001", "batchnorm": False, "lr": 0.001},
    ]

    resultados = []

    for cfg in configs:
        tf.random.set_seed(42)

        camadas = [layers.Input(shape=(187,))]
        for units, drop in [(128, 0.3), (64, 0.3), (32, 0.2)]:
            camadas.append(layers.Dense(units, activation="relu"))
            if cfg["batchnorm"]:
                camadas.append(layers.BatchNormalization())
            camadas.append(layers.Dropout(drop))
        camadas.append(layers.Dense(1, activation="sigmoid"))

        modelo = keras.Sequential(camadas)
        modelo.compile(
            optimizer=keras.optimizers.Adam(learning_rate=cfg["lr"]),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        es = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True,
        )
        hist = modelo.fit(
            X_treino, y_treino, epochs=50, batch_size=256,
            validation_split=0.15, class_weight=cw, callbacks=[es], verbose=0,
        )

        y_pred = (modelo.predict(X_teste, verbose=0).flatten() >= 0.5).astype(int)
        prec, rec, f1, _ = precision_recall_fscore_support(y_teste, y_pred, average=None)

        r = {
            "nome": cfg["nome"],
            "epocas": len(hist.history["loss"]),
            "acc": (y_pred == y_teste).mean(),
            "rec_normal": rec[0],
            "rec_anormal": rec[1],
            "f1_normal": f1[0],
            "f1_anormal": f1[1],
            "f1_macro": (f1[0] + f1[1]) / 2,
        }
        resultados.append(r)

        print(f"\n--- {cfg['nome']} ---")
        print(f"  Épocas treinadas: {r['epocas']}")
        print(f"  Acurácia:         {r['acc']:.4f}")
        print(f"  Recall Normal:    {r['rec_normal']:.4f}")
        print(f"  Recall Anormal:   {r['rec_anormal']:.4f}")
        print(f"  F1 Normal:        {r['f1_normal']:.4f}")
        print(f"  F1 Anormal:       {r['f1_anormal']:.4f}")
        print(f"  F1-macro:         {r['f1_macro']:.4f}")

    print(f"\n{'=' * 70}")
    print("COMPARAÇÃO COM V1")
    print("=" * 70)
    print(f"\n  {'Métrica':20s} {'v1':>8s} {'A':>8s} {'B':>8s} {'C':>8s}")
    print(f"  {'-' * 50}")
    print(f"  {'Recall Anormal':20s} {'0.052':>8s}", end="")
    for r in resultados:
        print(f" {r['rec_anormal']:>8.3f}", end="")
    print()
    print(f"  {'F1-macro':20s} {'0.504':>8s}", end="")
    for r in resultados:
        print(f" {r['f1_macro']:>8.3f}", end="")
    print()
    print(f"  {'Acurácia':20s} {'0.836':>8s}", end="")
    for r in resultados:
        print(f" {r['acc']:>8.3f}", end="")
    print()

    melhor = max(resultados, key=lambda r: r["f1_macro"])
    print(f"\n  Melhor variante por F1-macro: {melhor['nome']}")
    print(f"  Melhoria recall Anormal v1→v2: {melhor['rec_anormal']/0.052:.0f}x")


if __name__ == "__main__":
    main()
