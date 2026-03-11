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
|   |   |-- massa_et_al_2019_prevalencia_dcv_idosos.txt
|   |   |-- bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt
|   |-- visuais/                        # Parte 3 - imagens de exames (.jpg/.png)
|   |   |-- ecg/                       # eletrocardiogramas (.png)
|   |   |-- raio_x_toracico/           # raio-X de torax (.jpeg/.jpg/.png)
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

### Objetivo

Selecionar textos médicos relacionados a doenças cardiovasculares para alimentar futuros algoritmos de Processamento de Linguagem Natural (NLP) do projeto CardioIA.

### Textos selecionados

Os textos são papers científicos revisados por pares, publicados no periódico Ciência & Saúde Coletiva com acesso aberto via SciELO (licença Creative Commons). A escolha de papers garante estrutura textual bem definida (resumo, introdução, metodologia, resultados, discussão, conclusão) que algoritmos de NLP conseguem segmentar e classificar com maior precisão.

#### Paper 1 - Prevalência de DCV em idosos

| Metadado | Valor |
|----------|-------|
| Arquivo | [`massa_et_al_2019_prevalencia_dcv_idosos.txt`](data/textuais/massa_et_al_2019_prevalencia_dcv_idosos.txt) |
| Título | Análise da prevalência de doenças cardiovasculares e fatores associados em idosos, 2000-2010 |
| Autores | Massa, K.H.C.; Duarte, Y.A.O.; Chiavegatto Filho, A.D.P. |
| Periódico | Ciência & Saúde Coletiva, v.24, n.1, p.105-114, 2019 |
| DOI | [10.1590/1413-81232018241.02072017](https://doi.org/10.1590/1413-81232018241.02072017) |

O paper analisa a mudança na prevalência de doença cardiovascular entre idosos de São Paulo (2000-2010) utilizando dados do Estudo SABE. Identifica aumento significativo na prevalência (17,9% para 22,9%) e associações com idade avançada, tabagismo, diabetes e hipertensão.

#### Paper 2 - Fatores de risco cardiovascular em mulheres

| Metadado | Valor |
|----------|-------|
| Arquivo | [`bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt`](data/textuais/bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt) |
| Título | Conhecimento dos fatores de risco modificáveis para doença cardiovascular entre mulheres e seus fatores associados: um estudo de base populacional |
| Autores | Bonotto, G.M.; Mendoza-Sassi, R.A.; Susin, L.R.O. |
| Periódico | Ciência & Saúde Coletiva, v.21, n.1, p.293-302, 2016 |
| DOI | [10.1590/1413-81232015211.07232015](https://doi.org/10.1590/1413-81232015211.07232015) |

O paper avalia o conhecimento de 1.593 mulheres sobre fatores de risco cardiovascular modificáveis. Revela que apenas 33% conheciam três ou mais dos sete fatores pesquisados, com iniquidade associada a menor escolaridade e renda.

### Como algoritmos de NLP podem explorar os textos

Os papers selecionados oferecem conteúdo rico para múltiplas técnicas de NLP:

- **Extração de entidades clínicas (NER)** - identificar automaticamente menções a doenças (hipertensão, diabetes, DCV), fatores de risco (tabagismo, sedentarismo, obesidade), medicamentos e exames nos textos. Essas entidades alimentam bases de conhecimento médico estruturadas.

- **Classificação de tópicos** - categorizar seções e parágrafos por tema (epidemiologia, fatores de risco, metodologia estatística, recomendações clínicas). Modelos treinados nessa tarefa podem organizar automaticamente grandes volumes de literatura médica.

- **Análise de sentimento e tom clínico** - detectar a gravidade e urgência nas descrições de fatores de risco e resultados epidemiológicos. Essa análise apoia sistemas de triagem que priorizam pacientes com base em relatos textuais.

- **Extração de relações** - mapear relações causais entre fatores de risco e desfechos cardiovasculares (tabagismo eleva risco de DCV, hipertensão associada a infarto). Essas relações estruturadas alimentam grafos de conhecimento médico.

- **Sumarização automática** - gerar resumos concisos de papers longos para profissionais de saúde que precisam acessar evidências rapidamente durante a prática clínica.

### Relevância para IA aplicada à saúde

A aplicação de NLP em textos médicos cardiovasculares contribui diretamente para:

- Automatizar a revisão de literatura médica, acelerando a atualização de protocolos clínicos
- Alimentar chatbots e assistentes virtuais de saúde com informações baseadas em evidências
- Identificar lacunas no conhecimento populacional sobre fatores de risco, direcionando campanhas de saúde pública
- Apoiar sistemas de apoio à decisão clínica com extração automática de evidências da literatura

---

## Parte 3 - Dados Visuais (VC)

### Objetivo

Selecionar imagens de exames cardiológicos para alimentar futuros algoritmos de Visão Computacional (VC) do projeto CardioIA.

### Imagens selecionadas

O diretório [`data/visuais/`](data/visuais/) contém 100 imagens organizadas em duas categorias de exames cardiológicos:

#### ECG - Eletrocardiogramas (50 imagens)

| Metadado | Valor |
|----------|-------|
| Diretório | [`data/visuais/ecg/`](data/visuais/ecg/) |
| Formato | PNG |
| Origem | Kaggle - [ECG Dataset](https://www.kaggle.com/datasets/ankurray00/ecg-dataset) |
| Licença | CC-BY-NC-SA-4.0 |
| Classes | Normal Person (17), Abnormal Heartbeat (17), History of MI (16) |

As imagens representam traçados de eletrocardiograma de 12 derivações, o exame mais utilizado na prática cardiológica para detecção de arritmias, isquemia miocárdica e infarto. A distribuição balanceada entre as três classes permite treinar modelos de classificação sem viés significativo.

#### Raio-X torácico (50 imagens)

| Metadado | Valor |
|----------|-------|
| Diretório | [`data/visuais/raio_x_toracico/`](data/visuais/raio_x_toracico/) |
| Formato | JPEG/JPG/PNG |
| Origem | Kaggle - [COVID-19 Xray Dataset](https://www.kaggle.com/datasets/khoongweihao/covid19-xray-dataset-train-test-sets) |
| Licença | CC0-1.0 (domínio público) |
| Classes | Normal (25), Pneumonia (25) |

As imagens de raio-X torácico posteroanterior (PA) permitem visualizar a silhueta cardíaca, campos pulmonares e estruturas mediastinais. Alterações como cardiomegalia, congestão pulmonar e derrame pleural são indicadores visuais de insuficiência cardíaca e outras cardiopatias. A classificação entre Normal e Pneumonia exercita técnicas fundamentais de visão computacional aplicáveis a qualquer tarefa de diagnóstico por imagem.

### Como algoritmos de Visão Computacional podem explorar as imagens

As imagens selecionadas oferecem conteúdo para múltiplas técnicas de VC:

- **Classificação de imagens** - modelos como ResNet, EfficientNet e Vision Transformers (ViT) podem classificar ECGs em normal, arritmia e infarto, ou raios-X em normal e patológico. Essa tarefa é a base da triagem automatizada em cardiologia.

- **Detecção de anomalias** - algoritmos de detecção de anomalias podem identificar padrões atípicos nos traçados de ECG ou nas radiografias, sinalizando casos que requerem avaliação médica urgente.

- **Segmentação** - redes como U-Net podem segmentar a silhueta cardíaca em raios-X torácicos para calcular o índice cardiotorácico (ICT), métrica utilizada no diagnóstico de cardiomegalia.

- **Transfer learning** - modelos pré-treinados em grandes datasets de imagens médicas (como CheXNet) podem ser refinados com estas imagens para tarefas específicas do CardioIA, reduzindo a necessidade de grandes volumes de dados de treino.

- **Aumento de dados (data augmentation)** - técnicas como rotação, espelhamento, ajuste de brilho e contraste podem expandir o dataset de 100 imagens para milhares de amostras de treino, melhorando a generalização dos modelos.

### Relevância para IA aplicada à saúde

A aplicação de Visão Computacional em imagens cardiológicas contribui diretamente para:

- Automatizar a triagem de ECGs em unidades de emergência, priorizando pacientes com alterações críticas
- Apoiar o diagnóstico de cardiomegalia e insuficiência cardíaca por meio da análise automatizada de raios-X torácicos
- Reduzir o tempo de interpretação de exames em regiões com escassez de cardiologistas especializados
- Integrar com os módulos de dados numéricos e textuais do CardioIA para um sistema de apoio à decisão clínica multimodal

