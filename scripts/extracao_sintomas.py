"""Extração de sintomas e sugestão de diagnóstico cardiovascular.

Lê relatos de pacientes (TXT), identifica sintomas com base no mapa de
conhecimento (JSON) e sugere diagnósticos usando motor de scoring declarativo
com detecção de negação, qualificadores semiológicos e normalização.

Uso:
    python scripts/extracao_sintomas.py [--formato texto|json|ambos] [--saida arquivo]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

logger = logging.getLogger("cardio_extrator")

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent / "data" / "textuais"
ARQUIVO_RELATOS = DIRETORIO_DADOS / "sintomas_pacientes.txt"
ARQUIVO_MAPA = DIRETORIO_DADOS / "mapa_conhecimento.json"

CHAVES_META = {"intersecoes", "ambiguidades_clinicas", "red_flags"}


# ---------------------------------------------------------------------------
# dataclasses
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# expressões de sintomas
# ---------------------------------------------------------------------------

EXPRESSOES_SINTOMAS: dict[str, list[str]] = {
    "dor_toracica": [
        r"dor\s+(?:\w+\s+){0,3}(?:peito|tórax|torax)",
        r"dor\s+torácica",
        r"dor\s+precordial",
        r"dor\s+retroesternal",
        r"aperto\s+(?:\w+\s+){0,4}(?:peito|tórax)",
        r"opressão\s+(?:\w+\s+){0,2}(?:peito|torácica|tórax)",
        r"pressão\s+(?:\w+\s+){0,2}peito",
        r"desconforto\s+(?:\w+\s+){0,2}(?:peito|torácico|precordial)",
        r"pontada\s+(?:\w+\s+){0,2}peito",
    ],
    "dispneia": [
        r"falta\s+de\s+ar",
        r"dificuldade\s+(?:para|de|em)\s+respirar",
        r"sufocamento",
        r"dispn[eé]ia",
        r"(?:não|sem)\s+consig\w+\s+respirar",
    ],
    "ortopneia": [
        r"falta\s+de\s+ar\s+(?:\w+\s+){0,2}(?:ao\s+)?deitar",
        r"(?:preciso|precisa|necessito|uso)\s+(?:\w+\s+){0,2}travesseiros?",
        r"ortopn[eé]ia",
    ],
    "dispneia_paroxistica_noturna": [
        r"(?:acordo|desperto|levanto)\s+(?:\w+\s+){0,5}(?:noite|madrugada)\s+(?:\w+\s+){0,4}(?:falta\s+de\s+ar|sufoc|sem\s+conseg\w+\s+respir)",
        r"(?:acordo|desperto)\s+(?:\w+\s+){0,4}(?:sufoc|falta\s+de\s+ar)",
        r"dispn[eé]ia\s+parox[ií]stica\s+noturna",
    ],
    "edema_membros_inferiores": [
        r"(?:pernas?|membros?\s+inferiores?|tornozelos?|pés)\s+(?:\w+\s+){0,3}(?:incha\w+|edema\w*)",
        r"(?:incha\w+|edema)\s+(?:\w+\s+){0,3}(?:pernas?|membros?\s+inferiores?|tornozelos?|pés)",
        r"edema\s+(?:de\s+)?(?:membros?\s+inferiores?|periférico|bilateral)",
    ],
    "fadiga": [
        r"cansaço\s+(?:constante|extremo|intenso|excessivo|(?:que\s+)?não\s+(?:passa|melhora|some))",
        r"fadiga",
        r"cansaço\s+desproporcional",
        r"exaust(?:ão|o)",
        r"fraqueza",
        r"astenia",
    ],
    "palpitacao": [
        r"palpita\w+",
        r"coração\s+(?:\w+\s+){0,2}(?:disparad|aceler|descompass)\w*",
        r"batimentos?\s+(?:irregulares?|acelerados?|descompassados?|rápidos?)",
        r"falhas?\s+(?:\w+\s+){0,2}batimentos?",
        r"taquicardia",
    ],
    "sincope": [
        r"(?:quase\s+)?desmai\w+",
        r"perda\s+(?:de\s+)?consci[eê]ncia",
        r"s[ií]ncope",
        r"apag(?:ão|ou|uei)",
    ],
    "tontura": [
        r"tontura",
        r"zonz(?:o|a|eira)",
        r"vertigem",
        r"cabeça\s+(?:leve|rodando)",
        r"escurecimento\s+(?:da\s+)?vis(?:ão|ta)",
    ],
    "cefaleia": [
        r"dor(?:es)?\s+de\s+cabeça",
        r"cefal[eé]ia",
        r"enxaqueca",
    ],
    "febre": [
        r"febre",
        r"febr(?:il|e)",
        r"temperatura\s+(?:elevada|alta)",
    ],
    "tosse_seca_noturna": [
        r"tosse\s+(?:seca\s+)?noturna",
        r"tosse\s+(?:à|a)\s+noite",
        r"tosse\s+seca",
    ],
    "nocturia": [
        r"urinando\s+(?:\w+\s+){0,2}(?:à|a)\s+noite",
        r"noct[úu]ria",
        r"levant\w+\s+(?:\w+\s+){0,3}(?:urinar|banheiro)\s+(?:\w+\s+){0,2}noite",
    ],
    "nausea": [
        r"n[áa]usea",
        r"enjô?o",
        r"vontade\s+de\s+vomitar",
    ],
    "sudorese": [
        r"suor\s+(?:frio|excessivo|abundante)",
        r"sudorese",
        r"transpiração\s+(?:fria|excessiva)",
    ],
    "epistaxe": [
        r"sangramento\s+nasal",
        r"sangue\s+(?:pelo|no)\s+nariz",
        r"epistaxe",
    ],
    "visao_turva": [
        r"vis(?:ão|ta)\s+(?:\w+\s+){0,2}(?:embara?çada|turva|borrada|emba[cç]ada)",
        r"enxerg\w+\s+(?:mal|emba[cç]ado)",
    ],
    "zumbido": [
        r"zumbido",
        r"zunido",
        r"chiado\s+(?:no|nos)\s+ouvido",
    ],
    "mialgia": [
        r"dor(?:es)?\s+muscular(?:es)?",
        r"mialgia",
        r"corpo\s+(?:todo\s+)?doendo",
    ],
    "distensao_abdominal": [
        r"barriga\s+(?:inchada|estufada|distendida)",
        r"disten(?:são|ção)\s+abdominal",
        r"saciedade\s+precoce",
    ],
    "confusao_mental": [
        r"confus(?:ão|o)\s+mental",
        r"desnorteado",
        r"sonolência\s+excessiva",
    ],
}

# ---------------------------------------------------------------------------
# qualificadores semiológicos
# ---------------------------------------------------------------------------

EXPRESSOES_QUALIFICADORES: dict[str, dict[str, list[str]]] = {
    "dor_toracica": {
        "tipo_opressiva": [
            r"aperto", r"opressão", r"pressão", r"peso",
            r"constri\w+", r"sufoc\w+",
        ],
        "tipo_pleuritica": [
            r"(?:dor\s+)?aguda", r"pontada", r"lancinante",
            r"piora\w*\s+(?:\w+\s+){0,3}respir",
        ],
        "irradiacao_mse": [
            r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}braço\s+esquerdo",
            r"(?:vai?\s+(?:para|pro)|irradi\w+\s+(?:para|pro)?)\s+(?:\w+\s+){0,3}(?:membro\s+superior\s+esquerdo|mse)",
        ],
        "irradiacao_mandibula": [
            r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}mandíbula",
        ],
        "irradiacao_trapezio": [
            r"(?:irradi|vai?\s+(?:para|pro))\w*\s+(?:\w+\s+){0,3}(?:trapézio|ombro)",
        ],
        "piora_esforco": [
            r"(?:piora|aparece|surge|durante)\s+(?:\w+\s+){0,3}(?:esforço|exercício|caminh|sub|corr|atividade)",
            r"(?:ao|quando)\s+(?:\w+\s+){0,2}(?:esforço|exercício|caminh|sub\w+\s+escada|corr)",
        ],
        "piora_respiracao": [
            r"piora\s+(?:\w+\s+){0,3}respir",
            r"piora\s+(?:\w+\s+){0,3}inspir",
        ],
        "piora_decubito": [
            r"piora\s+(?:\w+\s+){0,3}(?:deit|decúbito)",
            r"piora\s+(?:\w+\s+){0,3}(?:me\s+)?deit",
        ],
        "alivio_repouso": [
            r"(?:melhora|alívi\w*|some|passa)\s+(?:\w+\s+){0,3}(?:repos|descans|par)",
        ],
        "alivio_inclinado": [
            r"(?:melhora|alívi\w*)\s+(?:\w+\s+){0,4}(?:inclin|sent\w+\s+(?:e\s+)?inclin|sent\w+\s+para\s+frente)",
            r"(?:sento|inclino)\s+(?:\w+\s+){0,3}(?:para\s+)?frente",
        ],
    },
    "palpitacao": {
        "irregular": [r"irregular", r"descompass"],
        "inicio_subito": [
            r"(?:começ|inici)\w+\s+(?:\w+\s+){0,3}(?:de\s+repente|súbit|do\s+nada)",
            r"(?:de\s+repente|súbit|do\s+nada)\s+(?:\w+\s+){0,3}(?:começ|inici)",
        ],
        "precipitante_cafe": [r"caf[eé]", r"cafeína"],
        "precipitante_estresse": [r"estresse", r"ansiedade", r"nervos"],
    },
    "dispneia": {
        "aos_esforcos": [
            r"(?:ao|durante|com)\s+(?:\w+\s+){0,3}(?:esforço|exercício|caminh|sub|escada)",
        ],
        "ao_deitar": [
            r"ao\s+deitar",
            r"deit\w+\s+(?:\w+\s+){0,2}dormir",
        ],
    },
}

# ---------------------------------------------------------------------------
# contextos clínicos
# ---------------------------------------------------------------------------

EXPRESSOES_CONTEXTO: dict[str, list[str]] = {
    "prodomo_viral": [
        r"(?:depois|após)\s+(?:\w+\s+){0,4}(?:gripe|resfriado|virose|infecção)",
        r"pr[oó]dromo\s+viral",
    ],
    "historico_familiar_morte_subita": [
        r"(?:pai|mãe|irmão|irmã|parente)\s+(?:\w+\s+){0,6}(?:falec|morr)\w+\s+(?:\w+\s+){0,4}(?:súbit|jovem|cedo)",
        r"(?:pai|mãe|irmão|irmã|parente)\s+(?:\w+\s+){0,4}(?:doença\s+(?:no\s+)?coração|cardiopatia)",
        r"(?:história|histórico)\s+familiar\s+(?:\w+\s+){0,3}(?:morte\s+súbita|cardíac)",
    ],
    "esforco_fisico": [
        r"(?:ao|durante|quando)\s+(?:\w+\s+){0,2}(?:esforço|exercício|caminh|sub\w+\s+escada|corr\w+|atividade\s+física)",
    ],
}


# ---------------------------------------------------------------------------
# motor de negação (E1)
# ---------------------------------------------------------------------------

NEGADORES = [
    r"\bnão\b", r"\bnego\b", r"\bnega\b", r"\bsem\b",
    r"\bnunca\b", r"\bnenhum[a]?\b", r"\bausência\s+de\b",
]

RESTAURADORES = [
    r"\bmas\b", r"\bporém\b", r"\bentretanto\b", r"\bcontudo\b",
    r"\btodavia\b", r"\bno\s+entanto\b", r"\bagora\s+sim\b",
    r"\brecentemente\b",
]

DUPLA_NEGACAO = [
    r"\bnão\s+posso\s+negar\b",
    r"\bnão\s+nego\b",
    r"\bimpossível\s+negar\b",
]

JANELA_NEGACAO = 5

# delimitadores que encerram o escopo de negação (conjunções, pontuação)
DELIMITADORES_ESCOPO = [
    r"\be\b", r"\bou\b", r",", r"\.", r";", r":", r"\bque\s+(?!não)",
]


def _tokenizar(texto: str) -> list[tuple[str, int, int]]:
    """Retorna lista de (token, posição_início, posição_fim)."""
    return [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", texto)]


def _encontrar_negador(
    texto_norm: str,
    pos_inicio_match: int,
    tokens: list[tuple[str, int, int]],
) -> tuple[str | None, int]:
    """Verifica se há negador dentro da janela antes da posição do match.

    Args:
        texto_norm: Texto normalizado (minúsculo).
        pos_inicio_match: Posição de início do match do sintoma.
        tokens: Lista de tokens do texto com posições.

    Returns:
        Tupla (negador_encontrado, posição_do_negador). None e -1 se não há.
    """
    idx_match = None
    for i, (_, inicio, _) in enumerate(tokens):
        if inicio >= pos_inicio_match:
            idx_match = i
            break
    if idx_match is None:
        return None, -1

    janela_inicio = max(0, idx_match - JANELA_NEGACAO)
    janela_texto = texto_norm[:pos_inicio_match]

    for padrao in NEGADORES:
        for m in re.finditer(padrao, janela_texto):
            idx_negador = None
            for i, (_, inicio, _) in enumerate(tokens):
                if inicio >= m.start():
                    idx_negador = i
                    break
            if idx_negador is not None and idx_negador >= janela_inicio:
                return m.group(), m.start()

    return None, -1


def _verificar_restaurador(
    texto_norm: str,
    pos_negador: int,
    pos_match: int,
) -> bool:
    """Verifica se há restaurador entre o negador e o match do sintoma.

    Args:
        texto_norm: Texto normalizado.
        pos_negador: Posição do negador no texto.
        pos_match: Posição do match do sintoma.

    Returns:
        True se há restaurador (negação é revertida).
    """
    trecho = texto_norm[pos_negador:pos_match]
    for padrao in RESTAURADORES:
        if re.search(padrao, trecho):
            return True
    return False


def _verificar_delimitador_escopo(
    texto_norm: str,
    pos_negador: int,
    pos_match: int,
) -> bool:
    """Verifica se há delimitador de escopo entre o negador e o match.

    Conjunções coordenativas (e, ou), vírgulas e pontos encerram o
    escopo de negação, impedindo que um negador numa oração afete
    sintomas de outra oração.

    Args:
        texto_norm: Texto normalizado.
        pos_negador: Posição do negador no texto.
        pos_match: Posição do match do sintoma.

    Returns:
        True se há delimitador (negação não se aplica ao match).
    """
    trecho = texto_norm[pos_negador:pos_match]
    for padrao in DELIMITADORES_ESCOPO:
        if re.search(padrao, trecho):
            return True
    return False


def _verificar_dupla_negacao(texto_norm: str, pos_match: int) -> bool:
    """Verifica se o contexto antes do match contém dupla negação (= afirmação).

    Args:
        texto_norm: Texto normalizado.
        pos_match: Posição do match do sintoma.

    Returns:
        True se há dupla negação (o sintoma é afirmado).
    """
    janela = texto_norm[max(0, pos_match - 40):pos_match]
    for padrao in DUPLA_NEGACAO:
        if re.search(padrao, janela):
            return True
    return False


def detectar_negacao(
    texto_norm: str,
    pos_match: int,
    tokens: list[tuple[str, int, int]],
) -> tuple[bool, str | None]:
    """Determina se um achado na posição dada está negado.

    Args:
        texto_norm: Texto normalizado.
        pos_match: Posição de início do match.
        tokens: Tokens do texto com posições.

    Returns:
        Tupla (negado, negador). negado=True se o achado está negado.
    """
    if _verificar_dupla_negacao(texto_norm, pos_match):
        return False, None

    negador, pos_negador = _encontrar_negador(texto_norm, pos_match, tokens)
    if negador is None:
        return False, None

    if _verificar_delimitador_escopo(texto_norm, pos_negador, pos_match):
        return False, None

    if _verificar_restaurador(texto_norm, pos_negador, pos_match):
        return False, None

    return True, negador


# ---------------------------------------------------------------------------
# pré-processamento de texto (E5)
# ---------------------------------------------------------------------------

CONTRACOES: list[tuple[str, str]] = [
    (r"\bpro\b", "para o"), (r"\bpra\b", "para a"),
    (r"\bpros\b", "para os"), (r"\bpras\b", "para as"),
    (r"\btô\b", "estou"), (r"\btá\b", "está"),
    (r"\bnum\b", "em um"), (r"\bnuma\b", "em uma"),
    (r"\bnuns\b", "em uns"), (r"\bnumas\b", "em umas"),
    (r"\bduma\b", "de uma"), (r"\bdum\b", "de um"),
    (r"\bpelo\b", "por o"), (r"\bpela\b", "por a"),
    (r"\bnele\b", "em ele"), (r"\bnela\b", "em ela"),
    (r"\bdele\b", "de ele"), (r"\bdela\b", "de ela"),
    (r"\bcê\b", "você"), (r"\bocê\b", "você"),
]

CORRECOES_ORTOGRAFICAS: dict[str, str] = {
    "dispineia": "dispneia", "dispinéia": "dispneia",
    "palpitassão": "palpitação", "palpitasão": "palpitação",
    "inchazo": "inchaço", "inchasço": "inchaço",
    "torax": "tórax", "toráx": "tórax",
    "exame": "exame",
    "cançaso": "cansaço", "cansaso": "cansaço",
    "cabeça": "cabeça",
    "nausea": "náusea",
    "colestero": "colesterol",
    "diabetis": "diabetes", "diabete": "diabetes",
    "pressao": "pressão",
    "coraçao": "coração", "coracao": "coração",
    "desmaiei": "desmaiei",
}


def normalizar(texto: str) -> str:
    """Normaliza texto: minúsculo, contrações expandidas, correções ortográficas.

    Aplica pré-processamento em 3 etapas:
    1. Conversão para minúsculo e simplificação de espaços
    2. Expansão de contrações coloquiais (pro→para o, tô→estou)
    3. Correção de erros ortográficos comuns em relatos de pacientes

    Args:
        texto: Texto original do relato.

    Returns:
        Texto normalizado pronto para extração por regex.
    """
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto).strip()

    for padrao, subst in CONTRACOES:
        texto = re.sub(padrao, subst, texto)

    for errado, correto in CORRECOES_ORTOGRAFICAS.items():
        texto = re.sub(r"\b" + re.escape(errado) + r"\b", correto, texto)

    return texto


# ---------------------------------------------------------------------------
# extração de sintomas com negação
# ---------------------------------------------------------------------------

def extrair_sintomas(texto: str) -> list[AchadoClinico]:
    """Identifica sintomas no texto, respeitando contexto de negação.

    Args:
        texto: Relato do paciente (texto livre).

    Returns:
        Lista de AchadoClinico com flag de presença/negação.
    """
    texto_norm = normalizar(texto)
    tokens = _tokenizar(texto_norm)
    achados: list[AchadoClinico] = []
    sintomas_vistos: set[str] = set()

    for sintoma, padroes in EXPRESSOES_SINTOMAS.items():
        for padrao in padroes:
            for match in re.finditer(padrao, texto_norm):
                if sintoma in sintomas_vistos:
                    break
                negado, negador = detectar_negacao(
                    texto_norm, match.start(), tokens,
                )
                achados.append(AchadoClinico(
                    sintoma=sintoma,
                    presente=not negado,
                    expressao_original=match.group(),
                    negador=negador,
                    posicao_texto=(match.start(), match.end()),
                ))
                sintomas_vistos.add(sintoma)
                logger.info(
                    "Sintoma '%s' detectado e %s (expressão: '%s')",
                    sintoma,
                    "confirmado" if not negado else f"NEGADO ({negador})",
                    match.group(),
                )
                break

    return achados


def achados_presentes(achados: list[AchadoClinico]) -> set[str]:
    """Retorna conjunto de sintomas confirmados (não negados).

    Args:
        achados: Lista de achados clínicos extraídos.

    Returns:
        Conjunto de nomes canônicos dos sintomas presentes.
    """
    return {a.sintoma for a in achados if a.presente}


# ---------------------------------------------------------------------------
# extração de qualificadores
# ---------------------------------------------------------------------------

def extrair_qualificadores(
    texto: str,
    sintomas_presentes: set[str],
) -> dict[str, dict[str, bool]]:
    """Extrai qualificadores semiológicos dos sintomas presentes.

    Args:
        texto: Relato do paciente.
        sintomas_presentes: Conjunto de sintomas confirmados.

    Returns:
        Dicionário {sintoma: {qualificador: True}}.
    """
    texto_norm = normalizar(texto)
    qualificadores: dict[str, dict[str, bool]] = {}

    for sintoma in sintomas_presentes:
        if sintoma not in EXPRESSOES_QUALIFICADORES:
            continue

        quals_sintoma: dict[str, bool] = {}
        for nome_qual, padroes in EXPRESSOES_QUALIFICADORES[sintoma].items():
            for padrao in padroes:
                if re.search(padrao, texto_norm):
                    quals_sintoma[nome_qual] = True
                    break

        if quals_sintoma:
            qualificadores[sintoma] = quals_sintoma

    return qualificadores


# ---------------------------------------------------------------------------
# extração de contexto
# ---------------------------------------------------------------------------

def extrair_contexto(texto: str) -> dict[str, bool]:
    """Extrai contextos clínicos relevantes do relato.

    Args:
        texto: Relato do paciente.

    Returns:
        Dicionário {nome_contexto: True}.
    """
    texto_norm = normalizar(texto)
    contexto: dict[str, bool] = {}

    for nome, padroes in EXPRESSOES_CONTEXTO.items():
        for padrao in padroes:
            if re.search(padrao, texto_norm):
                contexto[nome] = True
                break

    return contexto


# ---------------------------------------------------------------------------
# extração de fatores de risco e medicações (E6)
# ---------------------------------------------------------------------------

EXPRESSOES_FATORES_RISCO: dict[str, list[str]] = {
    "tabagismo": [
        r"(?:sou\s+)?fum(?:o|ante|ava|ei)",
        r"tabagis\w+",
        r"cigarr\w+",
        r"fumo\s+(?:\w+\s+){0,2}(?:maço|carteira)",
    ],
    "diabetes": [
        r"diabet\w+",
        r"açúcar\s+(?:no\s+sangue\s+)?alto",
        r"glicemia\s+(?:alta|elevada)",
        r"insulina",
    ],
    "hipertensao": [
        r"(?:pressão|pa)\s+(?:\w+\s+)?alta",
        r"hipertens\w+",
        r"pressão\s+(?:arterial\s+)?elevada",
    ],
    "dislipidemia": [
        r"colesterol\s+(?:\w+\s+)?(?:alto|elevado)",
        r"dislipidemia",
        r"triglicér\w+\s+(?:\w+\s+)?alt\w+",
    ],
    "obesidade": [
        r"obes\w+",
        r"sobrepeso",
        r"(?:muito\s+)?acima\s+do\s+peso",
    ],
    "sedentarismo": [
        r"sedentár\w+",
        r"não\s+(?:faço|pratico)\s+(?:\w+\s+)?exercício",
        r"não\s+(?:faço|pratico)\s+(?:\w+\s+)?atividade\s+física",
        r"vida\s+(?:\w+\s+)?sedentária",
    ],
}

EXPRESSOES_MEDICACOES: dict[str, list[str]] = {
    "anti_hipertensivo": [
        r"losartana", r"enalapril", r"amlodipina", r"atenolol",
        r"captopril", r"valsartana", r"nifedipina", r"metoprolol",
        r"propranolol", r"carvedilol", r"hidralazina",
        r"remédio\s+(?:\w+\s+){0,2}pressão",
    ],
    "anticoagulante": [
        r"varfarina", r"rivaroxabana", r"apixabana",
        r"dabigatrana", r"edoxabana", r"heparina",
        r"marevan", r"xarelto", r"eliquis",
    ],
    "antiplaquetario": [
        r"\baas\b", r"aspirina", r"clopidogrel",
        r"ticagrelor", r"prasugrel",
    ],
    "estatina": [
        r"sinvastatina", r"atorvastatina", r"rosuvastatina",
        r"pravastatina", r"fluvastatina",
        r"remédio\s+(?:\w+\s+){0,2}colesterol",
    ],
    "diuretico": [
        r"furosemida", r"hidroclorotiazida", r"espironolactona",
        r"indapamida", r"clortalidona",
        r"lasix",
    ],
    "antidiabetico": [
        r"metformina", r"glibenclamida", r"gliclazida",
        r"insulina", r"glargina", r"dapagliflozina",
        r"empagliflozina", r"sitagliptina",
        r"remédio\s+(?:\w+\s+){0,2}(?:diabetes|açúcar|glicemia)",
    ],
    "antiarritmico": [
        r"amiodarona", r"sotalol", r"propafenona",
        r"flecainida", r"digoxina",
    ],
}


def extrair_fatores_risco(texto: str) -> dict[str, bool]:
    """Extrai fatores de risco cardiovascular mencionados no relato.

    Args:
        texto: Relato do paciente.

    Returns:
        Dicionário {fator_de_risco: True}.
    """
    texto_norm = normalizar(texto)
    fatores: dict[str, bool] = {}

    for fator, padroes in EXPRESSOES_FATORES_RISCO.items():
        for padrao in padroes:
            if re.search(padrao, texto_norm):
                fatores[fator] = True
                logger.debug("Fator de risco '%s' detectado no texto", fator)
                break

    return fatores


def extrair_medicacoes(texto: str) -> dict[str, list[str]]:
    """Extrai medicações mencionadas no relato, agrupadas por classe.

    Args:
        texto: Relato do paciente.

    Returns:
        Dicionário {classe_medicacao: [medicamentos_encontrados]}.
    """
    texto_norm = normalizar(texto)
    medicacoes: dict[str, list[str]] = {}

    for classe, padroes in EXPRESSOES_MEDICACOES.items():
        encontrados: list[str] = []
        for padrao in padroes:
            match = re.search(padrao, texto_norm)
            if match:
                encontrados.append(match.group())
        if encontrados:
            medicacoes[classe] = encontrados
            logger.debug(
                "Medicação classe '%s' detectada: %s", classe, encontrados,
            )

    return medicacoes


# ---------------------------------------------------------------------------
# extração temporal (E2)
# ---------------------------------------------------------------------------

PADROES_TEMPORAIS: dict[str, list[str]] = {
    "inicio": [
        r"há\s+((?:\w+\s+)?(?:dias?|semanas?|meses?|anos?|horas?))",
        r"há\s+(\d+\s+(?:dias?|semanas?|meses?|anos?|horas?))",
        r"desde\s+(ontem|anteontem|semana\s+passada|mês\s+passado)",
        r"(?:começou|iniciou|apareceu)\s+(?:há|faz)\s+((?:\w+\s+)?(?:dias?|semanas?|meses?|horas?))",
        r"(?:começou|iniciou|apareceu)\s+(?:\w+\s+){0,3}(ontem|anteontem|hoje|semana\s+passada)",
    ],
    "duracao": [
        r"(?:dura|duram)\s+(?:\w+\s+){0,2}(\d+\s+(?:minutos?|horas?|segundos?))",
        r"(?:dura|duram)\s+(\w+\s+(?:minutos?|horas?))",
        r"(persistente|contínu[oa]|o\s+dia\s+todo|o\s+tempo\s+todo)",
        r"(?:por|durante)\s+(\d+\s+(?:minutos?|horas?|dias?))",
    ],
    "frequencia": [
        r"(toda\s+(?:noite|manhã|dia|semana))",
        r"(\d+\s*(?:x|vezes?)\s+(?:por|ao|na|no)\s+(?:dia|semana|mês))",
        r"((?:esporádic|ocasional|frequent|diári|intermitente)\w*)",
    ],
    "progressao": [
        r"((?:vem\s+)?(?:piorando|agravando|intensificando))",
        r"((?:vem\s+)?(?:melhorando|aliviando|diminuindo))",
        r"(estável|estacion\w+|sem\s+(?:mudança|alteração))",
        r"((?:cada\s+vez\s+)?(?:pior|mais\s+(?:forte|intenso|frequent)))",
    ],
}


def extrair_temporal(texto: str) -> dict[str, str]:
    """Extrai atributos temporais do relato como um todo.

    Busca padrões de início, duração, frequência e progressão
    no texto do relato.

    Args:
        texto: Relato do paciente.

    Returns:
        Dicionário {atributo_temporal: valor_extraído}.
    """
    texto_norm = normalizar(texto)
    temporal: dict[str, str] = {}

    for atributo, padroes in PADROES_TEMPORAIS.items():
        for padrao in padroes:
            match = re.search(padrao, texto_norm)
            if match:
                temporal[atributo] = match.group(1) if match.lastindex else match.group()
                break

    return temporal


def vincular_temporal_achados(
    achados: list[AchadoClinico],
    temporal: dict[str, str],
) -> None:
    """Vincula informações temporais aos achados clínicos.

    Atribui o temporal global ao primeiro achado presente (sintoma principal),
    pois nos relatos curtos a temporalidade geralmente se refere ao quadro geral.

    Args:
        achados: Lista de achados clínicos (modificada in-place).
        temporal: Atributos temporais extraídos.
    """
    if not temporal:
        return

    for achado in achados:
        if achado.presente:
            achado.temporal = temporal
            break


# ---------------------------------------------------------------------------
# red flags (E8)
# ---------------------------------------------------------------------------

def avaliar_red_flags(
    mapa: dict,
    sintomas_presentes: set[str],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
) -> list[AlertaRedFlag]:
    """Avalia combinações de achados que indicam emergência cardiovascular.

    Utiliza o avaliador de condições declarativas para verificar cada
    red flag definida no mapa de conhecimento.

    Args:
        mapa: Mapa de conhecimento completo (contém seção red_flags).
        sintomas_presentes: Sintomas confirmados.
        qualificadores: Qualificadores semiológicos.
        contexto: Contextos clínicos.
        fatores_risco: Fatores de risco.

    Returns:
        Lista de AlertaRedFlag para as condições satisfeitas.
    """
    alertas: list[AlertaRedFlag] = []

    for red_flag in mapa.get("red_flags", []):
        if avaliar_condicao(
            red_flag["condicao"],
            sintomas_presentes, qualificadores, contexto, fatores_risco,
        ):
            alertas.append(AlertaRedFlag(
                nome=red_flag["nome"],
                mensagem=red_flag["mensagem"],
                prioridade=red_flag["prioridade"],
            ))

    return alertas


# ---------------------------------------------------------------------------
# avaliador de condições declarativas (E3)
# ---------------------------------------------------------------------------

def avaliar_condicao(
    condicao: dict,
    sintomas_presentes: set[str],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
) -> bool:
    """Avalia uma condição declarativa contra o estado clínico atual.

    Suporta os seguintes tipos de condição:
    - {"sintoma": "nome"} — sintoma presente
    - {"qualificador": "sintoma.qualificador"} — qualificador presente
    - {"contexto": "nome"} — contexto clínico presente
    - {"fator_risco": "nome"} — fator de risco presente
    - {"operador": "AND", "criterios": [...]} — todos verdadeiros
    - {"operador": "OR", "criterios": [...]} — ao menos um verdadeiro
    - {"operador": "COUNT_GE", "criterios": [...], "limiar": N} — ao menos N verdadeiros

    Args:
        condicao: Dicionário descrevendo a condição.
        sintomas_presentes: Sintomas confirmados.
        qualificadores: Qualificadores extraídos.
        contexto: Contextos clínicos extraídos.
        fatores_risco: Fatores de risco extraídos.

    Returns:
        True se a condição é satisfeita.
    """
    if "sintoma" in condicao:
        return condicao["sintoma"] in sintomas_presentes

    if "qualificador" in condicao:
        partes = condicao["qualificador"].split(".", 1)
        if len(partes) != 2:
            return False
        sintoma, qual = partes
        return qualificadores.get(sintoma, {}).get(qual, False)

    if "contexto" in condicao:
        return contexto.get(condicao["contexto"], False)

    if "fator_risco" in condicao:
        return fatores_risco.get(condicao["fator_risco"], False)

    operador = condicao.get("operador")
    criterios = condicao.get("criterios", [])

    if operador == "AND":
        return all(
            avaliar_condicao(c, sintomas_presentes, qualificadores, contexto, fatores_risco)
            for c in criterios
        )

    if operador == "OR":
        return any(
            avaliar_condicao(c, sintomas_presentes, qualificadores, contexto, fatores_risco)
            for c in criterios
        )

    if operador == "COUNT_GE":
        limiar = condicao.get("limiar", 1)
        contagem = sum(
            1 for c in criterios
            if avaliar_condicao(c, sintomas_presentes, qualificadores, contexto, fatores_risco)
        )
        return contagem >= limiar

    return False


# ---------------------------------------------------------------------------
# motor de scoring declarativo (E3 + E4)
# ---------------------------------------------------------------------------

def _calcular_score_maximo(scoring: dict) -> float:
    """Calcula o score máximo possível de uma doença (para normalização).

    Args:
        scoring: Seção 'scoring' do mapa de conhecimento da doença.

    Returns:
        Soma de todos os pesos base + todos os bônus possíveis.
    """
    max_sintomas = sum(
        cfg["peso_base"] for cfg in scoring["sintomas"].values()
    )
    max_bonus = sum(
        r["bonus"] for r in scoring.get("regras_bonificacao", [])
    )
    max_fatores = sum(scoring.get("fatores_risco", {}).values())
    return max_sintomas + max_bonus + max_fatores


def pontuar_doenca(
    doenca_config: dict,
    sintomas_presentes: set[str],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
) -> tuple[float, list[str]]:
    """Avalia UMA doença contra os achados clínicos. Sem if/elif por doença.

    Args:
        doenca_config: Configuração completa da doença no mapa.
        sintomas_presentes: Sintomas confirmados do relato.
        qualificadores: Qualificadores semiológicos extraídos.
        contexto: Contextos clínicos extraídos.
        fatores_risco: Fatores de risco extraídos.

    Returns:
        Tupla (score_bruto, justificativas).
    """
    scoring = doenca_config.get("scoring", {})
    score = 0.0
    justificativas: list[str] = []

    # 1. pesos base dos sintomas presentes
    for sintoma, cfg in scoring.get("sintomas", {}).items():
        if sintoma in sintomas_presentes:
            peso = cfg["peso_base"]
            score += peso
            justificativas.append(f"sintoma: {sintoma} (peso {peso:.1f})")

    # 2. regras de bonificação
    for regra in scoring.get("regras_bonificacao", []):
        if avaliar_condicao(
            regra["condicao"],
            sintomas_presentes, qualificadores, contexto, fatores_risco,
        ):
            score += regra["bonus"]
            justificativas.append(
                f"bônus +{regra['bonus']:.1f}: {regra['justificativa']}"
            )

    # 3. regras de exclusão/penalidade
    for regra in scoring.get("regras_exclusao", []):
        if avaliar_condicao(
            regra["condicao"],
            sintomas_presentes, qualificadores, contexto, fatores_risco,
        ):
            score += regra["penalidade"]
            justificativas.append(
                f"penalidade {regra['penalidade']:.1f}: {regra['justificativa']}"
            )

    # 4. fatores de risco
    for fator, peso in scoring.get("fatores_risco", {}).items():
        if fatores_risco.get(fator, False):
            score += peso
            justificativas.append(f"fator de risco: {fator} (+{peso:.1f})")

    return score, justificativas


def pontuar_doencas(
    achados: list[AchadoClinico],
    qualificadores: dict[str, dict[str, bool]],
    contexto: dict[str, bool],
    fatores_risco: dict[str, bool],
    mapa: dict,
) -> list[ScoreDiagnostico]:
    """Calcula pontuação normalizada para todas as doenças do mapa.

    Args:
        achados: Achados clínicos extraídos.
        qualificadores: Qualificadores semiológicos.
        contexto: Contextos clínicos.
        fatores_risco: Fatores de risco.
        mapa: Mapa de conhecimento completo.

    Returns:
        Lista de ScoreDiagnostico ordenada por score normalizado (desc).
    """
    presentes = achados_presentes(achados)
    resultados: list[ScoreDiagnostico] = []

    for chave, config in mapa.items():
        if chave in CHAVES_META:
            continue

        score_bruto, justificativas = pontuar_doenca(
            config, presentes, qualificadores, contexto, fatores_risco,
        )

        if score_bruto <= 0:
            continue

        score_max = _calcular_score_maximo(config.get("scoring", {}))
        score_norm = score_bruto / score_max if score_max > 0 else 0.0
        score_norm = min(score_norm, 1.0)

        if score_norm < 0.3:
            confianca = "baixa"
        elif score_norm < 0.6:
            confianca = "moderada"
        else:
            confianca = "alta"

        resultados.append(ScoreDiagnostico(
            doenca=chave,
            nome_exibicao=config.get("nome_exibicao", chave),
            score_bruto=score_bruto,
            score_normalizado=score_norm,
            confianca=confianca,
            justificativas=justificativas,
        ))

    resultados.sort(key=lambda x: x.score_normalizado, reverse=True)

    if len(resultados) >= 2:
        diff = resultados[0].score_normalizado - resultados[1].score_normalizado
        if diff < 0.10:
            logger.warning(
                "Ambiguidade: scores de %s (%.2f) e %s (%.2f) diferem em < 0.10",
                resultados[0].nome_exibicao, resultados[0].score_normalizado,
                resultados[1].nome_exibicao, resultados[1].score_normalizado,
            )

    return resultados


# ---------------------------------------------------------------------------
# formatação de saída
# ---------------------------------------------------------------------------

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

    # red flags (exibidas no topo por prioridade)
    if resultado.alertas:
        for alerta in resultado.alertas:
            linhas.append(f"  !!! [{alerta.prioridade}] {alerta.mensagem}")
        linhas.append("")

    # achados clínicos com status de negação
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

    # temporalidade
    if resultado.temporal:
        linhas.append("\nTEMPORALIDADE:")
        for attr, valor in resultado.temporal.items():
            linhas.append(f"  - {attr}: {valor}")

    # qualificadores
    if resultado.qualificadores:
        linhas.append("\nQUALIFICADORES SEMIOLÓGICOS:")
        for sintoma, quals in resultado.qualificadores.items():
            linhas.append(f"  {sintoma}:")
            for qual in quals:
                linhas.append(f"    - {qual}")

    # contexto clínico
    if resultado.contexto:
        linhas.append("\nCONTEXTO CLÍNICO:")
        for ctx in resultado.contexto:
            linhas.append(f"  - {ctx}")

    # fatores de risco
    if resultado.fatores_risco:
        linhas.append("\nFATORES DE RISCO:")
        for fator in resultado.fatores_risco:
            linhas.append(f"  - {fator}")

    # medicações
    if resultado.medicacoes:
        linhas.append("\nMEDICAÇÕES:")
        for classe, meds in resultado.medicacoes.items():
            linhas.append(f"  {classe}: {', '.join(meds)}")

    # diagnósticos sugeridos
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

            # alerta de ambiguidade
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


# ---------------------------------------------------------------------------
# carregamento de dados
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def analisar_relato(relato: str, mapa: dict) -> ResultadoAnalise:
    """Executa o pipeline completo de análise para um relato.

    Args:
        relato: Texto do relato do paciente.
        mapa: Mapa de conhecimento carregado.

    Returns:
        ResultadoAnalise com todos os achados e diagnósticos.
    """
    logger.info("Iniciando análise do relato: '%s...'", relato[:50])

    achados = extrair_sintomas(relato)
    presentes = achados_presentes(achados)
    qualificadores = extrair_qualificadores(relato, presentes)
    contexto = extrair_contexto(relato)
    temporal = extrair_temporal(relato)
    vincular_temporal_achados(achados, temporal)
    fatores_risco = extrair_fatores_risco(relato)
    medicacoes = extrair_medicacoes(relato)

    diagnosticos = pontuar_doencas(
        achados, qualificadores, contexto, fatores_risco, mapa,
    )

    alertas = avaliar_red_flags(
        mapa, presentes, qualificadores, contexto, fatores_risco,
    )

    logger.info(
        "Análise concluída: %d sintomas, %d diagnósticos, %d alertas",
        len(presentes), len(diagnosticos), len(alertas),
    )

    return ResultadoAnalise(
        relato_original=relato,
        sintomas=achados,
        qualificadores=qualificadores,
        contexto=contexto,
        temporal=temporal,
        fatores_risco=fatores_risco,
        medicacoes=medicacoes,
        diagnosticos=diagnosticos,
        alertas=alertas,
    )


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

    resultados: list[ResultadoAnalise] = []
    for relato in relatos:
        resultados.append(analisar_relato(relato, mapa))

    # gerar saída
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

    # escrever saída
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


if __name__ == "__main__":
    main()
