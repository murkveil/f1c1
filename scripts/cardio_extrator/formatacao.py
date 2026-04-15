"""Formatação de saída textual dos resultados de análise."""

from __future__ import annotations

from .modelos import ResultadoAnalise


def formatar_resultado(resultado: ResultadoAnalise, indice: int) -> str:
    """Formata a saída textual de um relato analisado.

    Args:
        resultado: Objeto ResultadoAnalise completo.
        indice: Número sequencial do relato.

    Returns:
        String formatada para exibição humana.
    """
    linhas: list[str] = []
    separador = "=" * 72

    linhas.append(separador)
    linhas.append(f"RELATO {indice}")
    linhas.append(separador)
    linhas.append(f"\n\"{resultado.relato_original}\"\n")

    if resultado.alertas:
        for alerta in resultado.alertas:
            linhas.append(f"  !!! [{alerta.prioridade}] {alerta.mensagem}")
        linhas.append("")

    presentes = [a for a in resultado.sintomas if a.presente]
    negados = [a for a in resultado.sintomas if not a.presente]

    linhas.append("SINTOMAS IDENTIFICADOS:")
    if presentes:
        for a in presentes:
            linhas.append(f"  + {a.sintoma} (expressão: \"{a.expressao_original}\")")
    else:
        linhas.append("  Nenhum sintoma identificado.")

    if negados:
        linhas.append("\nSINTOMAS NEGADOS:")
        for a in negados:
            linhas.append(
                f"  - {a.sintoma} (expressão: \"{a.expressao_original}\", "
                f"negador: \"{a.negador}\")"
            )

    if resultado.temporal:
        linhas.append("\nTEMPORALIDADE:")
        for attr, valor in resultado.temporal.items():
            linhas.append(f"  - {attr}: {valor}")

    if resultado.qualificadores:
        linhas.append("\nQUALIFICADORES SEMIOLÓGICOS:")
        for sintoma, quals in resultado.qualificadores.items():
            linhas.append(f"  {sintoma}:")
            for qual in quals:
                linhas.append(f"    - {qual}")

    if resultado.contexto:
        linhas.append("\nCONTEXTO CLÍNICO:")
        for ctx in resultado.contexto:
            linhas.append(f"  - {ctx}")

    if resultado.fatores_risco:
        linhas.append("\nFATORES DE RISCO:")
        for fator in resultado.fatores_risco:
            linhas.append(f"  - {fator}")

    if resultado.medicacoes:
        linhas.append("\nMEDICAÇÕES:")
        for classe, meds in resultado.medicacoes.items():
            linhas.append(f"  {classe}: {', '.join(meds)}")

    linhas.append("\nDIAGNÓSTICOS SUGERIDOS (por score normalizado):")
    if resultado.diagnosticos:
        for pos, diag in enumerate(resultado.diagnosticos, 1):
            linhas.append(
                f"\n  {pos}. {diag.nome_exibicao} "
                f"(bruto: {diag.score_bruto:.1f} | "
                f"normalizado: {diag.score_normalizado:.2f} | "
                f"confiança: {diag.confianca})"
            )
            for j in diag.justificativas:
                linhas.append(f"     - {j}")

            if pos == 1 and len(resultado.diagnosticos) > 1:
                segundo = resultado.diagnosticos[1]
                diff = diag.score_normalizado - segundo.score_normalizado
                if diff < 0.10:
                    linhas.append(
                        f"     * ATENÇÃO: score normalizado próximo de "
                        f"{segundo.nome_exibicao} (diff={diff:.2f}) — "
                        f"ambiguidade clínica requer investigação complementar"
                    )
    else:
        linhas.append("  Nenhum diagnóstico sugerido com base nos sintomas identificados.")

    linhas.append("")
    return "\n".join(linhas)
