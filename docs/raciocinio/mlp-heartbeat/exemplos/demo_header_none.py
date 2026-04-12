"""Demonstração: o efeito de omitir header=None em CSV sem cabeçalho.

Este script complementa a Seção I do documento docs/raciocinio-mlp-heartbeat.md.
O documento afirma que omitir header=None corrompe a primeira linha de dados como
nomes de colunas. Este script prova a afirmação com evidência reproduzível.

O leitor executa o script e observa, célula por célula, exatamente o que o pandas
faz internamente quando recebe um CSV numérico sem instrução de que não há cabeçalho.
Cada seção do output corresponde a uma consequência concreta e verificável.

Uso:
    python docs/raciocinio/mlp-heartbeat/exemplos/demo_header_none.py

Referência:
    docs/raciocinio/mlp-heartbeat/01-inspecao-dataset.md — Operação 1
"""

from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent.parent.parent
ARQUIVO = RAIZ_PROJETO / "data" / "numericos" / "heartbeat" / "mitbih_train.csv"


def main() -> None:
    """Executa a demonstração comparativa."""

    # --- carregamento correto vs incorreto ---
    correto = pd.read_csv(ARQUIVO, header=None)
    incorreto = pd.read_csv(ARQUIVO)  # header=0 é o padrão do pandas

    print("=" * 70)
    print("DEMONSTRAÇÃO: EFEITO DE OMITIR header=None")
    print("=" * 70)

    # --- 1. dimensões ---
    # O pandas consome a primeira linha como cabeçalho, reduzindo o dataset
    # em exatamente 1 amostra. Em 87.554 amostras, 1 amostra perdida parece
    # insignificante — mas o engenheiro que não percebe a discrepância
    # trabalha com premissa falsa sobre o tamanho do dataset.

    print(f"\n--- 1. DIMENSÕES ---")
    print(f"  Correto (header=None):  {correto.shape[0]:>6,} linhas x {correto.shape[1]} colunas")
    print(f"  Incorreto (default):    {incorreto.shape[0]:>6,} linhas x {incorreto.shape[1]} colunas")
    print(f"  Diferença:              {correto.shape[0] - incorreto.shape[0]:>6,} linha perdida")

    # --- 2. nomes das colunas ---
    # O pandas converte os 188 valores numéricos do primeiro batimento em
    # strings e os utiliza como nomes de colunas. O nome da coluna 0 torna-se
    # "9.779411554336547852e-01" — a amplitude do primeiro ponto do sinal ECG
    # do primeiro paciente, agora promovida a identificador de feature.

    print(f"\n--- 2. NOMES DAS COLUNAS ---")
    print(f"  Correto:")
    print(f"    {list(correto.columns[:5])}...")
    print(f"    Tipo: inteiros sequenciais (0, 1, 2, ..., 187)")
    print(f"  Incorreto:")
    print(f"    {list(incorreto.columns[:3])}...")
    print(f"    Tipo: strings de notação científica (valores do 1o batimento)")

    # --- 3. a linha destruída ---
    # O primeiro batimento do dataset é um registro clínico real. Ao promovê-lo
    # a cabeçalho, o pandas destrói esse registro de forma irrecuperável: os
    # dados existem como nomes de colunas (strings), não como observação
    # (float64). Nenhuma operação subsequente sobre o DataFrame recupera
    # essa amostra como dado numérico utilizável.

    print(f"\n--- 3. A LINHA DESTRUÍDA ---")
    primeira_linha = correto.iloc[0, :10].values
    print(f"  Dados reais do 1o batimento (10 primeiras amostras):")
    print(f"    {primeira_linha}")
    print(f"  O que o pandas faz com esses dados sem header=None:")
    print(f"    Promove como NOMES de colunas:")
    for i, nome in enumerate(list(incorreto.columns[:5])):
        valor_real = correto.iloc[0, i]
        print(f"      Coluna {i}: nome=\"{nome}\" (era o valor {valor_real:.8f})")

    # --- 4. tipos de dados ---
    # Neste dataset específico, a contaminação de tipos não ocorre porque
    # todos os valores são float64 — o pandas infere o dtype correto para as
    # linhas restantes. Em datasets onde a primeira linha contém valores
    # inteiros ou mistos, a promoção a cabeçalho pode forçar colunas inteiras
    # a dtype object (string), quebrando operações numéricas silenciosamente.

    print(f"\n--- 4. TIPOS DE DADOS ---")
    print(f"  Correto - dtype coluna 0:   {correto[0].dtype}")
    print(f"  Incorreto - dtype coluna 0: {incorreto.iloc[:, 0].dtype}")
    print(f"  Neste caso os tipos coincidem porque todas as linhas restantes")
    print(f"  são float64. Em CSVs com tipos mistos, a contaminação seria severa.")

    # --- 5. impacto na coluna de classe ---
    # A classe do batimento destruído era 0.0 (Normal). A distribuição de
    # classes no carregamento incorreto perde exatamente 1 amostra da classe
    # Normal. Com 72.471 amostras normais, a perda de 1 é estatisticamente
    # irrelevante — mas o princípio é o mesmo que perderia 1.000 amostras
    # se o CSV tivesse 1.000 linhas de cabeçalho falso.

    classe_destruida = correto.iloc[0, -1]
    nome_classe = "Normal" if classe_destruida == 0.0 else "Anormal"
    print(f"\n--- 5. IMPACTO NA COLUNA DE CLASSE ---")
    print(f"  Classe do batimento destruído: {int(classe_destruida)} ({nome_classe})")

    classe_correto = correto.iloc[:, -1]
    classe_incorreto = incorreto.iloc[:, -1]

    print(f"\n  Distribuição comparada:")
    print(f"    {'Classe':10s} {'Correto':>10s} {'Incorreto':>10s} {'Diff':>6s}")
    print(f"    {'-' * 40}")
    for c in [0.0, 1.0, 2.0, 3.0, 4.0]:
        n_c = (classe_correto == c).sum()
        n_i = (classe_incorreto == c).sum()
        diff = n_c - n_i
        marca = " <--" if diff != 0 else ""
        print(f"    Classe {int(c):2d} {n_c:>10,} {n_i:>10,} {diff:>+5d}{marca}")

    # --- 6. o que acontece ao treinar ---
    # O numpy converte o DataFrame incorreto para float64 sem reclamar.
    # O shape muda de (87554, 187) para (87553, 187). O modelo treina
    # normalmente com 1 amostra a menos. Nenhum erro, nenhum warning,
    # nenhum indício de que algo está errado. O erro é completamente
    # silencioso — a pior categoria de erro em engenharia de software.

    print(f"\n--- 6. COMPORTAMENTO NO TREINAMENTO ---")
    X_correto = correto.iloc[:, :-1].values
    X_incorreto = incorreto.iloc[:, :-1].values
    print(f"  X correto:   shape {X_correto.shape}, dtype {X_correto.dtype}")
    print(f"  X incorreto: shape {X_incorreto.shape}, dtype {X_incorreto.dtype}")
    print(f"  O numpy converte silenciosamente. Nenhum erro. Nenhum warning.")
    print(f"  O modelo treina com {X_correto.shape[0] - X_incorreto.shape[0]} amostra a menos.")
    print(f"  O engenheiro não percebe a menos que inspecione os dados antes.")

    # --- 7. resumo ---
    print(f"\n{'=' * 70}")
    print(f"CONCLUSÃO")
    print(f"{'=' * 70}")
    print(f"  Omitir header=None em CSV sem cabeçalho causa 5 efeitos concretos:")
    print(f"")
    print(f"    1. Perda de 1 amostra — a primeira linha vira cabeçalho")
    print(f"    2. Nomes de colunas incoerentes — valores numéricos viram strings")
    print(f"    3. Possível contaminação de tipos — float64 pode virar object")
    print(f"    4. Contagem de amostras incorreta — 87.553 em vez de 87.554")
    print(f"    5. Distribuição de classes alterada — 1 amostra a menos na classe {int(classe_destruida)}")
    print(f"")
    print(f"  Nenhum desses efeitos produz erro ou warning do Python.")
    print(f"  O engenheiro que não inspeciona os dados antes de treinar")
    print(f"  jamais descobre que trabalha sobre premissa falsa.")


if __name__ == "__main__":
    main()
