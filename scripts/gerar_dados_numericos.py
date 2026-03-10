"""
Gera dataset sintetico de pacientes cardiologicos para o projeto CardioIA.

O script produz dados clinicamente coerentes aplicando correlacoes entre
fatores de risco cardiovascular (idade, hipertensao, colesterol, diabetes,
tabagismo) e a presenca de doenca cardiaca.

Saida: data/numericos/dataset_cardiologico.csv

Variaveis geradas (18 colunas):

    Demograficas:
        id_paciente                  - Identificador unico do paciente (int)
        idade                        - Idade em anos, entre 25 e 85 (int)
        sexo                         - Sexo biologico: M ou F (str)

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

    Indicadores clinicos:
        diabetes                     - Glicemia >= 126 mg/dL (bool)
        imc                          - Indice de massa corporal, entre 16.0 e 45.0 (float)

    Historico e habitos:
        tabagismo                    - Paciente fumante (bool)
        atividade_fisica             - Pratica atividade fisica regular (bool)
        historico_familiar_cardiaco  - Historico familiar de doenca cardiaca (bool)

    Sintomas e diagnostico:
        tipo_dor_toracica            - angina_tipica, angina_atipica,
                                       dor_nao_cardiaca ou assintomatico (str)
        sintomas                     - Lista separada por ponto e virgula (str)
        doenca_cardiaca              - Variavel alvo / target (bool)

Correlacoes aplicadas:

    A idade eleva a pressao arterial sistolica em 0.6 mmHg por ano acima de 25.
    O tabagismo adiciona 15 mg/dL ao colesterol total basal.
    Mulheres recebem colesterol HDL basal de 55 mg/dL; homens, 45 mg/dL.
    A ausencia de atividade fisica eleva o IMC basal de 26.5 para 29.0.
    O IMC eleva a glicemia de jejum em 2.5 mg/dL por ponto acima de 22.
    A atividade fisica reduz a frequencia cardiaca basal de 75 para 65 bpm.

    A funcao calcular_risco() acumula incrementos de probabilidade para cada
    fator presente (idade, sexo, hipertensao, colesterol, HDL baixo, glicemia,
    tabagismo, IMC, sedentarismo, historico familiar) e o resultado determina
    a presenca de doenca cardiaca. O teto de risco e 0.95.

    Pacientes com doenca cardiaca recebem maior probabilidade de angina tipica
    (45%) e mais sintomas (1-4). Pacientes sem doenca recebem maior
    probabilidade de assintomatico (55%) e menos sintomas (0-2).

Reproducibilidade:

    O script utiliza seed fixa (SEED = 42) para garantir que execucoes
    repetidas produzam o mesmo dataset.
"""

import csv
import random
from pathlib import Path

# seed fixa para reproducibilidade entre execucoes
SEED = 42

# 300 pacientes (3x o minimo exigido pela atividade)
NUM_PACIENTES = 300

# sintomas cardiovasculares comuns utilizados na geracao dos dados
SINTOMAS_POSSIVEIS = [
    "dor_toracica",
    "dispneia",
    "palpitacao",
    "fadiga",
    "tontura",
    "edema_membros_inferiores",
    "sincope",
]

# classificacao clinica da dor toracica segundo padrao cardiologico
TIPOS_DOR_TORACICA = [
    "angina_tipica",
    "angina_atipica",
    "dor_nao_cardiaca",
    "assintomatico",
]


# cada tupla define (limiar, incremento) em ordem crescente de limiar.
# bisect localiza a faixa do valor e retorna o incremento correspondente.
FAIXAS_RISCO = {
    "idade":                       [(40, 0.05), (50, 0.15), (65, 0.25)],
    "pressao_arterial_sistolica":  [(130, 0.08), (140, 0.15)],
    "colesterol_total":            [(200, 0.08), (240, 0.15)],
    "glicemia_jejum":              [(100, 0.05), (126, 0.12)],
    "imc":                         [(25, 0.05), (30, 0.10)],
}

# cada tupla define (campo, condicao_para_incremento, incremento)
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
    O risco total nunca ultrapassa 0.95. A funcao retorna a probabilidade
    final que o gerador utiliza para determinar a presenca de doenca cardiaca.
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


def gerar_paciente(paciente_id: int) -> dict:
    """Gera os dados de um paciente com correlacoes clinicas realistas.

    O processo segue tres etapas:
    1. Sorteia variaveis demograficas e habitos de vida
    2. Deriva sinais vitais e exames laboratoriais aplicando correlacoes
       entre as variaveis (idade -> pressao, tabagismo -> colesterol,
       IMC -> glicemia, atividade fisica -> frequencia cardiaca)
    3. Calcula o risco acumulado e determina doenca cardiaca e sintomas
    """
    # prevalencia de tabagismo no Brasil: ~22% (IBGE/PNS)
    # prevalencia de atividade fisica regular: ~55%
    # prevalencia de historico familiar cardiaco: ~25%
    idade = random.randint(25, 85)
    sexo = random.choice(["M", "F"])
    tabagismo = random.random() < 0.22
    atividade_fisica = random.random() < 0.55
    historico_familiar = random.random() < 0.25

    # a pressao sistolica sobe em media 0.6 mmHg por ano acima dos 25
    base_sistolica = 110 + (idade - 25) * 0.6
    pressao_sistolica = int(random.gauss(base_sistolica, 15))
    pressao_sistolica = max(90, min(200, pressao_sistolica))

    pressao_diastolica = int(pressao_sistolica * random.gauss(0.62, 0.04))
    pressao_diastolica = max(55, min(120, pressao_diastolica))

    # o colesterol total sobe em media 0.8 mg/dL por ano acima dos 25
    # o tabagismo adiciona 15 mg/dL ao valor basal
    base_colesterol = 160 + (idade - 25) * 0.8
    if tabagismo:
        base_colesterol += 15
    colesterol_total = int(random.gauss(base_colesterol, 30))
    colesterol_total = max(120, min(350, colesterol_total))

    colesterol_hdl = int(random.gauss(55 if sexo == "F" else 45, 12))
    colesterol_hdl = max(20, min(100, colesterol_hdl))

    colesterol_ldl = int(colesterol_total * random.gauss(0.6, 0.08))
    colesterol_ldl = max(50, min(250, colesterol_ldl))

    triglicerideos = int(random.gauss(150, 60))
    triglicerideos = max(50, min(500, triglicerideos))

    # o IMC basal cai de 29.0 para 26.5 em pacientes fisicamente ativos
    # a glicemia sobe 2.5 mg/dL por ponto de IMC acima de 22
    imc = round(random.gauss(26.5 if atividade_fisica else 29.0, 4.5), 1)
    imc = max(16.0, min(45.0, imc))

    base_glicemia = 85 + (imc - 22) * 2.5
    glicemia_jejum = int(random.gauss(base_glicemia, 15))
    glicemia_jejum = max(65, min(300, glicemia_jejum))

    diabetes = glicemia_jejum >= 126

    # pacientes ativos apresentam frequencia cardiaca basal menor (65 vs 75 bpm)
    base_fc = 65 if atividade_fisica else 75
    frequencia_cardiaca = int(random.gauss(base_fc, 10))
    frequencia_cardiaca = max(45, min(120, frequencia_cardiaca))

    paciente = {
        "id_paciente": paciente_id,
        "idade": idade,
        "sexo": sexo,
        "pressao_arterial_sistolica": pressao_sistolica,
        "pressao_arterial_diastolica": pressao_diastolica,
        "colesterol_total": colesterol_total,
        "colesterol_hdl": colesterol_hdl,
        "colesterol_ldl": colesterol_ldl,
        "triglicerideos": triglicerideos,
        "glicemia_jejum": glicemia_jejum,
        "diabetes": diabetes,
        "frequencia_cardiaca": frequencia_cardiaca,
        "imc": imc,
        "tabagismo": tabagismo,
        "atividade_fisica": atividade_fisica,
        "historico_familiar_cardiaco": historico_familiar,
    }

    # o risco acumulado define a probabilidade de doenca cardiaca
    risco = calcular_risco(paciente)
    doenca_cardiaca = random.random() < risco

    # pacientes doentes recebem angina tipica com 45% de chance e 1-4 sintomas
    # pacientes saudaveis recebem assintomatico com 55% de chance e 0-2 sintomas
    if doenca_cardiaca:
        tipo_dor = random.choices(
            TIPOS_DOR_TORACICA, weights=[0.45, 0.30, 0.15, 0.10]
        )[0]
        num_sintomas = random.randint(1, 4)
    else:
        tipo_dor = random.choices(
            TIPOS_DOR_TORACICA, weights=[0.05, 0.10, 0.30, 0.55]
        )[0]
        num_sintomas = random.randint(0, 2)

    sintomas = random.sample(
        SINTOMAS_POSSIVEIS, min(num_sintomas, len(SINTOMAS_POSSIVEIS))
    )

    paciente["tipo_dor_toracica"] = tipo_dor
    paciente["sintomas"] = ";".join(sintomas) if sintomas else "nenhum"
    paciente["doenca_cardiaca"] = doenca_cardiaca

    return paciente


def main():
    """Gera o dataset e grava o CSV em data/numericos/dataset_cardiologico.csv.

    Exibe no terminal o total de pacientes e a distribuicao entre doentes e
    saudaveis para validacao rapida apos a execucao.
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
    print(f"Com doenca cardiaca: {total_doentes} ({total_doentes/len(pacientes)*100:.1f}%)")
    print(f"Sem doenca cardiaca: {len(pacientes)-total_doentes} ({(len(pacientes)-total_doentes)/len(pacientes)*100:.1f}%)")


if __name__ == "__main__":
    main()
