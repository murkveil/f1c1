"""Wrapper de retrocompatibilidade para o pacote cardio_extrator.

Este módulo re-exporta todos os símbolos públicos do pacote
cardio_extrator para manter compatibilidade com código que importa
diretamente de extracao_sintomas. Imports diretos deste módulo emitem
DeprecationWarning — migre para cardio_extrator.

Uso:
    python -m cardio_extrator.cli [--formato texto|json|ambos] [--saida arquivo]
"""

from __future__ import annotations

import warnings

warnings.warn(
    "O módulo 'extracao_sintomas' está depreciado. "
    "Use 'cardio_extrator' diretamente. "
    "Exemplo: from cardio_extrator.extratores import extrair_sintomas",
    DeprecationWarning,
    stacklevel=2,
)

# modelos
from cardio_extrator.modelos import (  # noqa: E402
    AchadoClinico,
    AlertaRedFlag,
    ResultadoAnalise,
    ScoreDiagnostico,
)

# io
from cardio_extrator.io import (  # noqa: E402
    ARQUIVO_MAPA,
    ARQUIVO_RELATOS,
    CHAVES_META,
    DIRETORIO_DADOS,
    carregar_mapa,
    carregar_relatos,
)

# preprocessamento
from cardio_extrator.preprocessamento import normalizar  # noqa: E402

# negação
from cardio_extrator.negacao import _tokenizar, detectar_negacao  # noqa: E402

# extratores
from cardio_extrator.extratores import (  # noqa: E402
    achados_presentes,
    extrair_contexto,
    extrair_fatores_risco,
    extrair_medicacoes,
    extrair_qualificadores,
    extrair_sintomas,
    extrair_temporal,
    vincular_temporal_achados,
)

# inferência
from cardio_extrator.inferencia import (  # noqa: E402
    avaliar_condicao,
    avaliar_red_flags,
    pontuar_doenca,
    pontuar_doencas,
)

# formatação
from cardio_extrator.formatacao import formatar_resultado  # noqa: E402

# pipeline
from cardio_extrator.pipeline import analisar_relato  # noqa: E402

# cli
from cardio_extrator.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
