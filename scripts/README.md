# scripts

Scripts standalone para geração e preparação de dados do projeto CardioIA.

## gerar_dados_numericos.py

Gera dataset sintético de pacientes cardiológicos para a Parte 1 (Dados Numéricos/IoT).

### Uso

```bash
python scripts/gerar_dados_numericos.py
```

### Saída

O script grava o arquivo `data/numericos/dataset_cardiologico.csv` com 300 pacientes e 18 variáveis clínicas.

### Variáveis geradas

| Grupo | Variáveis |
|-------|-----------|
| Demográficas | `id_paciente`, `idade`, `sexo` |
| Sinais vitais | `pressao_arterial_sistolica`, `pressao_arterial_diastolica`, `frequencia_cardiaca` |
| Exames laboratoriais | `colesterol_total`, `colesterol_hdl`, `colesterol_ldl`, `triglicerideos`, `glicemia_jejum` |
| Indicadores clínicos | `diabetes`, `imc` |
| Histórico e hábitos | `tabagismo`, `atividade_fisica`, `historico_familiar_cardiaco` |
| Sintomas e diagnóstico | `tipo_dor_toracica`, `sintomas`, `doenca_cardiaca` |

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

O script utiliza seed fixa (`SEED = 42`) para garantir que execuções repetidas produzam o mesmo dataset.

| Propriedade | Valor |
|-------------|-------|
| Arquivo | `data/numericos/dataset_cardiologico.csv` |
| Linhas | 300 (+ 1 cabeçalho) |
| Colunas | 18 |
| Seed | 42 |
| MD5 | `37494bc27300a66b716dd2ca10d2133f` |

Para verificar a integridade após gerar o dataset:

```bash
md5sum data/numericos/dataset_cardiologico.csv
```

### Dependências

Nenhuma. O script utiliza apenas a biblioteca padrão do Python 3 (`csv`, `random`, `pathlib`).
