"""Interface de linha de comando do extrator cardiovascular."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .formatacao import formatar_resultado
from .inferencia import CHAVES_META, pre_calcular_scores_maximos
from .io import ARQUIVO_MAPA, ARQUIVO_RELATOS, carregar_mapa, carregar_relatos
from .modelos import ResultadoAnalise
from .pipeline import analisar_relato

logger = logging.getLogger("cardio_extrator")


def _configurar_logging(nivel: str) -> None:
    """Configura o logging estruturado do pipeline.

    Args:
        nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR).
    """
    logging.basicConfig(
        level=getattr(logging, nivel.upper(), logging.WARNING),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def _parse_args() -> argparse.Namespace:
    """Processa argumentos de linha de comando.

    Returns:
        Namespace com os argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Extração de sintomas e diagnóstico cardiovascular",
    )
    parser.add_argument(
        "--formato",
        choices=["texto", "json", "ambos"],
        default="texto",
        help="formato de saída (padrão: texto)",
    )
    parser.add_argument(
        "--saida",
        type=str,
        default=None,
        help="arquivo de saída (padrão: stdout)",
    )
    parser.add_argument(
        "--log",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="nível de logging (padrão: WARNING)",
    )
    parser.add_argument(
        "--relatos",
        type=str,
        default=None,
        help="arquivo de relatos (padrão: data/textuais/sintomas_pacientes.txt)",
    )
    parser.add_argument(
        "--mapa",
        type=str,
        default=None,
        help="arquivo do mapa de conhecimento (padrão: data/textuais/mapa_conhecimento.json)",
    )
    return parser.parse_args()


def main() -> None:
    """Pipeline principal: carrega dados, extrai sintomas e sugere diagnósticos."""
    args = _parse_args()
    _configurar_logging(args.log)

    caminho_mapa = Path(args.mapa) if args.mapa else ARQUIVO_MAPA
    caminho_relatos = Path(args.relatos) if args.relatos else ARQUIVO_RELATOS

    mapa = carregar_mapa(caminho_mapa)
    relatos = carregar_relatos(caminho_relatos)

    n_doencas = sum(1 for k in mapa if k not in CHAVES_META)
    n_red_flags = len(mapa.get("red_flags", []))
    logger.info(
        "Mapa carregado: %d doenças, %d red flags", n_doencas, n_red_flags,
    )

    scores_maximos = pre_calcular_scores_maximos(mapa)

    resultados: list[ResultadoAnalise] = []
    for relato in relatos:
        resultados.append(analisar_relato(relato, mapa, scores_maximos))

    saida_texto = ""
    saida_json = ""

    if args.formato in ("texto", "ambos"):
        linhas = [
            f"Mapa de conhecimento: {n_doencas} doenças cardiovasculares, {n_red_flags} red flags",
            f"Relatos carregados: {len(relatos)}",
            "",
        ]
        for i, res in enumerate(resultados, 1):
            linhas.append(formatar_resultado(res, i))
        saida_texto = "\n".join(linhas)

    if args.formato in ("json", "ambos"):
        dados_json = {
            "meta": {
                "total_relatos": len(relatos),
                "total_doencas": n_doencas,
                "total_red_flags": n_red_flags,
            },
            "resultados": [r.to_json() for r in resultados],
        }
        saida_json = json.dumps(dados_json, ensure_ascii=False, indent=2)

    if args.saida:
        caminho_saida = Path(args.saida)
        if args.formato == "ambos":
            caminho_saida.with_suffix(".txt").write_text(
                saida_texto, encoding="utf-8",
            )
            caminho_saida.with_suffix(".json").write_text(
                saida_json, encoding="utf-8",
            )
        elif args.formato == "json":
            caminho_saida.write_text(saida_json, encoding="utf-8")
        else:
            caminho_saida.write_text(saida_texto, encoding="utf-8")
    else:
        if args.formato == "texto":
            print(saida_texto)
        elif args.formato == "json":
            print(saida_json)
        else:
            print(saida_texto)
            print("\n" + "=" * 72)
            print("SAÍDA JSON:")
            print("=" * 72)
            print(saida_json)
