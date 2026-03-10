# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
    <a href= "https://www.fiap.com.br/">
        <img    src="assets/logo-fiap.png"
                alt="FIAP - Faculdade de Informática e Admnistração Paulista"
                border="0" width=40% height=40%>
    </a>
</p>

<br>

# Cap 1 - A Busca de Dados: Preparando o Terreno para a Inteligência Cardiológica

## Informações do Grupo: Murkveil
|Nome Completo|RM|
|---|---|
|[LEONARDO DE SENA](https://www.linkedin.com/in/leonardosena)|RM563351|

## Professores:
### Tutor
- [André Godoi Chiovato](https://www.linkedin.com/in/inova-fusca)

## Coordenador
- Caique Nonato da Silva Bezerra

## Descrição

O CardioIA é um projeto acadêmico do curso de Inteligência Artificial da FIAP que desafia o desenvolvimento de uma plataforma digital inteligente simulando o ecossistema de uma cardiologia moderna. O projeto integra dados clínicos, modelos de Machine Learning, Visão Computacional, IoT e agentes inteligentes para lidar com triagem, diagnósticos, monitoramento, assistência remota e previsões médicas.

Na Fase 1 - Batimentos de Dados, o objetivo é buscar, organizar e preparar três tipos de dados cardiológicos (numéricos, textuais e visuais) que alimentarão os módulos inteligentes do CardioIA nas fases seguintes.

## Estrutura do repositório

```
f1c1/
|-- README.md
|-- data/
|   |-- numericos/                      # Parte 1 - datasets tabulares (.csv)
|   |   |-- dataset_cardiologico.csv
|   |-- textuais/                       # Parte 2 - textos médicos (.txt)
|   |-- visuais/                        # Parte 3 - imagens de exames (.jpg/.png)
|-- scripts/
|   |-- gerar_dados_numericos.py        # gerador do dataset sintético
|-- notebooks/                          # (futuro) notebooks Colab/Jupyter
```

A documentação técnica detalhada de cada diretório está disponível em:
- [`data/README.md`](data/README.md) - dicionário de variáveis, relevância clínica, governança de dados
- [`scripts/README.md`](scripts/README.md) - uso, correlações clínicas, reprodutibilidade

---

## Parte 1 - Dados Numéricos (IoT)

### Objetivo

Buscar e preparar um dataset numérico contendo variáveis clínicas de pacientes cardiológicos para alimentar futuros algoritmos de IA do projeto CardioIA.

### Dataset

O arquivo [`data/numericos/dataset_cardiologico.csv`](data/numericos/dataset_cardiologico.csv) contém 300 registros sintéticos de pacientes cardiológicos com 18 variáveis clínicas.

#### Por que dados sintéticos?

Datasets cardiológicos reais envolvem informações sensíveis protegidas por legislação de privacidade (LGPD, HIPAA), o que restringe severamente sua disponibilização pública. A geração sintética permite:

- Controlar a distribuição dos dados e garantir balanceamento entre classes
- Criar correlações clinicamente coerentes entre variáveis
- Garantir reprodutibilidade total via seed fixa
- Eliminar riscos de privacidade e conformidade regulatória

O script [`scripts/gerar_dados_numericos.py`](scripts/gerar_dados_numericos.py) gera cada paciente em três etapas: sorteia variáveis demográficas com base em prevalências epidemiológicas brasileiras (IBGE/PNS), deriva sinais vitais e exames laboratoriais aplicando correlações clínicas, e determina a presença de doença cardíaca pelo risco acumulado.

#### Variáveis

| Grupo | Variáveis |
|-------|-----------|
| Demográficas | `id_paciente`, `idade`, `sexo` |
| Sinais vitais | `pressao_arterial_sistolica`, `pressao_arterial_diastolica`, `frequencia_cardiaca` |
| Exames laboratoriais | `colesterol_total`, `colesterol_hdl`, `colesterol_ldl`, `triglicerideos`, `glicemia_jejum` |
| Indicadores clínicos | `diabetes`, `imc` |
| Histórico e hábitos | `tabagismo`, `atividade_fisica`, `historico_familiar_cardiaco` |
| Sintomas e diagnóstico | `tipo_dor_toracica`, `sintomas`, `doenca_cardiaca` |

O dicionário completo com tipo, faixa, unidade e descrição de cada variável está documentado em [`data/README.md`](data/README.md).

#### Relevância clínica

As variáveis foram selecionadas com base nos principais fatores de risco cardiovascular reconhecidos pela Sociedade Brasileira de Cardiologia (SBC):

- **Pressão arterial** - a hipertensão arterial é o principal fator de risco modificável para doenças cardiovasculares. Valores sistólicos acima de 140 mmHg indicam hipertensão, elevando o risco de infarto e AVC.
- **Perfil lipídico** (colesterol total, HDL, LDL, triglicerídeos) - o LDL elevado deposita gordura nas artérias formando placas ateroscleróticas, enquanto o HDL atua como fator protetor. A razão entre colesterol total e HDL é um dos melhores preditores de risco cardiovascular.
- **Glicemia e diabetes** - o diabetes mellitus danifica os vasos sanguíneos ao longo do tempo, dobrando o risco de doença cardíaca.
- **IMC** - a obesidade (IMC acima de 30) sobrecarrega o coração e está associada a hipertensão, diabetes e dislipidemia.
- **Frequência cardíaca** - valores em repouso acima de 80 bpm estão associados a maior mortalidade cardiovascular.
- **Tabagismo** - o tabaco danifica o endotélio vascular e acelera a aterosclerose. Fumantes possuem risco duas a quatro vezes maior que não fumantes.
- **Histórico familiar** - a predisposição genética é um fator de risco não modificável relevante para estratificação de risco.
- **Dor torácica e sintomas** - a classificação da dor torácica é o primeiro critério de triagem em emergências cardiológicas, e os sintomas compõem o quadro clínico para triagem automatizada.

#### Importância para IA em saúde

O dataset foi projetado para alimentar múltiplos módulos de IA nas fases futuras do CardioIA:

- **Classificação** - modelos como Random Forest, XGBoost e redes neurais podem utilizar `doenca_cardiaca` como variável alvo para prever risco cardiovascular
- **Clusterização** - algoritmos como K-Means e DBSCAN podem identificar perfis de pacientes com características semelhantes, apoiando a estratificação de risco
- **NLP** - a coluna `sintomas` permite integração com módulos de processamento de linguagem natural para extração e correlação de sintomas
- **Balanceamento** - a distribuição próxima de 50/50 entre pacientes com e sem doença cardíaca evita viés de classe nos modelos

#### Governança de Dados

- Os dados são inteiramente sintéticos e não representam pacientes reais, eliminando riscos de privacidade e conformidade com LGPD
- A seed fixa (42) garante reprodutibilidade e auditabilidade do processo de geração
- As prevalências epidemiológicas refletem dados populacionais brasileiros publicados pelo IBGE/PNS
- O script de geração está versionado no repositório, permitindo rastreabilidade completa da origem dos dados

#### Verificação de integridade

| Propriedade | Valor |
|-------------|-------|
| Linhas | 300 (+ 1 cabeçalho) |
| Colunas | 18 |
| Seed | 42 |
| MD5 | `37494bc27300a66b716dd2ca10d2133f` |

```bash
# verificar integridade
md5sum data/numericos/dataset_cardiologico.csv

# regenerar dataset
python scripts/gerar_dados_numericos.py
```

---

## Parte 2 - Dados Textuais (NLP)

Status: pendente.

---

## Parte 3 - Dados Visuais (VC)

Status: pendente.

