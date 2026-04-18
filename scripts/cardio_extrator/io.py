"""Carregamento de dados e caminhos padrão."""

from __future__ import annotations

import json
from pathlib import Path

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent.parent / "data" / "textuais"
ARQUIVO_RELATOS = DIRETORIO_DADOS / "sintomas_pacientes.txt"
ARQUIVO_MAPA = DIRETORIO_DADOS / "mapa_conhecimento.json"

_CHAVES_META_MAPA = {"intersecoes", "ambiguidades_clinicas", "red_flags"}


def carregar_mapa(caminho: Path) -> dict:
    """Carrega e valida o mapa de conhecimento JSON.

    Args:
        caminho: Caminho para o arquivo JSON.

    Returns:
        Dicionário com o mapa de conhecimento.

    Raises:
        ValueError: Se o arquivo carregado não tiver a estrutura esperada
            de um mapa de conhecimento (dicionário com configurações de
            doença contendo `scoring.sintomas`).
    """
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    _validar_estrutura_mapa(dados, caminho)
    return dados


def _validar_estrutura_mapa(dados: object, caminho: Path) -> None:
    """Verifica que `dados` tem a estrutura esperada de mapa de conhecimento.

    O mapa é um dicionário cujas chaves são nomes de doenças (fora as de
    metadados em `_CHAVES_META_MAPA`), e cada valor é um dicionário com
    pelo menos `scoring.sintomas`.
    """
    if not isinstance(dados, dict):
        raise ValueError(
            f"Arquivo {caminho} não contém um mapa de conhecimento válido: "
            f"esperado objeto JSON no topo, encontrado {type(dados).__name__}.",
        )

    chaves_doenca = [k for k in dados if k not in _CHAVES_META_MAPA]
    if not chaves_doenca:
        raise ValueError(
            f"Arquivo {caminho} não contém nenhuma doença: todas as chaves "
            f"({sorted(dados)}) são metadados. Verifique se o arquivo é o "
            f"mapa de conhecimento (ex.: data/textuais/mapa_conhecimento.json) "
            f"e não uma saída do próprio cardio_extrator.",
        )

    for chave in chaves_doenca:
        config = dados[chave]
        if not isinstance(config, dict) or "scoring" not in config or \
                "sintomas" not in config.get("scoring", {}):
            raise ValueError(
                f"Arquivo {caminho} não é um mapa de conhecimento válido: "
                f"chave '{chave}' não tem a estrutura esperada "
                f"`scoring.sintomas`. Confirme que está passando o arquivo "
                f"correto via --mapa (ex.: data/textuais/mapa_conhecimento.json).",
            )


def carregar_relatos(caminho: Path) -> list[str]:
    """Carrega os relatos do arquivo TXT (um relato por linha).

    Args:
        caminho: Caminho para o arquivo TXT.

    Returns:
        Lista de relatos (strings).
    """
    with open(caminho, encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]
