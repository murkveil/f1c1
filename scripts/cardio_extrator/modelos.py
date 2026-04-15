"""Modelos de domínio do extrator cardiovascular."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class AchadoClinico:
    """Representa um sintoma detectado (ou negado) no relato."""

    sintoma: str
    presente: bool
    expressao_original: str
    negador: str | None = None
    posicao_texto: tuple[int, int] = (0, 0)
    temporal: dict[str, str] = field(default_factory=dict)


@dataclass
class ScoreDiagnostico:
    """Resultado de scoring para uma doença."""

    doenca: str
    nome_exibicao: str
    score_bruto: float
    score_normalizado: float
    confianca: str
    justificativas: list[str] = field(default_factory=list)


@dataclass
class AlertaRedFlag:
    """Alerta de red flag clínica detectada."""

    nome: str
    mensagem: str
    prioridade: str


@dataclass
class ResultadoAnalise:
    """Resultado completo da análise de um relato."""

    relato_original: str
    sintomas: list[AchadoClinico]
    qualificadores: dict[str, dict[str, bool]]
    contexto: dict[str, bool]
    temporal: dict[str, str]
    fatores_risco: dict[str, bool]
    medicacoes: dict[str, list[str]]
    diagnosticos: list[ScoreDiagnostico]
    alertas: list[AlertaRedFlag]

    def to_json(self) -> dict:
        """Converte o resultado para dicionário serializável em JSON.

        Returns:
            Dicionário com todos os campos da análise.
        """
        return {
            "relato_original": self.relato_original,
            "sintomas": [asdict(a) for a in self.sintomas],
            "qualificadores": self.qualificadores,
            "contexto": self.contexto,
            "temporal": self.temporal,
            "fatores_risco": self.fatores_risco,
            "medicacoes": self.medicacoes,
            "diagnosticos": [asdict(d) for d in self.diagnosticos],
            "alertas": [asdict(a) for a in self.alertas],
        }
