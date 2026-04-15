"""
Gera dataset sintético de pacientes cardiológicos para o projeto CardioIA.

O script produz dados clinicamente coerentes aplicando correlações entre
fatores de risco cardiovascular (idade, hipertensão, colesterol, diabetes,
tabagismo) e a presença de doença cardíaca.

Saída: data/numericos/dataset_cardiologico.csv

Variáveis geradas (18 colunas):

    Demográficas:
        id_paciente                  - Identificador único do paciente (int)
        idade                        - Idade em anos, entre 25 e 85 (int)
        sexo                         - Sexo biológico: M ou F (str)

    Sinais vitais:
        pressao_arterial_sistolica   - mmHg, entre 90 e 200 (int)
        pressao_arterial_diastolica  - mmHg, entre 55 e 120 (int)
        frequencia_cardiaca          - bpm, entre 45 e 120 (int)

    Exames laboratoriais:
        colesterol_total             - mg/dL, entre 120 e 350 (int)
        colesterol_hdl               - mg/dL, entre 20 e 100 (int)
        colesterol_ldl               - mg/dL, entre 50 e 250 (int)
        triglicerideos               - mg/dL, entre 50 e 500 (int)
        glicemia_jejum               - mg/dL, entre 65 e 300 (int)

    Indicadores clínicos:
        diabetes                     - Glicemia >= 126 mg/dL (bool)
        imc                          - Índice de massa corporal, entre 16.0 e 45.0 (float)

    Histórico e hábitos:
        tabagismo                    - Paciente fumante (bool)
        atividade_fisica             - Pratica atividade física regular (bool)
        historico_familiar_cardiaco  - Histórico familiar de doença cardíaca (bool)

    Sintomas e diagnóstico:
        tipo_dor_toracica            - angina_tipica, angina_atipica,
                                       dor_nao_cardiaca ou assintomatico (str)
        sintomas                     - Lista separada por ponto e vírgula (str)
        doenca_cardiaca              - Variável alvo / target (bool)

Correlações aplicadas:

    A idade eleva a pressão arterial sistólica em 0.6 mmHg por ano acima de 25.
    O tabagismo adiciona 15 mg/dL ao colesterol total basal.
    Mulheres recebem colesterol HDL basal de 55 mg/dL; homens, 45 mg/dL.
    A ausência de atividade física eleva o IMC basal de 26.5 para 29.0.
    O IMC eleva a glicemia de jejum em 2.5 mg/dL por ponto acima de 22.
    A atividade física reduz a frequência cardíaca basal de 75 para 65 bpm.

    A função calcular_risco() acumula incrementos de probabilidade para cada
    fator presente (idade, sexo, hipertensão, colesterol, HDL baixo, glicemia,
    tabagismo, IMC, sedentarismo, histórico familiar) e o resultado determina
    a presença de doença cardíaca. O teto de risco é 0.95.

    Pacientes com doença cardíaca recebem maior probabilidade de angina típica
    (45%) e mais sintomas (1-4). Pacientes sem doença recebem maior
    probabilidade de assintomático (55%) e menos sintomas (0-2).

Reprodutibilidade:

    O script utiliza seed fixa (SEED = 42) para garantir que execuções
    repetidas produzam o mesmo dataset.
"""

import csv
import random
from pathlib import Path

# seed fixa para reprodutibilidade entre execuções
SEED = 42

# 300 pacientes (3x o mínimo exigido pela atividade)
NUM_PACIENTES = 300

# sintomas cardiovasculares comuns utilizados na geração dos dados
SINTOMAS_POSSIVEIS = [
    "dor_toracica",
    "dispneia",
    "palpitacao",
    "fadiga",
    "tontura",
    "edema_membros_inferiores",
    "sincope",
]

# classificação clínica da dor torácica segundo padrão cardiológico
TIPOS_DOR_TORACICA = [
    "angina_tipica",
    "angina_atipica",
    "dor_nao_cardiaca",
    "assintomatico",
]


# cada tupla define (limiar, incremento) em ordem crescente de limiar
# a iteração retorna o incremento da faixa mais alta que o valor atinge
FAIXAS_RISCO = {
    "idade":                       [(40, 0.05), (50, 0.15), (65, 0.25)],
    "pressao_arterial_sistolica":  [(130, 0.08), (140, 0.15)],
    "colesterol_total":            [(200, 0.08), (240, 0.15)],
    "glicemia_jejum":              [(100, 0.05), (126, 0.12)],
    "imc":                         [(25, 0.05), (30, 0.10)],
}

# cada tupla define (campo, condição_para_incremento, incremento)
FATORES_BOOLEANOS = [
    ("sexo",                        lambda v: v == "M",  0.05),
    ("colesterol_hdl",              lambda v: v < 40,    0.10),
    ("tabagismo",                   lambda v: v,         0.15),
    ("atividade_fisica",            lambda v: not v,     0.05),
    ("historico_familiar_cardiaco", lambda v: v,         0.10),
]

RISCO_BASAL = 0.05
RISCO_TETO = 0.95


def _incremento_por_faixa(valor: float, faixas: list[tuple[float, float]]) -> float:
    """Retorna o incremento da faixa mais alta que o valor atinge."""
    incremento = 0.0
    for limiar, inc in faixas:
        if valor >= limiar:
            incremento = inc
    return incremento


def calcular_risco(paciente: dict) -> float:
    """Acumula incrementos de probabilidade para cada fator de risco presente.

    Cada fator contribui com um incremento fixo ao risco basal de 0.05.
    O risco total nunca ultrapassa 0.95. A função retorna a probabilidade
    final que o gerador utiliza para determinar a presença de doença cardíaca.
    """
    risco = RISCO_BASAL

    risco += sum(
        _incremento_por_faixa(paciente[campo], faixas)
        for campo, faixas in FAIXAS_RISCO.items()
    )

    risco += sum(
        incremento
        for campo, condicao, incremento in FATORES_BOOLEANOS
        if condicao(paciente[campo])
    )

    return min(risco, RISCO_TETO)


def _sortear_perfil_base() -> tuple[dict, dict]:
    """Sorteia variáveis demográficas e hábitos de vida do paciente.

    As prevalências refletem dados epidemiológicos brasileiros:
    tabagismo ~22% (IBGE/PNS), atividade física regular ~55%,
    histórico familiar cardíaco ~25%.

    Retorna dois dicts separados (demograficos, habitos) para preservar
    a ordem original das colunas no CSV ao fazer o merge.
    """
    demograficos = {
        "idade": random.randint(25, 85),
        "sexo": random.choice(["M", "F"]),
    }
    habitos = {
        "tabagismo": random.random() < 0.22,
        "atividade_fisica": random.random() < 0.55,
        "historico_familiar_cardiaco": random.random() < 0.25,
    }
    return demograficos, habitos


def _clamp(valor, minimo, maximo):
    """Restringe valor ao intervalo [mínimo, máximo]."""
    return max(minimo, min(maximo, valor))


def _derivar_sinais_e_exames(demograficos: dict, habitos: dict) -> dict:
    """Deriva sinais vitais e exames laboratoriais a partir do perfil base.

    Aplica correlacoes clinicas entre variaveis:
    idade -> pressao arterial, idade/tabagismo -> colesterol,
    atividade fisica -> IMC/frequencia cardiaca, IMC -> glicemia.
    """
    idade = demograficos["idade"]
    sexo = demograficos["sexo"]
    tabagismo = habitos["tabagismo"]
    atividade_fisica = habitos["atividade_fisica"]

    # a pressão sistólica sobe em média 0.6 mmHg por ano acima dos 25
    base_sistolica = 110 + (idade - 25) * 0.6
    pressao_sistolica = _clamp(int(random.gauss(base_sistolica, 15)), 90, 200)
    pressao_diastolica = _clamp(int(pressao_sistolica * random.gauss(0.62, 0.04)), 55, 120)

    # o colesterol total sobe em média 0.8 mg/dL por ano acima dos 25
    # o tabagismo adiciona 15 mg/dL ao valor basal
    base_colesterol = 160 + (idade - 25) * 0.8 + (15 if tabagismo else 0)
    colesterol_total = _clamp(int(random.gauss(base_colesterol, 30)), 120, 350)
    colesterol_hdl = _clamp(int(random.gauss(55 if sexo == "F" else 45, 12)), 20, 100)
    colesterol_ldl = _clamp(int(colesterol_total * random.gauss(0.6, 0.08)), 50, 250)
    triglicerideos = _clamp(int(random.gauss(150, 60)), 50, 500)

    # o IMC basal cai de 29.0 para 26.5 em pacientes fisicamente ativos
    # a glicemia sobe 2.5 mg/dL por ponto de IMC acima de 22
    imc = _clamp(round(random.gauss(26.5 if atividade_fisica else 29.0, 4.5), 1), 16.0, 45.0)
    base_glicemia = 85 + (imc - 22) * 2.5
    glicemia_jejum = _clamp(int(random.gauss(base_glicemia, 15)), 65, 300)

    # pacientes ativos apresentam frequência cardíaca basal menor (65 vs 75 bpm)
    base_fc = 65 if atividade_fisica else 75
    frequencia_cardiaca = _clamp(int(random.gauss(base_fc, 10)), 45, 120)

    return {
        "pressao_arterial_sistolica": pressao_sistolica,
        "pressao_arterial_diastolica": pressao_diastolica,
        "colesterol_total": colesterol_total,
        "colesterol_hdl": colesterol_hdl,
        "colesterol_ldl": colesterol_ldl,
        "triglicerideos": triglicerideos,
        "glicemia_jejum": glicemia_jejum,
        "diabetes": glicemia_jejum >= 126,
        "frequencia_cardiaca": frequencia_cardiaca,
        "imc": imc,
    }


# pesos de tipo de dor e faixa de sintomas por presença/ausência de doença
PERFIL_SINTOMAS = {
    True:  {"pesos_dor": [0.45, 0.30, 0.15, 0.10], "sintomas_range": (1, 4)},
    False: {"pesos_dor": [0.05, 0.10, 0.30, 0.55], "sintomas_range": (0, 2)},
}


def _determinar_diagnostico(paciente: dict) -> dict:
    """Determina doença cardíaca e sintomas com base no risco acumulado.

    Pacientes doentes recebem angina típica com 45% de chance e 1-4 sintomas.
    Pacientes saudáveis recebem assintomático com 55% de chance e 0-2 sintomas.
    """
    doenca_cardiaca = random.random() < calcular_risco(paciente)
    perfil = PERFIL_SINTOMAS[doenca_cardiaca]

    tipo_dor = random.choices(TIPOS_DOR_TORACICA, weights=perfil["pesos_dor"])[0]
    num_sintomas = random.randint(*perfil["sintomas_range"])
    sintomas = random.sample(SINTOMAS_POSSIVEIS, min(num_sintomas, len(SINTOMAS_POSSIVEIS)))

    return {
        "tipo_dor_toracica": tipo_dor,
        "sintomas": ";".join(sintomas) if sintomas else "nenhum",
        "doenca_cardiaca": doenca_cardiaca,
    }


def gerar_paciente(paciente_id: int) -> dict:
    """Orquestra a geração de um paciente em três etapas.

    1. Sorteia perfil demografico e habitos de vida
    2. Deriva sinais vitais e exames laboratoriais com correlações clínicas
    3. Determina doença cardíaca e sintomas pelo risco acumulado
    """
    demograficos, habitos = _sortear_perfil_base()
    exames = _derivar_sinais_e_exames(demograficos, habitos)

    # a ordem do merge preserva a ordem original das colunas no CSV:
    # demográficos -> exames -> hábitos
    paciente = {"id_paciente": paciente_id, **demograficos, **exames, **habitos}
    diagnostico = _determinar_diagnostico(paciente)

    return {**paciente, **diagnostico}


def main():
    """Gera o dataset e grava o CSV em data/numericos/dataset_cardiologico.csv.

    Exibe no terminal o total de pacientes e a distribuição entre doentes e
    saudáveis para validação rápida após a execução.
    """
    random.seed(SEED)

    diretorio_saida = Path(__file__).resolve().parent.parent / "data" / "numericos"
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    arquivo_saida = diretorio_saida / "dataset_cardiologico.csv"

    pacientes = [gerar_paciente(i + 1) for i in range(NUM_PACIENTES)]

    colunas = list(pacientes[0].keys())
    with open(arquivo_saida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(pacientes)

    print(f"Dataset gerado: {arquivo_saida}")
    print(f"Total de pacientes: {len(pacientes)}")

    total_doentes = sum(1 for p in pacientes if p["doenca_cardiaca"])
    print(f"Com doença cardíaca: {total_doentes} ({total_doentes/len(pacientes)*100:.1f}%)")
    print(f"Sem doença cardíaca: {len(pacientes)-total_doentes} ({(len(pacientes)-total_doentes)/len(pacientes)*100:.1f}%)")


if __name__ == "__main__":
    main()
