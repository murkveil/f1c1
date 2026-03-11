# data

Diretório central de dados do projeto CardioIA. Armazena todos os datasets que alimentam os módulos de Inteligência Artificial nas fases do projeto.

## Estrutura

```
data/
|-- numericos/          # Parte 1 - datasets tabulares (.csv)
|-- textuais/           # Parte 2 - textos médicos (.txt)
|   |-- massa_et_al_2019_prevalencia_dcv_idosos.txt
|   |-- bonotto_et_al_2016_fatores_risco_dcv_mulheres.txt
|-- visuais/            # Parte 3 - imagens de exames cardiológicos (.jpg/.png)
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

O dataset foi projetado para alimentar múltiplos módulos de IA nas fases futuras do CardioIA:

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

---

## visuais/

Reservado para a Parte 3 (Dados Visuais/VC) do projeto. Este diretório armazena imagens de exames cardiológicos (ECGs, angiogramas, raio-X torácico) em formato `.jpg` ou `.png`.

Status: pendente.
