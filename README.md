# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
    <a href= "https://www.fiap.com.br/">
        <img    src="assets/logo-fiap.png"
                alt="FIAP - Faculdade de Informática e Admnistração Paulista"
                border="0" width=40% height=40%>
    </a>
</p>

<br>

# CardioIA - Plataforma Digital Inteligente para Cardiologia

## Informações do Grupo: Murkveil

| Nome Completo | RM |
|---|---|
| [LEONARDO DE SENA](https://www.linkedin.com/in/leonardosena) | RM563351 |

### Tutor
- [André Godoi Chiovato](https://www.linkedin.com/in/inova-fusca)

### Coordenador
- Caique Nonato da Silva Bezerra

---

## Descrição

O CardioIA é um projeto acadêmico do curso de Inteligência Artificial da FIAP que simula o ecossistema de uma cardiologia moderna. O projeto integra dados clínicos, modelos de Machine Learning, Visão Computacional, IoT e agentes inteligentes para lidar com triagem, diagnósticos, monitoramento, assistência remota e previsões médicas.

O repositório cobre duas fases:

- **Fase 1 - Batimentos de Dados:** busca, organiza e prepara três tipos de dados cardiológicos (numéricos, textuais e visuais) que alimentam os módulos inteligentes nas fases seguintes.
- **Fase 2 - Diagnóstico Automatizado:** desenvolve um módulo inteligente que analisa relatos clínicos em linguagem natural, reconhece sintomas, detecta negações, qualifica achados semiológicos e sugere diagnósticos cardiovasculares assistidos por IA.

---

## Estrutura do repositório

```
f1c1/
|-- README.md
|-- data/
|   |-- README.md
|   |-- numericos/
|   |   |-- dataset_cardiologico.csv          # Fase 1 - 300 pacientes sintéticos (18 variáveis)
|   |   |-- heartbeat/                        # Ir Além 2a - MIT-BIH Heartbeat (Kaggle)
|   |   |   |-- mitbih_train.csv              #   87.554 batimentos de treino
|   |   |   |-- mitbih_test.csv               #   21.892 batimentos de teste
|   |-- textuais/
|   |   |-- massa_et_al_2019_prevalencia_dcv_idosos.txt
|   |   |-- bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt
|   |   |-- sintomas_pacientes.txt            # Fase 2 - 10 relatos de pacientes
|   |   |-- mapa_conhecimento.json            # Fase 2 - ontologia com 8 doenças e scoring declarativo
|   |   |-- mapa_conhecimento.csv             # Fase 2 - visão tabulada (20 combinações sintoma-doença)
|   |   |-- frases_risco.csv                  # Fase 2 - 160 frases rotuladas (alto/baixo risco)
|   |-- visuais/
|   |   |-- ecg/                              # Fase 1 - 50 ECGs (normal/arritmia/infarto)
|   |   |-- raio_x_toracico/                  # Fase 1 - 50 raios-X (normal/pneumonia)
|-- scripts/
|   |-- README.md
|   |-- gerar_dados_numericos.py              # Fase 1 - gerador do dataset sintético
|   |-- extracao_sintomas.py                  # wrapper de retrocompatibilidade (depreciado)
|   |-- cardio_extrator/                      # Fase 2 - pacote de extração de sintomas
|   |   |-- __init__.py                       # exports públicos
|   |   |-- cli.py                            # interface de linha de comando
|   |   |-- pipeline.py                       # orquestração do pipeline
|   |   |-- preprocessamento.py               # normalização de texto
|   |   |-- negacao.py                        # motor de negação contextual
|   |   |-- extratores.py                     # 7 extratores clínicos
|   |   |-- inferencia.py                     # motor de scoring declarativo
|   |   |-- formatacao.py                     # formatação de saída textual
|   |   |-- modelos.py                        # dataclasses de domínio
|   |   |-- io.py                             # carregamento de dados
|   |   |-- vocabulario/                      # subpacote de dados puros (regex pré-compilados)
|   |   |   |-- __init__.py
|   |   |   |-- sintomas.py                   # 22 sintomas cardiovasculares
|   |   |   |-- qualificadores.py             # qualificadores semiológicos
|   |   |   |-- contexto.py                   # contextos clínicos
|   |   |   |-- fatores_risco.py              # 6 fatores de risco
|   |   |   |-- medicacoes.py                 # 7 classes de medicações
|   |   |   |-- temporal.py                   # padrões temporais
|   |   |   |-- negacao.py                    # constantes de negação
|-- scripts/
|   |-- explorar_heartbeat.py                 # Ir Além 2a - inspeção do dataset MIT-BIH
|-- notebooks/
|   |-- classificador_risco.ipynb             # Fase 2 - TF-IDF + 3 modelos de classificação
|   |-- mlp_heartbeat_v2.ipynb                   # Ir Além 2a - MLP Heartbeat (v2, funcional)
|   |-- mlp_heartbeat_v1.ipynb                # Ir Além 2a - MLP Heartbeat (v1, falho - preservado)
|-- tests/
|   |-- test_extracao.py                      # 48 testes automatizados (pytest)
|-- docs/
|   |-- classificador-risco-cardiovascular.md # documentação técnica do classificador
|   |-- estrategia-compilacao-regex.md        # documentação técnica dos regex pré-compilados
|   |-- raciocinio/mlp-heartbeat/             # Ir Além 2a - raciocínio técnico (9 capítulos)
|   |   |-- exemplos/                         #   scripts complementares reproduzíveis
```

A documentação técnica detalhada está disponível em:
- [`data/README.md`](data/README.md) - dicionário de variáveis, relevância clínica, governança de dados
- [`scripts/README.md`](scripts/README.md) - uso dos scripts, arquitetura do pacote cardio_extrator
- [`scripts/cardio_extrator/README.md`](scripts/cardio_extrator/README.md) - decisões arquiteturais, fluxo do pipeline, como estender o sistema
- [`tests/README.md`](tests/README.md) - cobertura dos 48 testes, como executar
- [`docs/classificador-risco-cardiovascular.md`](docs/classificador-risco-cardiovascular.md) - TF-IDF, modelos, avaliação, limitações
- [`docs/estrategia-compilacao-regex.md`](docs/estrategia-compilacao-regex.md) - pré-compilação de regex, arquitetura do vocabulário
- [`docs/raciocinio/mlp-heartbeat/`](docs/raciocinio/mlp-heartbeat/) - raciocínio técnico do Ir Além 2a (inspeção, falha v1, experimentos v2)
- [`tests/README.md`](tests/README.md) - cobertura dos testes, como executar

---

## Fase 1 - Batimentos de Dados

### Parte 1 - Dados Numéricos (IoT)

#### Objetivo

Buscar e preparar um dataset numérico contendo variáveis clínicas de pacientes cardiológicos para alimentar futuros algoritmos de IA do projeto CardioIA.

#### Dataset

O arquivo [`data/numericos/dataset_cardiologico.csv`](data/numericos/dataset_cardiologico.csv) contém 300 registros sintéticos de pacientes cardiológicos com 18 variáveis clínicas.

#### Por que dados sintéticos?

A LGPD proíbe a disponibilização pública de dados clínicos reais sem anonimização certificada. Datasets cardiológicos contêm combinações únicas de idade, sexo e comorbidades que permitem reidentificação mesmo após pseudonimização. O script [`scripts/gerar_dados_numericos.py`](scripts/gerar_dados_numericos.py) gera dados inteiramente sintéticos com seed fixa para garantir reprodutibilidade sem risco jurídico. A alternativa de usar datasets públicos como o Cleveland Heart Disease exigiria verificação de conformidade com LGPD e limitaria o controle sobre distribuição de classes e correlações entre variáveis.

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

As variáveis refletem os principais fatores de risco cardiovascular reconhecidos pela Sociedade Brasileira de Cardiologia (SBC):

- **Pressão arterial** - a hipertensão arterial é o principal fator de risco modificável para doenças cardiovasculares. Valores sistólicos acima de 140 mmHg indicam hipertensão, elevando o risco de infarto e AVC.
- **Perfil lipídico** (colesterol total, HDL, LDL, triglicerídeos) - o LDL elevado deposita gordura nas artérias formando placas ateroscleróticas, enquanto o HDL atua como fator protetor.
- **Glicemia e diabetes** - o diabetes mellitus danifica os vasos sanguíneos ao longo do tempo, dobrando o risco de doença cardíaca.
- **IMC** - a obesidade (IMC acima de 30) sobrecarrega o coração e está associada a hipertensão, diabetes e dislipidemia.
- **Frequência cardíaca** - valores em repouso acima de 80 bpm estão associados a maior mortalidade cardiovascular.
- **Tabagismo** - o tabaco danifica o endotélio vascular e acelera a aterosclerose. Fumantes possuem risco duas a quatro vezes maior que não fumantes.
- **Histórico familiar** - a predisposição genética é um fator de risco não modificável relevante para estratificação de risco.
- **Dor torácica e sintomas** - a classificação da dor torácica é o primeiro critério de triagem em emergências cardiológicas, e os sintomas compõem o quadro clínico para triagem automatizada.

#### Governança de Dados

- O script de geração utiliza seed fixa (42) para reprodutibilidade e auditabilidade
- As prevalências epidemiológicas refletem dados populacionais brasileiros do IBGE/PNS
- O script está versionado no repositório, garantindo rastreabilidade completa da origem dos dados

#### Verificação de integridade

| Propriedade | Valor |
|-------------|-------|
| Linhas | 300 (+ 1 cabeçalho) |
| Colunas | 18 |
| Seed | 42 |
| MD5 | `37494bc27300a66b716dd2ca10d2133f` |

```bash
md5sum data/numericos/dataset_cardiologico.csv
python scripts/gerar_dados_numericos.py
```

---

### Parte 2a - Dados Textuais (NLP): Papers Científicos

#### Objetivo

Selecionar textos médicos relacionados a doenças cardiovasculares para alimentar futuros algoritmos de Processamento de Linguagem Natural (NLP) do projeto CardioIA.

#### Textos selecionados

Os textos são papers científicos revisados por pares, publicados no periódico Ciência & Saúde Coletiva com acesso aberto via SciELO (licença Creative Commons). A escolha de papers revisados por pares garante estrutura textual bem definida (resumo, introdução, metodologia, resultados, discussão, conclusão) que algoritmos de NLP conseguem segmentar e classificar com maior precisão. A alternativa de usar textos de blogs médicos ou materiais educativos introduziria inconsistência estrutural e terminológica que prejudicaria o treinamento de modelos.

#### Paper 1 - Prevalência de DCV em idosos

| Metadado | Valor |
|----------|-------|
| Arquivo | [`massa_et_al_2019_prevalencia_dcv_idosos.txt`](data/textuais/massa_et_al_2019_prevalencia_dcv_idosos.txt) |
| Título | Análise da prevalência de doenças cardiovasculares e fatores associados em idosos, 2000-2010 |
| Autores | Massa, K.H.C.; Duarte, Y.A.O.; Chiavegatto Filho, A.D.P. |
| Periódico | Ciência & Saúde Coletiva, v.24, n.1, p.105-114, 2019 |
| DOI | [10.1590/1413-81232018241.02072017](https://doi.org/10.1590/1413-81232018241.02072017) |

#### Paper 2 - Fatores de risco cardiovascular em mulheres

| Metadado | Valor |
|----------|-------|
| Arquivo | [`bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt`](data/textuais/bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt) |
| Título | Conhecimento dos fatores de risco modificáveis para doença cardiovascular entre mulheres e seus fatores associados: um estudo de base populacional |
| Autores | Bonotto, G.M.; Mendoza-Sassi, R.A.; Susin, L.R.O. |
| Periódico | Ciência & Saúde Coletiva, v.21, n.1, p.293-302, 2016 |
| DOI | [10.1590/1413-81232015211.07232015](https://doi.org/10.1590/1413-81232015211.07232015) |

---

### Parte 2b - Dados Textuais (NLP): Pipeline de Extração de Sintomas

#### Objetivo

Construir um sistema determinístico de NLP clínico que lê relatos de pacientes em linguagem natural, identifica sintomas cardiovasculares, detecta negações, qualifica achados semiológicos e sugere diagnósticos ponderados por valor discriminativo.

#### O que o pipeline faz

O pacote [`scripts/cardio_extrator/`](scripts/cardio_extrator/) executa o seguinte fluxo para cada relato:

1. **Normaliza** o texto (minúsculo, expansão de contrações coloquiais, correção ortográfica)
2. **Tokeniza** o texto para análise posicional
3. **Extrai sintomas** via regex pré-compilados (22 sintomas cardiovasculares)
4. **Detecta negação** contextual (negadores, restauradores, delimitadores de escopo, dupla negação)
5. **Extrai qualificadores** semiológicos (tipo de dor, irradiação, fatores de alívio/piora)
6. **Extrai contexto** clínico (pródromo viral, histórico familiar, esforço físico)
7. **Extrai temporalidade** (início, duração, frequência, progressão)
8. **Extrai fatores de risco** (tabagismo, diabetes, hipertensão, dislipidemia, obesidade, sedentarismo)
9. **Extrai medicações** (7 classes farmacológicas)
10. **Pontua diagnósticos** via motor declarativo (pesos, bônus, penalidades, normalização 0-1)
11. **Avalia red flags** de emergência cardiovascular (SCA, IC descompensada, síncope de esforço)

#### Mapa de conhecimento

O arquivo [`data/textuais/mapa_conhecimento.json`](data/textuais/mapa_conhecimento.json) contém a ontologia clínica que o motor de inferência consome. O JSON define 8 doenças cardiovasculares (DAC, IC, FA, EAo, HAS, miocardite, pericardite, CMH), cada uma com:

- Sintomas com pesos base individualizados
- Regras de bonificação com condições declarativas (AND/OR/COUNT_GE)
- Regras de exclusão com penalidades
- Fatores de risco com pesos aditivos
- Sinais clínicos, qualificadores de referência e discriminadores textuais

Adicionar uma nova doença ao sistema requer apenas editar o JSON — zero alteração no código Python.

#### Como executar

```bash
# saída textual (padrão)
PYTHONPATH=scripts python -m cardio_extrator

# saída JSON
PYTHONPATH=scripts python -m cardio_extrator --formato json

# ambos os formatos em arquivo
PYTHONPATH=scripts python -m cardio_extrator --formato ambos --saida resultado

# com logging detalhado
PYTHONPATH=scripts python -m cardio_extrator --log INFO
```

#### Exemplo de saída (resumido)

```
RELATO 1: "Há três dias sinto uma dor forte no peito, como um aperto..."

SINTOMAS IDENTIFICADOS:
  + dor_toracica (expressão: "dor forte no peito")

QUALIFICADORES SEMIOLÓGICOS:
  dor_toracica: tipo_opressiva, irradiacao_mse, piora_esforco, alivio_repouso

DIAGNÓSTICOS SUGERIDOS:
  1. Doença Arterial Coronariana (normalizado: 0.45 | confiança: moderada)
     - bônus +1.2: Padrão esforço-repouso define angina típica (critérios Diamond-Forrester)
```

---

### Parte 2c - Classificador de Risco Cardiovascular

#### Objetivo

Treinar um classificador de texto que analisa frases com sintomas cardiovasculares e classifica o nível de risco como "alto risco" ou "baixo risco", simulando a triagem clínica automatizada.

#### Dataset

O arquivo [`data/textuais/frases_risco.csv`](data/textuais/frases_risco.csv) contém 160 frases médicas rotuladas manualmente:

| Propriedade | Valor |
|-------------|-------|
| Frases | 160 |
| Alto risco | 81 (50.6%) |
| Baixo risco | 79 (49.4%) |
| Ambíguas intencionais | ~15-20% |

Os critérios de rotulação seguem protocolos de triagem cardiovascular: frases com sintomas sugestivos de emergência (dor torácica opressiva, dispneia aguda, síncope, sinais de IC descompensada) recebem "alto risco"; queixas benignas ou crônicas estáveis recebem "baixo risco".

#### Notebook

O notebook [`notebooks/classificador_risco.ipynb`](notebooks/classificador_risco.ipynb) implementa:

1. **Vetorização TF-IDF** com unigramas e bigramas (`ngram_range=(1,2)`) → matriz 160x379
2. **3 modelos** comparados: Logistic Regression, Decision Tree, Naive Bayes
3. **Avaliação** com Stratified 5-Fold CV: precision, recall, F1-macro por classe
4. **Análise de coeficientes** da Logistic Regression (termos mais discriminativos)
5. **Teste com 10 frases novas** incluindo casos ambíguos

#### Resultados (Stratified 5-Fold CV)

| Modelo | Acurácia | F1-macro |
|--------|----------|----------|
| Logistic Regression | 0.856 +/- 0.037 | 0.856 +/- 0.037 |
| Decision Tree | 0.662 +/- 0.050 | 0.658 +/- 0.049 |
| Naive Bayes | 0.856 +/- 0.051 | 0.856 +/- 0.051 |

A documentação técnica completa (TF-IDF, hiperparâmetros, análise de coeficientes, limitações) está em [`docs/classificador-risco-cardiovascular.md`](docs/classificador-risco-cardiovascular.md).

---

### Parte 3 - Dados Visuais (VC)

#### Objetivo

Selecionar imagens de exames cardiológicos para alimentar futuros algoritmos de Visão Computacional (VC) do projeto CardioIA.

#### ECG - Eletrocardiogramas (50 imagens)

| Metadado | Valor |
|----------|-------|
| Diretório | [`data/visuais/ecg/`](data/visuais/ecg/) |
| Formato | PNG |
| Origem | Kaggle - [ECG Dataset](https://www.kaggle.com/datasets/ankurray00/ecg-dataset) |
| Licença | CC-BY-NC-SA-4.0 |
| Classes | Normal (17), Arritmia (17), Infarto (16) |

#### Raio-X torácico (50 imagens)

| Metadado | Valor |
|----------|-------|
| Diretório | [`data/visuais/raio_x_toracico/`](data/visuais/raio_x_toracico/) |
| Formato | JPEG/JPG/PNG |
| Origem | Kaggle - [COVID-19 Xray Dataset](https://www.kaggle.com/datasets/khoongweihao/covid19-xray-dataset-train-test-sets) |
| Licença | CC0-1.0 (domínio público) |
| Classes | Normal (25), Pneumonia (25) |

---

## Ir Além 2a - MLP para Classificação de Batimentos Cardíacos

### Objetivo

Aplicar uma rede neural MLP (Perceptron Multicamadas) com Keras para classificar
batimentos cardíacos do dataset MIT-BIH Heartbeat como normal ou anormal.

### Dataset

| Propriedade | Valor |
|-------------|-------|
| Origem | [Kaggle - shayanfazeli/heartbeat](https://www.kaggle.com/datasets/shayanfazeli/heartbeat) |
| Treino | 87.554 batimentos (187 amostras do sinal + 1 classe) |
| Teste | 21.892 batimentos |
| Classes originais | 5 (Normal, Supraventricular, Ventricular, Fusão, Desconhecido) |
| Classes binárias | 2 (Normal 82.8% vs. Anormal 17.2%) |

### Notebook

O notebook [`notebooks/mlp_heartbeat_v2.ipynb`](notebooks/mlp_heartbeat_v2.ipynb) (v2) implementa:

1. Carregamento e binarização do dataset (5 classes → 2)
2. Embaralhamento dos dados e compensação de desbalanceamento via `class_weight`
3. MLP com 3 camadas densas (128→64→32) + BatchNormalization + Dropout
4. Treinamento com Adam (lr=0.0005), early stopping (patience=10) e validation split
5. Avaliação: acurácia, precision, recall, F1, matriz de confusão, recall por classe original

### Resultados (v2)

| Métrica | Valor |
|---------|-------|
| Acurácia | 0.976 |
| Recall Normal | 0.985 |
| Recall Anormal | 0.933 |
| F1-macro | 0.959 |
| Taxa de Falsos Negativos | 6.65% |

### Recall por classe original

| Classe | Recall |
|--------|--------|
| Normal (N) | 0.985 |
| Supraventricular (S) | 0.732 |
| Ventricular (V) | 0.963 |
| Fusão (F) | 0.852 |
| Desconhecido (Q) | 0.985 |

### Evolução do modelo

O modelo v1 (`mlp_heartbeat_v1.ipynb`) atingiu apenas 5.17% de recall Anormal —
praticamente não detectava arritmias. A análise de falha identificou que o
`validation_split` do Keras extraía uma fatia não-representativa do CSV ordenado,
causando early stopping prematuro na época 6. A correção principal embaralha os
dados antes do treino. O modelo v2 atinge 93.3% de recall Anormal — melhoria de
18x.

| Métrica | v1 | v2 | Melhoria |
|---------|----|----|----------|
| Recall Anormal | 0.052 | 0.933 | 18x |
| F1-macro | 0.504 | 0.959 | 1.9x |
| Taxa FN | 94.83% | 6.65% | 14x redução |

A documentação completa do raciocínio técnico (9 capítulos + 4 scripts complementares)
está em [`docs/raciocinio/mlp-heartbeat/`](docs/raciocinio/mlp-heartbeat/).

### Vídeo
> O YouTube estava deletando meu video. Tive que separar em duas partes:

[Fase 2 Obrigatória - PARTE 1 - EXTRAÇÃO DE SINTOMAS](https://youtu.be/XheDuewAfKI)

[Fase 2 Obrigatória - PARTE 2 - CLASSIFICADOR TF-IDF](https://youtu.be/MAaB64KlukE)

---

## Como executar

### Requisitos

- Python 3.11+
- pytest (apenas para testes)
- TensorFlow/Keras, NumPy, Pandas, matplotlib, scikit-learn (para o Ir Além 2a)
- Nenhuma dependência externa para o código de produção do pipeline de extração

### Gerar dataset numérico (Fase 1)

```bash
python scripts/gerar_dados_numericos.py
```

### Executar pipeline de extração (Fase 2)

```bash
PYTHONPATH=scripts python -m cardio_extrator
```

### Executar notebook MLP Heartbeat (Ir Além 2a)

```bash
# baixar dataset (usa credenciais do .env, verifica integridade via SHA256)
python scripts/baixar_heartbeat.py

# executar notebook
cd notebooks && jupyter nbconvert --to notebook --execute mlp_heartbeat_v2.ipynb
```

### Executar testes

```bash
PYTHONPATH=scripts python -m pytest tests/ -v
```

---

## Testes

O arquivo [`tests/test_extracao.py`](tests/test_extracao.py) contém 48 testes automatizados organizados em 10 classes que cobrem todas as camadas do pipeline de extração:

| Classe | Testes | O que valida |
|--------|--------|-------------|
| TestNegacao | 6 | Negação simples, com afirmação, dupla negação, "sem", delimitadores de escopo |
| TestTemporal | 5 | Início, duração, progressão, frequência |
| TestScoring | 10 | Doença fictícia sem alterar código, normalização, penalidade, operadores AND/OR/COUNT_GE |
| TestNormalizacao | 2 | Confiança baixa e alta |
| TestColoquialismo | 6 | Contrações, espaços, correção ortográfica, palavras intermediárias, DPN com madrugada |
| TestFatoresRisco | 5 | Tabagismo, diabetes, hipertensão, múltiplos, ausência |
| TestMedicacoes | 4 | Anti-hipertensivo, estatina, múltiplas classes, ausência |
| TestSaidaEstruturada | 2 | Serialização JSON, campos completos |
| TestRedFlags | 5 | IC descompensada, síncope de esforço, SCA, sem alertas, prioridade |
| TestIntegracao | 3 | 10 relatos com diagnósticos esperados, DAC clássico, pericardite clássica |

---

## Tecnologias

| Tecnologia | Uso |
|-----------|-----|
| Python 3.11+ | Linguagem principal |
| Biblioteca padrão (`re`, `json`, `csv`, `pathlib`, `bisect`, `argparse`, `logging`, `dataclasses`) | Pipeline de extração (código de produção) |
| scikit-learn | Métricas, class_weight, TF-IDF (classificador + MLP) |
| TensorFlow/Keras | Construção, treino e avaliação da MLP (Ir Além 2a) |
| NumPy, Pandas, matplotlib | Manipulação de dados e visualização |
| pytest | Framework de testes |

O projeto utiliza exclusivamente a biblioteca padrão do Python para o código de produção. Sistemas clínicos de apoio à decisão exigem determinismo e auditabilidade — cada decisão diagnóstica deve ser rastreável a uma regra explícita no mapa de conhecimento. Modelos de linguagem (LLMs) ou bibliotecas de NLP como spaCy introduziriam não-determinismo, dependências pesadas e impossibilidade de auditar por que o sistema chegou a uma conclusão específica. A escolha de regex pré-compilados garante que o pipeline produz exatamente o mesmo resultado para o mesmo input, sempre.
