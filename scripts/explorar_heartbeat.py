"""Exploração inicial do dataset MIT-BIH Heartbeat.

Inspeciona estrutura, distribuição de classes, range de valores e formato
dos sinais de ECG. Os achados deste script determinam todas as decisões de
pré-processamento e arquitetura do notebook mlp_heartbeat.ipynb.

Uso:
    python scripts/explorar_heartbeat.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent / "data" / "numericos" / "heartbeat"
ARQUIVO_TREINO = DIRETORIO_DADOS / "mitbih_train.csv"
ARQUIVO_TESTE = DIRETORIO_DADOS / "mitbih_test.csv"

NOMES_CLASSES = {
    0: "Normal (N)",
    1: "Supraventricular (S)",
    2: "Ventricular (V)",
    3: "Fusão (F)",
    4: "Desconhecido (Q)",
}


def main() -> None:
    """Executa a inspeção completa do dataset."""

    # 1. carregar sem cabeçalho — o MIT-BIH não possui nomes de colunas
    treino = pd.read_csv(ARQUIVO_TREINO, header=None)
    teste = pd.read_csv(ARQUIVO_TESTE, header=None)

    print("=" * 60)
    print("INSPEÇÃO DO DATASET MIT-BIH HEARTBEAT")
    print("=" * 60)

    # 2. dimensões — revela quantas amostras e quantas features
    print(f"\nDimensões:")
    print(f"  Treino: {treino.shape[0]:>6,} amostras x {treino.shape[1]} colunas")
    print(f"  Teste:  {teste.shape[0]:>6,} amostras x {teste.shape[1]} colunas")
    print(f"  Features (sinal ECG): {treino.shape[1] - 1} amostras por batimento")
    print(f"  Última coluna: classe (target)")

    # 3. distribuição de classes — revela o desbalanceamento
    print(f"\nDistribuição de classes (treino):")
    print("-" * 50)
    for c in sorted(treino.iloc[:, -1].unique()):
        n = (treino.iloc[:, -1] == c).sum()
        nome = NOMES_CLASSES.get(int(c), "?")
        barra = "#" * int(n / treino.shape[0] * 40)
        print(f"  Classe {int(c)} {nome:25s}: {n:>6,} ({n / len(treino) * 100:5.1f}%) {barra}")

    print(f"\nDistribuição de classes (teste):")
    print("-" * 50)
    for c in sorted(teste.iloc[:, -1].unique()):
        n = (teste.iloc[:, -1] == c).sum()
        nome = NOMES_CLASSES.get(int(c), "?")
        print(f"  Classe {int(c)} {nome:25s}: {n:>6,} ({n / len(teste) * 100:5.1f}%)")

    # 4. distribuição binária — o que a binarização produz
    y_treino_bin = (treino.iloc[:, -1] > 0).astype(int)
    n_normal = (y_treino_bin == 0).sum()
    n_anormal = (y_treino_bin == 1).sum()
    print(f"\nDistribuição binária (Normal vs Anormal):")
    print(f"  Normal:  {n_normal:>6,} ({n_normal / len(treino) * 100:.1f}%)")
    print(f"  Anormal: {n_anormal:>6,} ({n_anormal / len(treino) * 100:.1f}%)")
    print(f"  Razão Normal/Anormal: {n_normal / n_anormal:.1f}x")

    # 5. range de valores — determina se normalização é necessária
    valores = treino.iloc[:, :-1].values
    print(f"\nRange dos valores do sinal:")
    print(f"  Mínimo global: {valores.min():.6f}")
    print(f"  Máximo global: {valores.max():.6f}")
    print(f"  Média global:  {valores.mean():.6f}")
    print(f"  Desvio padrão: {valores.std():.6f}")

    # 6. amostra concreta — o que um batimento contém
    print(f"\nAmostra do primeiro batimento (primeiras 10 de 187 amostras):")
    print(f"  {treino.iloc[0, :10].values}")

    # 7. verificar valores ausentes
    nulos_treino = treino.isnull().sum().sum()
    nulos_teste = teste.isnull().sum().sum()
    print(f"\nValores ausentes:")
    print(f"  Treino: {nulos_treino}")
    print(f"  Teste:  {nulos_teste}")

    # 8. verificar proporções treino/teste por classe
    print(f"\nConsistência treino/teste (proporções devem ser similares):")
    print(f"  {'Classe':25s} {'Treino':>8s} {'Teste':>8s} {'Diff':>8s}")
    print(f"  {'-' * 49}")
    for c in sorted(treino.iloc[:, -1].unique()):
        pct_treino = (treino.iloc[:, -1] == c).sum() / len(treino) * 100
        pct_teste = (teste.iloc[:, -1] == c).sum() / len(teste) * 100
        diff = abs(pct_treino - pct_teste)
        nome = NOMES_CLASSES.get(int(c), "?")
        print(f"  {nome:25s} {pct_treino:7.1f}% {pct_teste:7.1f}% {diff:7.1f}%")

    # 9. class_weight que será necessário
    from sklearn.utils.class_weight import compute_class_weight
    pesos = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_treino_bin.values)
    print(f"\nclass_weight calculado (para compensar desbalanceamento):")
    print(f"  Normal (0):  {pesos[0]:.4f}")
    print(f"  Anormal (1): {pesos[1]:.4f}")
    print(f"  Fator de amplificação Anormal: {pesos[1] / pesos[0]:.1f}x")

    print(f"\n{'=' * 60}")
    print("CONCLUSÕES PARA O NOTEBOOK")
    print("=" * 60)
    print(f"  1. Dados já normalizados [0, 1] — MinMaxScaler desnecessário")
    print(f"  2. Sem valores ausentes — nenhuma imputação necessária")
    print(f"  3. Desbalanceamento severo (82.8% vs 17.2%) — class_weight obrigatório")
    print(f"  4. Proporções treino/teste consistentes — split do Kaggle é estratificado")
    print(f"  5. 187 features por batimento — input_dim=187 na MLP")
    print(f"  6. Acurácia baseline (sempre Normal): {n_normal / len(treino) * 100:.1f}%")
    print(f"     Qualquer modelo deve superar {n_normal / len(treino) * 100:.1f}% para ter valor")


if __name__ == "__main__":
    main()
