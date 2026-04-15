"""Baixa o dataset MIT-BIH Heartbeat se não existir localmente.

Carrega credenciais do Kaggle a partir do arquivo .env na raiz do
repositório e baixa automaticamente via Kaggle CLI. Verifica a
integridade dos arquivos via SHA256 após o download.

Uso:
    python scripts/baixar_heartbeat.py
"""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIRETORIO_DESTINO = RAIZ_PROJETO / "data" / "numericos" / "heartbeat"
ARQUIVO_ENV = RAIZ_PROJETO / ".env"

ARQUIVOS_NECESSARIOS = ["mitbih_train.csv", "mitbih_test.csv"]

HASHES_SHA256 = {
    "mitbih_train.csv": "ae4c80504ad1d0be5c3f1b3c6ef02851e4d1b05d05805fce2a73374f083a700e",
    "mitbih_test.csv": "f3fdb3fd318275e653fac082b617d8c1ef09fca619a0606dc22c863451c77333",
}

KAGGLE_DATASET = "shayanfazeli/heartbeat"


def carregar_env() -> None:
    """Carrega variáveis de ambiente do arquivo .env.

    O .env contém KAGGLE_USERNAME e KAGGLE_KEY para autenticação
    automática no Kaggle CLI sem exigir configuração manual.
    """
    if not ARQUIVO_ENV.exists():
        return

    with open(ARQUIVO_ENV, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            if "=" in linha:
                chave, valor = linha.split("=", 1)
                os.environ[chave.strip()] = valor.strip()


def verificar_existencia() -> bool:
    """Verifica se os CSVs necessários existem no diretório de destino."""
    for arquivo in ARQUIVOS_NECESSARIOS:
        if not (DIRETORIO_DESTINO / arquivo).exists():
            return False
    return True


def verificar_integridade() -> bool:
    """Verifica SHA256 dos CSVs contra hashes conhecidos.

    Compara o hash de cada arquivo com o hash do dataset original
    do Kaggle para garantir que os dados não sofreram alteração.
    """
    for arquivo, hash_esperado in HASHES_SHA256.items():
        caminho = DIRETORIO_DESTINO / arquivo
        if not caminho.exists():
            return False
        sha256 = hashlib.sha256(caminho.read_bytes()).hexdigest()
        if sha256 != hash_esperado:
            print(f"  HASH INCORRETO: {arquivo}")
            print(f"    Esperado: {hash_esperado}")
            print(f"    Obtido:   {sha256}")
            return False
        print(f"  {arquivo}: SHA256 OK")
    return True


def baixar_via_kaggle() -> bool:
    """Baixa o dataset via Kaggle CLI usando credenciais do .env."""
    print("  Baixando via Kaggle CLI...")
    try:
        resultado = subprocess.run(
            ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET,
             "-p", str(DIRETORIO_DESTINO), "--unzip"],
            capture_output=True, text=True, timeout=300,
        )
        if resultado.returncode == 0:
            print("  Download concluído.")
            return True
        print(f"  Kaggle CLI falhou: {resultado.stderr.strip()}")
    except FileNotFoundError:
        print("  kaggle CLI não encontrado. Instale com: pip install kaggle")
    except subprocess.TimeoutExpired:
        print("  Timeout no download.")
    return False


def main() -> None:
    """Verifica existência, baixa se necessário e valida integridade."""
    print("=" * 60)
    print("DATASET MIT-BIH HEARTBEAT")
    print("=" * 60)

    # carregar credenciais do .env
    carregar_env()

    if verificar_existencia():
        print(f"\nArquivos encontrados em {DIRETORIO_DESTINO}/")
        if verificar_integridade():
            print("\nDataset pronto para uso.")
            return
        print("\nAVISO: arquivos existem mas a integridade falhou.")
        print("Rebaixando o dataset...\n")

    print(f"\nDataset não encontrado em {DIRETORIO_DESTINO}/")
    print("Iniciando download...\n")

    DIRETORIO_DESTINO.mkdir(parents=True, exist_ok=True)

    if baixar_via_kaggle():
        print("\nVerificando integridade...")
        if verificar_integridade():
            print("\nDataset baixado e verificado com sucesso.")
            return
        print("\nERRO: download concluído mas integridade falhou.")

    print("\n" + "=" * 60)
    print("DOWNLOAD MANUAL NECESSÁRIO")
    print("=" * 60)
    print(f"""
  O download automático não funcionou. Baixe manualmente:

  Kaggle (requer conta gratuita):
    https://www.kaggle.com/datasets/shayanfazeli/heartbeat
    Clique em "Download" e descompacte em:
    {DIRETORIO_DESTINO}/

  Arquivos necessários:
    mitbih_train.csv  (SHA256: {HASHES_SHA256['mitbih_train.csv']})
    mitbih_test.csv   (SHA256: {HASHES_SHA256['mitbih_test.csv']})
""")
    sys.exit(1)


if __name__ == "__main__":
    main()
