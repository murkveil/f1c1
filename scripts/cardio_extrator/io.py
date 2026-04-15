"""Carregamento de dados e caminhos padrão."""

from __future__ import annotations

import json
from pathlib import Path

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent.parent / "data" / "textuais"
ARQUIVO_RELATOS = DIRETORIO_DADOS / "sintomas_pacientes.txt"
ARQUIVO_MAPA = DIRETORIO_DADOS / "mapa_conhecimento.json"

def carregar_mapa(caminho: Path) -> dict:
    """Carrega o mapa de conhecimento JSON.

    Args:
        caminho: Caminho para o arquivo JSON.

    Returns:
        Dicionário com o mapa de conhecimento.
    """
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def carregar_relatos(caminho: Path) -> list[str]:
    """Carrega os relatos do arquivo TXT (um relato por linha).

    Args:
        caminho: Caminho para o arquivo TXT.

    Returns:
        Lista de relatos (strings).
    """
    with open(caminho, encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]
