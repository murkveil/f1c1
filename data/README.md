# data

Diretório central de dados do projeto CardioIA. Armazena todos os datasets que alimentam os módulos de Inteligência Artificial nas fases do projeto.

## Estrutura

```
data/
|-- numericos/
|   |-- dataset_cardiologico.csv             # Fase 1 - 300 pacientes (18 variáveis)
|-- textuais/
|   |-- massa_et_al_2019_prevalencia_dcv_idosos.txt      # Fase 1 - paper NLP
|   |-- bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt  # Fase 1 - paper NLP
|   |-- sintomas_pacientes.txt               # Fase 2 - 10 relatos de pacientes
|   |-- mapa_conhecimento.json               # Fase 2 - ontologia (8 doenças, scoring)
|   |-- mapa_conhecimento.csv                # Fase 2 - visão tabulada (20 combinações)
|-- visuais/
|   |-- ecg/                                 # Fase 1 - 50 ECGs (.png)
|   |-- raio_x_toracico/                     # Fase 1 - 50 raios-X (.jpeg/.jpg/.png)
```

## Por que `data/` e não `docs/` ou `assets/`?

A atividade sugere armazenar dados em `docs/` ou `assets/`, porém essas convenções possuem significado reservado em repositórios Git:

- `docs/` - a comunidade Git e o GitHub reservam esse diretório para documentação do projeto (guias, referências de API, arquitetura). O GitHub permite servir GitHub Pages diretamente a partir dele. Armazenar dados brutos nesse diretório gera conflito semântico com essa finalidade.
- `assets/` - a comunidade utiliza esse diretório para recursos estáticos do projeto em si (logos, ícones de UI, imagens de documentação). Os dados desta atividade não se encaixam nessa categoria.

Os textos, CSVs e imagens deste projeto representam dados de entrada para algoritmos de IA, não documentação nem recursos visuais do projeto. O diretório `data/` segue o padrão consolidado em projetos de data science e machine learning, estabelecido pela convenção do cookiecutter-data-science, e separa dados brutos de documentação de forma clara. A subdivisão em `numericos/`, `textuais/` e `visuais/` organiza os dados por tipo de processamento (IoT, NLP e Visão Computacional) de forma escalável para as fases futuras do CardioIA.

---

## numericos/

Contém datasets tabulares em formato CSV para a Parte 1 (Dados Numéricos/IoT) do projeto.

### dataset_cardiologico.csv

Dataset sintético de pacientes cardiológicos gerado pelo script `scripts/gerar_dados_numericos.py`. Os dados são sintéticos porque datasets cardiológicos reais envolvem informações sensíveis protegidas por legislação de privacidade (LGPD, HIPAA), o que restringe severamente sua disponibilização pública. A geração sintética permite controlar a distribuição dos dados, garantir reprodutibilidade e criar correlações clinicamente coerentes entre as variáveis.

#### Origem dos dados

O script gera cada paciente em três etapas:

1. Sorteia variáveis demográficas e hábitos de vida com base em prevalências epidemiológicas brasileiras (IBGE/PNS)
2. Deriva sinais vitais e exames laboratoriais aplicando correlações clínicas entre as variáveis
3. Calcula o risco acumulado de doença cardíaca e determina diagnóstico e sintomas

As prevalências utilizadas refletem dados populacionais reais: tabagismo em aproximadamente 22% da população (IBGE/PNS), prática de atividade física regular em 55% e histórico familiar cardíaco em 25%.

#### Propriedades do dataset

| Propriedade | Valor |
|-------------|-------|
| Arquivo | `data/numericos/dataset_cardiologico.csv` |
| Linhas | 300 (+ 1 cabeçalho) |
| Colunas | 18 |
| Encoding | UTF-8 |
| Seed | 42 |
| MD5 | `37494bc27300a66b716dd2ca10d2133f` |

#### Dicionário de variáveis

##### Demográficas

| Variável | Tipo | Faixa | Descrição |
|----------|------|-------|-----------|
| `id_paciente` | int | 1-300 | Identificador único do paciente |
| `idade` | int | 25-85 | Idade do paciente em anos |
| `sexo` | str | M, F | Sexo biológico |

##### Sinais vitais

| Variável | Tipo | Faixa | Unidade | Descrição |
|----------|------|-------|---------|-----------|
| `pressao_arterial_sistolica` | int | 90-200 | mmHg | Pressão arterial sistólica |
| `pressao_arterial_diastolica` | int | 55-120 | mmHg | Pressão arterial diastólica |
| `frequencia_cardiaca` | int | 45-120 | bpm | Frequência cardíaca em repouso |

##### Exames laboratoriais

| Variável | Tipo | Faixa | Unidade | Descrição |
|----------|------|-------|---------|-----------|
| `colesterol_total` | int | 120-350 | mg/dL | Colesterol total sérico |
| `colesterol_hdl` | int | 20-100 | mg/dL | Colesterol HDL (lipoproteína de alta densidade) |
| `colesterol_ldl` | int | 50-250 | mg/dL | Colesterol LDL (lipoproteína de baixa densidade) |
| `triglicerideos` | int | 50-500 | mg/dL | Triglicerídeos séricos |
| `glicemia_jejum` | int | 65-300 | mg/dL | Glicemia de jejum |

##### Indicadores clínicos

| Variável | Tipo | Faixa | Descrição |
|----------|------|-------|-----------|
| `diabetes` | bool | True, False | Presença de diabetes (glicemia de jejum >= 126 mg/dL) |
| `imc` | float | 16.0-45.0 | Índice de massa corporal (kg/m2) |

##### Histórico e hábitos

| Variável | Tipo | Faixa | Descrição |
|----------|------|-------|-----------|
| `tabagismo` | bool | True, False | Paciente fumante |
| `atividade_fisica` | bool | True, False | Pratica atividade física regular |
| `historico_familiar_cardiaco` | bool | True, False | Histórico familiar de doença cardíaca |

##### Sintomas e diagnóstico

| Variável | Tipo | Valores possíveis | Descrição |
|----------|------|-------------------|-----------|
| `tipo_dor_toracica` | str | angina_tipica, angina_atipica, dor_nao_cardiaca, assintomatico | Classificação clínica da dor torácica |
| `sintomas` | str | dor_toracica, dispneia, palpitacao, fadiga, tontura, edema_membros_inferiores, sincope, nenhum | Lista de sintomas separados por ponto e vírgula |
| `doenca_cardiaca` | bool | True, False | Variável alvo (target) para modelos de classificação |

#### Relevância clínica das variáveis

As variáveis do dataset foram selecionadas com base nos principais fatores de risco cardiovascular reconhecidos pela literatura médica e pelas diretrizes da Sociedade Brasileira de Cardiologia (SBC):

- `pressao_arterial_sistolica` e `pressao_arterial_diastolica` - a hipertensão arterial é o principal fator de risco modificável para doenças cardiovasculares. Valores sistólicos acima de 140 mmHg ou diastólicos acima de 90 mmHg indicam hipertensão, elevando significativamente o risco de infarto e AVC.

- `colesterol_total`, `colesterol_hdl` e `colesterol_ldl` - o perfil lipídico é determinante na formação de placas ateroscleróticas. O LDL elevado (acima de 160 mg/dL) deposita gordura nas artérias, enquanto o HDL atua como fator protetor ao transportar colesterol de volta ao fígado. A razão entre colesterol total e HDL é um dos melhores preditores de risco cardiovascular.

- `glicemia_jejum` e `diabetes` - o diabetes mellitus danifica os vasos sanguíneos ao longo do tempo, dobrando o risco de doença cardíaca. A glicemia de jejum acima de 126 mg/dL indica diabetes, e valores entre 100 e 125 mg/dL indicam pré-diabetes.

- `imc` - o índice de massa corporal acima de 30 (obesidade) sobrecarrega o coração e está associado a hipertensão, diabetes e dislipidemia. É um indicador rápido de risco metabólico.

- `frequencia_cardiaca` - a frequência cardíaca em repouso acima de 80 bpm está associada a maior mortalidade cardiovascular. Pacientes fisicamente ativos apresentam frequência basal menor devido ao condicionamento do músculo cardíaco.

- `tabagismo` - o tabaco danifica o endotélio vascular, eleva a pressão arterial e acelera a aterosclerose. Fumantes possuem risco de doença cardíaca duas a quatro vezes maior que não fumantes.

- `historico_familiar_cardiaco` - a predisposição genética para doenças cardiovasculares é um fator de risco não modificável. Pacientes com parentes de primeiro grau acometidos antes dos 55 anos (homens) ou 65 anos (mulheres) possuem risco elevado.

- `tipo_dor_toracica` - a classificação da dor torácica (angina típica, atípica, não cardíaca ou assintomático) é o primeiro critério de triagem em emergências cardiológicas. A angina típica apresenta as três características clássicas: dor retroesternal, provocada por esforço e aliviada por repouso ou nitroglicerina.

- `sintomas` - sintomas como dispneia (falta de ar), palpitação, fadiga, tontura, edema de membros inferiores e síncope (desmaio) compõem o quadro clínico que algoritmos de NLP e classificação podem utilizar para triagem automatizada.

#### Importância para Inteligência Artificial em saúde

O script projeta o dataset para alimentar múltiplos módulos de IA nas fases futuras do CardioIA:

- Modelos de classificação (Random Forest, XGBoost, redes neurais) podem utilizar `doenca_cardiaca` como variável alvo para prever risco cardiovascular a partir dos fatores clínicos
- Algoritmos de clusterização (K-Means, DBSCAN) podem identificar perfis de pacientes com características semelhantes, apoiando a estratificação de risco
- A coluna `sintomas` permite integração com módulos de NLP para extração e correlação de sintomas em texto livre
- As correlações entre variáveis refletem relações clínicas reais, permitindo que modelos aprendam padrões epidemiologicamente válidos em vez de ruído estatístico
- O balanceamento próximo de 50/50 entre pacientes com e sem doença cardíaca evita viés de classe nos modelos de classificação

#### Considerações sobre Governança de Dados

- Os dados são inteiramente sintéticos e não representam pacientes reais, eliminando riscos de privacidade e conformidade com LGPD
- A seed fixa garante reprodutibilidade e auditabilidade do processo de geração
- As prevalências epidemiológicas utilizadas refletem dados populacionais brasileiros publicados pelo IBGE/PNS, conferindo verossimilhança sem comprometer dados individuais
- O script de geração está versionado em `scripts/gerar_dados_numericos.py`, permitindo rastreabilidade completa da origem dos dados

#### Verificação de integridade

Para verificar que o dataset não foi alterado após a geração:

```bash
md5sum data/numericos/dataset_cardiologico.csv
# esperado: 37494bc27300a66b716dd2ca10d2133f
```

Para regenerar o dataset a partir do script:

```bash
python scripts/gerar_dados_numericos.py
```

---

## textuais/

Contém papers científicos em formato `.txt` para a Parte 2 (Dados Textuais/NLP) do projeto. Os textos são artigos revisados por pares publicados no periódico Ciência & Saúde Coletiva com acesso aberto via SciELO (licença Creative Commons).

### massa_et_al_2019_prevalencia_dcv_idosos.txt

| Metadado | Valor |
|----------|-------|
| Título | Análise da prevalência de doenças cardiovasculares e fatores associados em idosos, 2000-2010 |
| Autores | Kaio Henrique Correa Massa, Yeda Aparecida Oliveira Duarte, Alexandre Dias Porto Chiavegatto Filho |
| Periódico | Ciência & Saúde Coletiva |
| Volume/Número/Páginas | v.24, n.1, p.105-114 |
| Ano | 2019 |
| DOI | [10.1590/1413-81232018241.02072017](https://doi.org/10.1590/1413-81232018241.02072017) |
| ISSN | 1678-4561 |
| Palavras-chave | Doenças cardiovasculares; Epidemiologia; Idoso; Doença crônica |
| URL | [SciELO](https://www.scielo.br/j/csc/a/9mjfHq4BdxPZgdPLNq9x5Rw/?lang=pt) |
| PDF | [Download](https://www.scielo.br/j/csc/a/9mjfHq4BdxPZgdPLNq9x5Rw/?format=pdf&lang=pt) |
| Licença | Creative Commons (acesso aberto via SciELO) |

O paper utiliza dados do Estudo SABE para analisar a mudança na prevalência de doença cardiovascular entre idosos de São Paulo no período de 2000 a 2010. Aplica modelos multinível bayesianos e regressão logística, identificando aumento significativo na prevalência (de 17,9% para 22,9%) e associações com idade avançada, histórico de tabagismo, diabetes e hipertensão.

Relevância para NLP: o texto contém terminologia epidemiológica densa, dados estatísticos estruturados (odds ratios, intervalos de confiança), descrições de fatores de risco e relações causais entre variáveis clínicas — conteúdo ideal para extração de entidades clínicas, mapeamento de relações causais e classificação de tópicos médicos.

### bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt

| Metadado | Valor |
|----------|-------|
| Título | Conhecimento dos fatores de risco modificáveis para doença cardiovascular entre mulheres e seus fatores associados: um estudo de base populacional |
| Autores | Gabriel Missaggia Bonotto, Raul Andres Mendoza-Sassi, Lulie Rosane Odeh Susin |
| Periódico | Ciência & Saúde Coletiva |
| Volume/Número/Páginas | v.21, n.1, p.293-302 |
| Ano | 2016 |
| DOI | [10.1590/1413-81232015211.07232015](https://doi.org/10.1590/1413-81232015211.07232015) |
| ISSN | 1678-4561 |
| Palavras-chave | Conhecimento; Conhecimentos, atitudes e práticas em saúde; Fatores de risco; Doenças cardiovasculares; Mulheres |
| URL | [SciELO](https://www.scielo.br/j/csc/a/Smt5y5xfY9Yvws8CxPsKMpg/?lang=pt) |
| PDF | [Download](https://www.scielo.br/j/csc/a/Smt5y5xfY9Yvws8CxPsKMpg/?format=pdf&lang=pt) |
| Licença | Creative Commons (acesso aberto via SciELO) |

O paper avalia o nível de conhecimento de 1.593 mulheres sobre fatores de risco cardiovascular modificáveis em Rio Grande (RS). Revela que apenas 33% conheciam três ou mais dos sete fatores de risco pesquisados, com iniquidade significativa associada a menor escolaridade e renda familiar.

Relevância para NLP: o texto aborda percepção populacional sobre saúde cardiovascular, contendo vocabulário de saúde pública, descrições de fatores de risco em linguagem acessível e análises de iniquidade social — conteúdo relevante para análise de sentimento, extração de sintomas mencionados espontaneamente e classificação de nível de conhecimento em saúde.

### Formato dos arquivos

Cada arquivo `.txt` segue a mesma estrutura:

1. Cabeçalho de metadados (título, autores, DOI, ISSN, URLs, licença)
2. Texto completo organizado por seções (resumo, introdução, metodologia, resultados, discussão, limitações, conclusão)

Essa estrutura facilita o pré-processamento por pipelines de NLP, permitindo segmentação automática por seções e extração de metadados via parsing do cabeçalho.

### sintomas_pacientes.txt (Fase 2)

Arquivo de entrada do pipeline de extração de sintomas (`cardio_extrator`). Contém 10 relatos simulados de pacientes cardiológicos, um por linha.

| Propriedade | Valor |
|-------------|-------|
| Formato | Texto puro, UTF-8, um relato por linha |
| Linhas | 10 |
| Idioma | Português brasileiro |

Cada relato descreve o que o paciente sente, quando começou e como os sintomas afetam sua rotina. Os 10 relatos exercitam as 8 doenças cardiovasculares do mapa de conhecimento:

| Relato | Doença exercitada | Achados-chave |
|--------|-------------------|---------------|
| 1 | Doença Arterial Coronariana | Dor opressiva, irradiação MSE, alívio ao repouso |
| 2 | Insuficiência Cardíaca | DPN, edema MMII, fadiga |
| 3 | Fibrilação Atrial | Palpitações irregulares, início súbito |
| 4 | Estenose Aórtica | Tríade dispneia-angina-síncope de esforço |
| 5 | Hipertensão Arterial | Cefaleia occipital, tontura, zumbido, epistaxe, visão turva |
| 6 | Miocardite | Pródromo viral, dor torácica, febre, taquicardia |
| 7 | Pericardite | Dor pleurítica, alívio inclinado, irradiação trapézio |
| 8 | Cardiomiopatia Hipertrófica | Síncope de esforço, história familiar morte súbita |
| 9 | Insuficiência Cardíaca | Ortopneia (3 travesseiros), edema, noctúria |
| 10 | Fibrilação Atrial | Palpitações paroxísticas, precipitantes (café, estresse) |

### mapa_conhecimento.json (Fase 2)

Ontologia clínica que o motor de inferência do `cardio_extrator` consome. O JSON define a base de conhecimento completa para diagnóstico diferencial cardiovascular.

| Propriedade | Valor |
|-------------|-------|
| Formato | JSON, UTF-8 |
| Linhas | 758 |
| Doenças | 8 |
| Red flags | 5 |

#### Por que JSON e não CSV ou YAML

O mapa de conhecimento contém estruturas aninhadas com profundidade variável — uma doença possui sintomas com pesos, regras de bonificação com condições compostas (AND/OR/COUNT_GE) e fatores de risco. CSV não suporta aninhamento sem achatamento destrutivo que perderia a semântica das relações hierárquicas. YAML suportaria a estrutura, mas adiciona ambiguidade de tipos (strings vs booleanos, indentação significativa) e não possui suporte nativo na stdlib do Python sem dependência externa (`pyyaml`). JSON é nativo na stdlib (`json`), não-ambíguo em tipos e suporta aninhamento arbitrário.

#### Estrutura do JSON

```
mapa_conhecimento.json
|-- <chave_doença>              # 8 doenças
|   |-- nome_exibicao           # nome com acentos para saída
|   |-- sigla                   # sigla clínica (DAC, IC, FA, etc.)
|   |-- sinais                  # lista de sinais ao exame físico (referência)
|   |-- qualificadores_referencia  # qualificadores semiológicos descritivos
|   |-- discriminadores         # achados de alto valor discriminativo (texto livre)
|   |-- scoring
|   |   |-- sintomas            # {sintoma: {peso_base: float}}
|   |   |-- regras_bonificacao  # [{condicao, bonus, justificativa}]
|   |   |-- regras_exclusao     # [{condicao, penalidade, justificativa}]
|   |   |-- fatores_risco       # {fator: peso}
|-- intersecoes                 # {sintoma: [doenças que compartilham]}
|-- ambiguidades_clinicas       # [{par, sobreposição, diferenciação}]
|-- red_flags                   # [{nome, condicao, mensagem, prioridade}]
```

#### Doenças cobertas

| Doença | Sigla | Sintomas (scoring) | Bônus | Exclusões | Fatores de risco |
|--------|-------|---------------------|-------|-----------|------------------|
| Doença Arterial Coronariana | DAC | 6 | 6 | 2 | 5 |
| Insuficiência Cardíaca | IC | 10 | 4 | 0 | 4 |
| Fibrilação Atrial | FA | 5 | 3 | 0 | 3 |
| Estenose Aórtica | EAo | 3 | 3 | 0 | 0 |
| Hipertensão Arterial Sistêmica | HAS | 7 | 1 | 0 | 4 |
| Miocardite | - | 7 | 3 | 0 | 0 |
| Pericardite | - | 5 | 5 | 1 | 0 |
| Cardiomiopatia Hipertrófica | CMH | 4 | 2 | 0 | 0 |

### mapa_conhecimento.csv (Fase 2)

Visão tabulada do mapa de conhecimento que satisfaz o formato exigido pelo enunciado da atividade (Sintoma 1 | Sintoma 2 | Doença Associada). O enunciado solicita um arquivo CSV com associações sintoma-doença — este CSV cumpre esse requisito com 20 combinações e 4 colunas de sintomas.

| Propriedade | Valor |
|-------------|-------|
| Formato | CSV, UTF-8, separador vírgula |
| Linhas | 20 (+ 1 cabeçalho) |
| Colunas | sintoma_1, sintoma_2, sintoma_3, sintoma_4, doenca_associada |

O CSV é uma projeção simplificada do JSON — o motor de inferência do `cardio_extrator` consome o JSON (que contém pesos, bônus e condições compostas), não o CSV. O CSV existe como entregável do enunciado e como referência tabulada para consulta rápida.

---

## visuais/

Contém imagens de exames cardiológicos para a Parte 3 (Dados Visuais/VC) do projeto. As imagens foram obtidas de datasets públicos do Kaggle e renomeadas com padrão descritivo para facilitar o carregamento por pipelines de Visão Computacional.

### ecg/

Imagens de eletrocardiogramas (ECG) de 12 derivações em formato PNG.

| Metadado | Valor |
|----------|-------|
| Diretório | `data/visuais/ecg/` |
| Total de imagens | 50 |
| Formato | PNG |
| Origem | Kaggle - [ECG Dataset](https://www.kaggle.com/datasets/ankurray00/ecg-dataset) (ankurray00) |
| Licença | CC-BY-NC-SA-4.0 |

#### Distribuição por classe

| Classe | Prefixo | Quantidade | Descrição |
|--------|---------|------------|-----------|
| Normal | `ecg_normal_` | 17 | ECG de paciente saudável, sem alterações de ritmo ou morfologia |
| Arritmia | `ecg_arritmia_` | 17 | ECG com batimento cardíaco anormal (Abnormal Heartbeat) |
| Infarto | `ecg_infarto_` | 16 | ECG com histórico de infarto do miocárdio (History of MI) |

#### Convenção de nomes

Os arquivos originais seguiam o padrão do dataset Kaggle (`Normal(25).png`, `HB_(120).png`, `PMI_(102).png`). Foram renomeados para o padrão `ecg_{classe}_{NNN}.png` onde `{classe}` indica o diagnóstico em pt-BR e `{NNN}` é a numeração sequencial com zero-padding.

| Nome original | Nome renomeado | Classe |
|---------------|----------------|--------|
| `Normal(*)` | `ecg_normal_001.png` ... `ecg_normal_017.png` | Normal Person |
| `HB_(*)` | `ecg_arritmia_001.png` ... `ecg_arritmia_017.png` | Abnormal Heartbeat |
| `PMI_(*)` | `ecg_infarto_001.png` ... `ecg_infarto_016.png` | History of MI |

#### Relevância clínica

O eletrocardiograma é o exame complementar mais solicitado na prática cardiológica. A interpretação automatizada de ECGs por algoritmos de Visão Computacional pode:

- Detectar arritmias em tempo real em dispositivos de monitoramento contínuo (IoT)
- Identificar sinais precoces de infarto agudo do miocárdio em unidades de emergência
- Auxiliar na triagem de pacientes em regiões com escassez de cardiologistas

As três classes presentes no dataset (normal, arritmia, infarto) representam os diagnósticos mais frequentes e clinicamente relevantes na eletrocardiografia, permitindo treinar modelos de classificação multiclasse.

### raio_x_toracico/

Imagens de raio-X torácico posteroanterior (PA) em formatos JPEG, JPG e PNG.

| Metadado | Valor |
|----------|-------|
| Diretório | `data/visuais/raio_x_toracico/` |
| Total de imagens | 50 |
| Formatos | JPEG, JPG, PNG |
| Origem | Kaggle - [COVID-19 Xray Dataset](https://www.kaggle.com/datasets/khoongweihao/covid19-xray-dataset-train-test-sets) (khoongweihao) |
| Licença | CC0-1.0 (domínio público) |

#### Distribuição por classe

| Classe | Prefixo | Quantidade | Descrição |
|--------|---------|------------|-----------|
| Normal | `rx_normal_` | 25 | Raio-X torácico sem achados patológicos |
| Pneumonia | `rx_pneumonia_` | 25 | Raio-X torácico com pneumonia |

#### Convenção de nomes

Os arquivos originais possuíam nomes não descritivos (UUIDs, referências de artigos). Foram renomeados para o padrão `rx_{classe}_{NNN}.{ext}` onde `{classe}` indica o diagnóstico, `{NNN}` é a numeração sequencial com zero-padding e `{ext}` é a extensão original preservada.

| Diretório de origem | Nome renomeado | Classe |
|---------------------|----------------|--------|
| `train/NORMAL/` | `rx_normal_001` ... `rx_normal_025` | Normal |
| `train/PNEUMONIA/` | `rx_pneumonia_001` ... `rx_pneumonia_025` | Pneumonia |

#### Relevância clínica

O raio-X torácico é o exame de imagem mais acessível e frequente na avaliação cardiopulmonar. A análise automatizada de radiografias torácicas pode:

- Detectar cardiomegalia pela medição do índice cardiotorácico (ICT) via segmentação da silhueta cardíaca
- Identificar congestão pulmonar e derrame pleural, sinais de insuficiência cardíaca descompensada
- Classificar padrões de opacidade pulmonar para diagnóstico diferencial entre causas cardíacas e infecciosas

A distinção entre raios-X normais e com pneumonia exercita técnicas fundamentais de classificação binária de imagens, aplicáveis a qualquer tarefa de diagnóstico por imagem na cardiologia.

### Nomenclatura padronizada

Ambos os subdiretórios seguem o mesmo padrão de nomenclatura:

```
{tipo_exame}_{classe}_{NNN}.{ext}
```

| Componente | Descrição | Exemplos |
|------------|-----------|----------|
| `tipo_exame` | Tipo do exame cardiológico | `ecg`, `rx` |
| `classe` | Diagnóstico clínico em pt-BR | `normal`, `arritmia`, `infarto`, `pneumonia` |
| `NNN` | Numeração sequencial com zero-padding | `001`, `002`, ..., `025` |
| `ext` | Extensão original do arquivo | `png`, `jpeg`, `jpg` |

Essa padronização permite que pipelines de VC extraiam automaticamente a classe (label) a partir do nome do arquivo via parsing de string, eliminando a necessidade de arquivos de anotação externos para tarefas de classificação supervisionada.
