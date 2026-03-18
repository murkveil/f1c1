# cardio_extrator

Pacote Python para extração de sintomas cardiovasculares e sugestão de diagnósticos a partir de relatos de pacientes em linguagem natural.

## Fluxo do pipeline

```
relato (texto livre em pt-BR)
    |
    v
[preprocessamento.py] normalizar()
    |  minúsculo + contrações + correções ortográficas
    v
[negacao.py] _tokenizar()
    |  tokens com posições para busca binária
    v
[extratores.py] extrair_sintomas()
    |  regex pré-compilados -> AchadoClinico por sintoma
    |  |
    |  +--[negacao.py] detectar_negacao()
    |        janela de tokens + bisect + delimitadores de escopo
    v
[extratores.py] extrair_qualificadores()
    |  tipo de dor, irradiação, fatores de alívio/piora
    v
[extratores.py] extrair_contexto()
    |  pródromo viral, histórico familiar, esforço físico
    v
[extratores.py] extrair_temporal()
    |  início, duração, frequência, progressão
    v
[extratores.py] extrair_fatores_risco()
    |  tabagismo, diabetes, hipertensão, dislipidemia, obesidade, sedentarismo
    v
[extratores.py] extrair_medicacoes()
    |  7 classes farmacológicas
    v
[inferencia.py] pontuar_doencas()
    |  scoring declarativo: pesos + bônus + penalidades + normalização 0-1
    v
[inferencia.py] avaliar_red_flags()
    |  5 alertas de emergência cardiovascular
    v
ResultadoAnalise (dataclass com todos os achados)
    |
    +--[formatacao.py] formatar_resultado()  -> texto humano
    +--[modelos.py] .to_json()               -> dict serializável
```

## Decisões arquiteturais

### Por que regex e não modelo de linguagem

Sistemas clínicos de apoio à decisão exigem que cada conclusão diagnóstica seja rastreável a uma regra explícita. Modelos de linguagem (LLMs) ou bibliotecas como spaCy produzem resultados não-determinísticos — o mesmo relato pode gerar diagnósticos diferentes em execuções consecutivas. O pipeline utiliza regex pré-compilados que garantem determinismo absoluto: o mesmo input produz exatamente o mesmo output, sempre. A alternativa de usar spaCy ou Stanza adicionaria ~500MB de dependências, exigiria modelo de língua portuguesa e tornaria impossível auditar por que o sistema detectou (ou não) um sintoma específico.

### Por que scoring declarativo via JSON e não if/elif hardcoded

A versão inicial do motor de scoring continha ~120 linhas de if/elif com lógica de pontuação embutida por doença. Cada nova doença exigia alterar o código Python. O JSON declarativo separa dados (pesos, regras, condições) de lógica (motor de avaliação). O motor genérico `avaliar_condicao()` suporta operadores AND, OR e COUNT_GE sobre sintomas, qualificadores, contextos e fatores de risco. Adicionar uma nova doença requer apenas editar `mapa_conhecimento.json` — zero alteração em código Python. A alternativa de manter if/elif violaria o princípio Open/Closed e tornaria o sistema frágil à medida que o número de doenças crescesse.

### Por que motor de negação próprio e não biblioteca pronta

Bibliotecas como NegEx e pyConTextNLP foram projetadas para inglês clínico. O português clínico possui particularidades que essas ferramentas não cobrem: contrações coloquiais ("não tô sentindo"), delimitadores de escopo por conjunção ("não tenho dor no peito, e sinto falta de ar" — o "e" inicia nova oração), dupla negação como afirmação ("não posso negar que sinto"), e restauradores ("nego dor, mas recentemente voltou"). O motor próprio implementa janela de tokens com busca binária (bisect), delimitadores configuráveis e tratamento explícito de dupla negação, com controle granular impossível de obter adaptando uma biblioteca anglófona.

### Por que Python puro sem dependências externas

O contexto acadêmico exige que o projeto funcione em qualquer ambiente Python 3.11+ sem instalação de pacotes. O código de produção utiliza exclusivamente a biblioteca padrão (`re`, `json`, `csv`, `pathlib`, `bisect`, `argparse`, `logging`, `dataclasses`). A única dependência externa é `pytest`, utilizada apenas para testes. A alternativa de usar pandas, scikit-learn ou NLTK para tarefas que a stdlib resolve adicionaria complexidade de instalação sem benefício funcional.

## Como adicionar uma nova doença

Editar `data/textuais/mapa_conhecimento.json` adicionando uma entrada com a seguinte estrutura:

```json
{
  "nome_da_doenca": {
    "nome_exibicao": "Nome para Exibição",
    "sigla": "SGL",
    "scoring": {
      "sintomas": {
        "dor_toracica": { "peso_base": 1.0 },
        "dispneia": { "peso_base": 0.8 }
      },
      "regras_bonificacao": [
        {
          "condicao": { "qualificador": "dor_toracica.tipo_opressiva" },
          "bonus": 0.5,
          "justificativa": "Razão clínica documentada"
        }
      ],
      "regras_exclusao": [],
      "fatores_risco": { "tabagismo": 0.3 }
    }
  }
}
```

Nenhum arquivo Python precisa ser alterado. O motor de scoring avalia automaticamente a nova doença contra os achados extraídos.

## Como adicionar um novo sintoma

1. Editar `vocabulario/sintomas.py` adicionando a entrada ao dicionário:

```python
"novo_sintoma": [
    re.compile(r"expressão\s+regex\s+do\s+sintoma"),
    re.compile(r"variação\s+coloquial"),
],
```

2. Adicionar o novo sintoma às seções `scoring.sintomas` das doenças relevantes em `mapa_conhecimento.json`.

## Módulos

| Módulo | Responsabilidade | Linhas |
|--------|-----------------|--------|
| `modelos.py` | Dataclasses de domínio (AchadoClinico, ScoreDiagnostico, AlertaRedFlag, ResultadoAnalise) | 71 |
| `preprocessamento.py` | Normalização, contrações coloquiais, correções ortográficas | 76 |
| `negacao.py` | Motor de negação contextual com busca binária | 146 |
| `extratores.py` | 7 extratores clínicos (sintomas, qualificadores, contexto, temporal, fatores de risco, medicações, vinculação temporal) | 215 |
| `inferencia.py` | Avaliador de condições declarativas, scoring ponderado, normalização, red flags | 280 |
| `formatacao.py` | Formatação de saída textual | 101 |
| `pipeline.py` | Orquestração: normaliza 1x, tokeniza 1x, chama extratores e inferência | 77 |
| `cli.py` | Interface de linha de comando (argparse, logging, formatos de saída) | 146 |
| `io.py` | Carregamento de JSON e TXT, caminhos padrão | 35 |

### Subpacote vocabulario/

Contém exclusivamente declarações de dicionários com regex pré-compilados. Nenhum módulo possui funções ou imports de lógica — são arquivos de configuração em Python.

| Módulo | Conteúdo |
|--------|----------|
| `sintomas.py` | 22 sintomas cardiovasculares (~5 padrões regex cada) |
| `qualificadores.py` | Qualificadores de dor torácica (10), palpitação (4) e dispneia (2) |
| `contexto.py` | 3 contextos clínicos (pródromo viral, histórico familiar, esforço físico) |
| `fatores_risco.py` | 6 fatores de risco (~4 padrões cada) |
| `medicacoes.py` | 7 classes farmacológicas (~8 medicamentos cada) |
| `temporal.py` | 4 atributos temporais (início, duração, frequência, progressão) |
| `negacao.py` | Negadores (7), restauradores (8), dupla negação (3), janela (5), delimitadores (7) |

Os regex são pré-compilados no carregamento do módulo (`re.compile()`) para evitar lookup no cache interno do `re` a cada chamada — o pipeline executa ~150+ buscas regex por relato, e a pré-compilação reduz o overhead de 0.603ms para 0.163ms por relato (3.7x speedup medido em benchmark de 10.000 relatos).
