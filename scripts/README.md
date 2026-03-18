# scripts

Scripts e pacotes para geração e análise de dados do projeto CardioIA.

## Estrutura

```
scripts/
|-- gerar_dados_numericos.py        # Fase 1 - gerador do dataset sintético
|-- extracao_sintomas.py            # wrapper depreciado (re-exports para cardio_extrator)
|-- cardio_extrator/                # Fase 2 - pacote de extração de sintomas
|   |-- __init__.py                 # exports públicos (analisar_relato, carregar_mapa, modelos)
|   |-- cli.py                      # interface de linha de comando
|   |-- pipeline.py                 # orquestração do pipeline
|   |-- preprocessamento.py         # normalização de texto
|   |-- negacao.py                  # motor de negação contextual
|   |-- extratores.py               # 7 extratores clínicos
|   |-- inferencia.py               # motor de scoring declarativo
|   |-- formatacao.py               # formatação de saída textual
|   |-- modelos.py                  # dataclasses de domínio
|   |-- io.py                       # carregamento de dados
|   |-- vocabulario/                # subpacote de regex pré-compilados
|   |   |-- sintomas.py, qualificadores.py, contexto.py, fatores_risco.py,
|   |   |-- medicacoes.py, temporal.py, negacao.py
```

---

## gerar_dados_numericos.py

O script gera o dataset sintético de pacientes cardiológicos para a Fase 1 (Dados Numéricos/IoT).

### Uso

```bash
python scripts/gerar_dados_numericos.py
```

### Saída

O script grava o arquivo `data/numericos/dataset_cardiologico.csv` com 300 pacientes e 18 variáveis clínicas.

### Correlações clínicas

O script aplica correlações entre fatores de risco para produzir dados clinicamente coerentes:

- A idade eleva a pressão arterial sistólica em 0.6 mmHg por ano acima de 25
- O tabagismo adiciona 15 mg/dL ao colesterol total basal
- Mulheres recebem colesterol HDL basal de 55 mg/dL; homens, 45 mg/dL
- A ausência de atividade física eleva o IMC basal de 26.5 para 29.0
- O IMC eleva a glicemia de jejum em 2.5 mg/dL por ponto acima de 22
- A atividade física reduz a frequência cardíaca basal de 75 para 65 bpm

A função `calcular_risco()` acumula incrementos de probabilidade para cada fator presente e o resultado determina a presença de doença cardíaca. O teto de risco é 0.95.

### Reprodutibilidade

| Propriedade | Valor |
|-------------|-------|
| Seed | 42 |
| Linhas | 300 (+ 1 cabeçalho) |
| Colunas | 18 |
| MD5 | `37494bc27300a66b716dd2ca10d2133f` |

### Dependências

Nenhuma. O script utiliza apenas a biblioteca padrão do Python 3 (`csv`, `random`, `pathlib`).

---

## extracao_sintomas.py

Wrapper de retrocompatibilidade que re-exporta todos os símbolos públicos do pacote `cardio_extrator`. Imports deste módulo emitem `DeprecationWarning` orientando migração para o pacote.

O módulo existia originalmente como arquivo monolítico (~1450 linhas) com 8 responsabilidades distintas. A refatoração arquitetural decomôs esse God Module no pacote `cardio_extrator/` com 10 módulos e 7 arquivos de vocabulário. O wrapper preserva compatibilidade com código que importa diretamente de `extracao_sintomas` enquanto sinaliza migração gradual.

```python
# depreciado
from extracao_sintomas import extrair_sintomas  # emite DeprecationWarning

# recomendado
from cardio_extrator.extratores import extrair_sintomas
```

---

## cardio_extrator/

Pacote Python modular para extração de sintomas cardiovasculares e sugestão de diagnósticos a partir de relatos de pacientes em linguagem natural. A documentação completa do pacote (arquitetura, decisões de design, como estender) está em [`cardio_extrator/README.md`](cardio_extrator/README.md).

### Uso rápido

```bash
# saída textual
PYTHONPATH=scripts python -m cardio_extrator.cli

# saída JSON
PYTHONPATH=scripts python -m cardio_extrator.cli --formato json

# arquivo de saída com logging
PYTHONPATH=scripts python -m cardio_extrator.cli --formato ambos --saida resultado --log INFO
```

### Argumentos da CLI

| Argumento | Valores | Padrão | Descrição |
|-----------|---------|--------|-----------|
| `--formato` | `texto`, `json`, `ambos` | `texto` | Formato de saída |
| `--saida` | caminho | stdout | Arquivo de saída (`.txt` e/ou `.json`) |
| `--log` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `WARNING` | Nível de logging (emitido em stderr) |
| `--relatos` | caminho | `data/textuais/sintomas_pacientes.txt` | Arquivo de relatos |
| `--mapa` | caminho | `data/textuais/mapa_conhecimento.json` | Arquivo do mapa de conhecimento |

### API Python

```python
from cardio_extrator import analisar_relato, carregar_mapa
from cardio_extrator.io import ARQUIVO_MAPA

mapa = carregar_mapa(ARQUIVO_MAPA)
resultado = analisar_relato("Sinto dor no peito há 3 dias", mapa)

print(resultado.diagnosticos[0].nome_exibicao)  # Doença Arterial Coronariana
print(resultado.to_json())                       # dict serializável
```
