"""Demonstração: quando omitir header=None causa resultado catastrófico.

A demonstração anterior (demo_header_none.py) prova que o MIT-BIH perde 1 amostra
de 87.554 — consequência real porém benigna. Este script demonstra os cenários onde
a mesma omissão produz resultado grotescamente incorreto: modelo que treina, converge,
reporta métricas, e entrega predições completamente erradas sem que nenhum erro ou
warning alerte o engenheiro.

O script fabrica 3 CSVs sintéticos que simulam situações reais onde a omissão
de header=None causa caos:

Cenário 1 — Primeira linha é outlier extremo
    O primeiro paciente possui valores atípicos. Ao virar cabeçalho, o pandas
    remove o único outlier do dataset. O modelo treina sem nunca ver esse padrão,
    e falha silenciosamente ao encontrá-lo em produção.

Cenário 2 — Primeira linha contém inteiros que alteram dtype
    O primeiro paciente possui valores inteiros (idade=65, pressão=140). Ao virar
    cabeçalho, esses inteiros tornam-se strings. O pandas infere dtype das colunas
    restantes sem considerar o cabeçalho — mas qualquer operação que referencie
    colunas por nome (df["65"]) quebra silenciosamente porque "65" é string, não int.

Cenário 3 — Dataset pequeno onde 1 amostra muda a distribuição de classes
    Um dataset com 10 amostras (5 normais, 5 anormais) perde o primeiro registro.
    Se esse registro era da classe minoritária, a distribuição muda de 50/50 para
    56/44. Com datasets clínicos pequenos (50-200 amostras), perder 1 amostra da
    classe rara pode eliminar o único exemplo de uma variante clínica específica.

Uso:
    python docs/raciocinio/mlp-heartbeat/exemplos/demo_header_none_catastrofico.py

Referência:
    docs/raciocinio/mlp-heartbeat/01-inspecao-dataset.md — Operação 1
"""

import csv
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


def cenario_1_outlier() -> None:
    """Primeira linha é o único outlier — removê-la cega o modelo."""
    print("=" * 70)
    print("CENÁRIO 1: PRIMEIRA LINHA É OUTLIER EXTREMO")
    print("=" * 70)

    # fabricar dataset onde a primeira linha é um paciente com valores extremos
    # que representa exatamente o caso raro que o modelo precisa detectar
    np.random.seed(42)
    n = 100

    # 99 pacientes normais: features entre 0.1 e 0.5
    normais = np.random.uniform(0.1, 0.5, size=(n - 1, 5))
    classes_normais = np.zeros(n - 1)

    # 1 paciente crítico (outlier): features entre 0.9 e 1.0
    # este paciente representa uma arritmia ventricular rara
    outlier = np.array([[0.95, 0.98, 0.92, 0.97, 0.99]])
    classe_outlier = np.array([1.0])

    # o outlier é a PRIMEIRA linha do CSV
    dados = np.vstack([outlier, normais])
    classes = np.concatenate([classe_outlier, classes_normais])
    completo = np.column_stack([dados, classes])

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        caminho = f.name
        writer = csv.writer(f)
        for linha in completo:
            writer.writerow(linha)

    # carregar corretamente
    correto = pd.read_csv(caminho, header=None)
    incorreto = pd.read_csv(caminho)

    print(f"\n  Dataset: {n} pacientes, 5 features, 1 classe")
    print(f"  Primeiro paciente: outlier com arritmia rara (valores 0.92-0.99)")
    print(f"  Demais pacientes: normais (valores 0.10-0.50)")

    print(f"\n  Correto (header=None):")
    print(f"    Amostras: {correto.shape[0]}")
    print(f"    Classe 1 (anormal): {(correto.iloc[:, -1] == 1.0).sum()} amostra(s)")
    print(f"    Max da feature 0: {correto.iloc[:, 0].max():.2f}")

    print(f"\n  Incorreto (sem header=None):")
    print(f"    Amostras: {incorreto.shape[0]}")
    print(f"    Classe 1 (anormal): {(incorreto.iloc[:, -1] == 1.0).sum()} amostra(s)")
    print(f"    Max da feature 0: {incorreto.iloc[:, 0].max():.2f}")

    print(f"\n  CONSEQUÊNCIA:")
    print(f"    O carregamento correto contém 1 amostra anormal (o outlier).")
    print(f"    O carregamento incorreto contém 0 amostras anormais.")
    print(f"    O modelo treinado sobre o dataset incorreto NUNCA VÊ um exemplo")
    print(f"    de arritmia. Quando encontra um em produção, classifica como normal.")
    print(f"    Resultado: falso negativo em 100% dos casos anormais.")
    print(f"    O modelo reporta 100% de acurácia no treino — porque só existem")
    print(f"    amostras normais. O engenheiro celebra. O paciente morre.")

    Path(caminho).unlink()


def cenario_2_dtype() -> None:
    """Primeira linha contém inteiros que corrompem referências por nome."""
    print(f"\n{'=' * 70}")
    print("CENÁRIO 2: TIPOS MISTOS CORROMPEM REFERÊNCIAS POR NOME")
    print("=" * 70)

    # fabricar CSV com primeira linha de inteiros e demais de floats
    # simula um dataset clínico onde a primeira observação possui
    # valores arredondados (idade=65, pressão=140, glicemia=200)
    linhas = [
        [65, 140, 200, 1],       # paciente 1: inteiros arredondados
        [42.5, 121.3, 95.7, 0],  # paciente 2: floats
        [58.2, 138.8, 110.4, 1], # paciente 3: floats
        [31.0, 105.0, 88.0, 0],  # paciente 4: floats
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        caminho = f.name
        writer = csv.writer(f)
        for linha in linhas:
            writer.writerow(linha)

    correto = pd.read_csv(caminho, header=None)
    incorreto = pd.read_csv(caminho)

    print(f"\n  Dataset: 4 pacientes (idade, pressão, glicemia, classe)")
    print(f"  Primeiro paciente: valores inteiros (65, 140, 200, 1)")

    print(f"\n  Correto (header=None):")
    print(f"    Colunas: {list(correto.columns)}")
    print(f"    Primeira linha: {correto.iloc[0].tolist()}")
    print(f"    Amostras: {correto.shape[0]}")

    print(f"\n  Incorreto (sem header=None):")
    print(f"    Colunas: {list(incorreto.columns)}")
    print(f"    Primeira linha: {incorreto.iloc[0].tolist()}")
    print(f"    Amostras: {incorreto.shape[0]}")

    print(f"\n  O que acontece ao tentar acessar colunas:")
    print(f"    correto[0] funciona? ", end="")
    try:
        _ = correto[0]
        print("Sim")
    except Exception as e:
        print(f"Erro: {e}")

    print(f"    incorreto[0] funciona? ", end="")
    try:
        _ = incorreto[0]
        print("Sim")
    except Exception as e:
        print(f"Erro: {type(e).__name__}: {e}")

    print(f"\n    incorreto['65'] funciona? ", end="")
    try:
        _ = incorreto['65']
        print(f"Sim — retorna a coluna 'idade' que agora chama '65'")
    except Exception as e:
        print(f"Erro: {e}")

    print(f"\n  CONSEQUÊNCIA:")
    print(f"    Qualquer código que referencia colunas por índice inteiro")
    print(f"    (df[0], df[1]) falha com KeyError porque os nomes das colunas")
    print(f"    são strings ('65', '140', '200', '1'), não inteiros.")
    print(f"    O código que funcionava em desenvolvimento (com header=None)")
    print(f"    quebra em produção (sem header=None) sem nenhum warning prévio.")

    Path(caminho).unlink()


def cenario_3_dataset_pequeno() -> None:
    """Dataset pequeno onde 1 amostra perdida elimina variante clínica."""
    print(f"\n{'=' * 70}")
    print("CENÁRIO 3: DATASET PEQUENO — 1 AMOSTRA MUDA TUDO")
    print("=" * 70)

    # fabricar dataset com 10 amostras onde a primeira é o ÚNICO exemplo
    # de uma subclasse rara (ex: arritmia de fusão, classe 3 no MIT-BIH)
    np.random.seed(42)

    # 5 normais (classe 0), 4 anormais comuns (classe 1), 1 fusão rara (classe 3)
    # a fusão rara é a PRIMEIRA linha
    features_fusao = np.array([[0.85, 0.72, 0.91]])  # padrão único de fusão
    features_normais = np.random.uniform(0.1, 0.4, size=(5, 3))
    features_anormais = np.random.uniform(0.5, 0.8, size=(4, 3))

    dados = np.vstack([features_fusao, features_normais, features_anormais])
    classes = np.array([3, 0, 0, 0, 0, 0, 1, 1, 1, 1]).reshape(-1, 1)
    completo = np.hstack([dados, classes])

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        caminho = f.name
        writer = csv.writer(f)
        for linha in completo:
            writer.writerow(linha.tolist())

    correto = pd.read_csv(caminho, header=None)
    incorreto = pd.read_csv(caminho)

    print(f"\n  Dataset: 10 pacientes, 3 features")
    print(f"  Composição: 5 normais (classe 0), 4 anormais (classe 1), 1 fusão (classe 3)")
    print(f"  A fusão é a PRIMEIRA linha — o único exemplo dessa variante clínica")

    print(f"\n  Correto (header=None):")
    classes_correto = correto.iloc[:, -1]
    for c in sorted(classes_correto.unique()):
        n = (classes_correto == c).sum()
        print(f"    Classe {int(c)}: {n} amostras")

    print(f"\n  Incorreto (sem header=None):")
    classes_incorreto = incorreto.iloc[:, -1]
    for c in sorted(classes_incorreto.unique()):
        n = (classes_incorreto == c).sum()
        print(f"    Classe {int(c)}: {n} amostras")

    fusao_correto = (classes_correto == 3).sum()
    fusao_incorreto = (classes_incorreto == 3).sum()

    print(f"\n  Classe 3 (fusão rara):")
    print(f"    Correto:   {fusao_correto} amostra")
    print(f"    Incorreto: {fusao_incorreto} amostras")

    print(f"\n  CONSEQUÊNCIA:")
    print(f"    O dataset incorreto NÃO CONTÉM nenhum exemplo de fusão.")
    print(f"    Se o modelo precisa classificar fusão (multiclasse), a classe 3")
    print(f"    simplesmente não existe no treino. O modelo nunca aprende o padrão.")
    print(f"    Se o modelo agrupa em binário (normal vs anormal), perde o ÚNICO")
    print(f"    exemplo do subtipo mais raro — exatamente o que mais precisa aprender.")
    print(f"")
    print(f"    Em datasets clínicos com 50-200 amostras (como o Ir Além 2b com 50")
    print(f"    imagens de ECG), perder 1 amostra significa perder 2-6% do dataset")
    print(f"    e potencialmente 100% de uma variante clínica rara.")

    Path(caminho).unlink()


def main() -> None:
    """Executa as 3 demonstrações de cenários catastróficos."""
    cenario_1_outlier()
    cenario_2_dtype()
    cenario_3_dataset_pequeno()

    print(f"\n{'=' * 70}")
    print("SÍNTESE")
    print("=" * 70)
    print(f"""
  O MIT-BIH Heartbeat perde 1 amostra de 87.554 — ruído estatístico.
  A gravidade do erro escala inversamente com o tamanho do dataset e
  diretamente com a raridade da primeira observação:

    Dataset grande + primeira linha comum     = incômodo menor
    Dataset grande + primeira linha é outlier  = modelo cego a caso raro
    Dataset pequeno + primeira linha é única   = classe inteira desaparece

  O princípio que justifica SEMPRE usar header=None em CSVs sem cabeçalho
  não deriva da gravidade do caso MIT-BIH especificamente. Deriva do fato
  de que o engenheiro não sabe, no momento do carregamento, se a primeira
  linha é dispensável ou insubstituível. A verificação custa uma keyword.
  A omissão custa, no pior caso, um modelo que reporta métricas perfeitas
  sobre dados corrompidos.""")


if __name__ == "__main__":
    main()
