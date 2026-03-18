# tests

Testes automatizados do pipeline de extração de sintomas cardiovasculares (`cardio_extrator`).

## Como executar

```bash
PYTHONPATH=scripts python -m pytest tests/ -v
```

## Cobertura

O arquivo `test_extracao.py` contém 48 testes organizados em 10 classes. Cada classe valida uma camada ou funcionalidade específica do pipeline, garantindo que refatorações e otimizações não alterem o comportamento clínico do sistema.

### TestNegacao (6 testes)

Valida o motor de negação contextual (`negacao.py`):

| Teste | O que valida |
|-------|-------------|
| `test_negacao_simples` | "Não sinto dor no peito" marca `dor_toracica` como ausente |
| `test_negacao_com_afirmacao` | "Nego dor no peito mas sinto falta de ar" nega dor e confirma dispneia |
| `test_dupla_negacao` | "Não posso negar que sinto um aperto no peito" confirma dor (afirmação) |
| `test_negacao_com_sem` | "Sem queixas de tontura" marca tontura como ausente |
| `test_delimitador_escopo_conjuncao` | Negação não atravessa conjunção "e" entre orações |
| `test_delimitador_escopo_virgula` | Negação não atravessa vírgula entre orações |

### TestTemporal (5 testes)

Valida a extração de atributos temporais (`extratores.py:extrair_temporal`):

| Teste | O que valida |
|-------|-------------|
| `test_inicio_ha_dias` | "há 3 dias" extraído como início |
| `test_inicio_ha_texto` | "Há duas semanas" extraído como início |
| `test_duracao` | "duram vários minutos" extraído como duração |
| `test_progressao_piorando` | "vem piorando" extraído como progressão |
| `test_frequencia` | "Toda noite" extraído como frequência |

### TestScoring (10 testes)

Valida o motor de inferência declarativo (`inferencia.py`):

| Teste | O que valida |
|-------|-------------|
| `test_nova_doenca_sem_alterar_codigo` | Doença fictícia adicionada ao JSON funciona sem mudar Python |
| `test_normalizacao` | Score normalizado entre 0.0 e 1.0 para todos os diagnósticos |
| `test_penalidade_aplicada` | Dor opressiva penaliza score de pericardite |
| `test_avaliador_and` | Operador AND exige todos os critérios verdadeiros |
| `test_avaliador_or` | Operador OR aceita ao menos um critério verdadeiro |
| `test_avaliador_count_ge` | Operador COUNT_GE respeita limiar mínimo |
| `test_avaliador_qualificador` | Avaliação de qualificador via notação ponto |
| `test_avaliador_contexto` | Avaliação de contexto clínico |
| `test_avaliador_fator_risco` | Avaliação de fator de risco |
| `test_fatores_risco_no_scoring` | Fatores de risco incrementam score quando presentes |

### TestNormalizacao (2 testes)

Valida a classificação de confiança:

| Teste | O que valida |
|-------|-------------|
| `test_confianca_baixa` | Score < 0.3 classifica como "baixa" |
| `test_confianca_alta` | Score >= 0.6 classifica como "alta" |

### TestColoquialismo (6 testes)

Valida a robustez do pré-processamento (`preprocessamento.py`):

| Teste | O que valida |
|-------|-------------|
| `test_contracoes_pro` | "vai pro braço" detecta irradiação para MSE |
| `test_contracoes_to` | "Tô sentindo dor no peito" detecta dor torácica |
| `test_normalizacao_espacos` | Múltiplos espaços e tabs normalizados |
| `test_correcao_ortografica` | "dispineia" e "pressao" corrigidos automaticamente |
| `test_dor_com_palavras_intermediarias` | "aperto forte no meio do peito" detecta dor torácica |
| `test_dpn_madrugada` | "acordo de madrugada sem conseguir respirar" detecta DPN |

### TestFatoresRisco (5 testes)

Valida a extração de fatores de risco (`extratores.py:extrair_fatores_risco`):

| Teste | O que valida |
|-------|-------------|
| `test_tabagismo` | "Sou fumante há 20 anos" detecta tabagismo |
| `test_diabetes` | "Tenho diabetes tipo 2" detecta diabetes |
| `test_hipertensao` | "Minha pressão é alta" detecta hipertensão |
| `test_multiplos_fatores` | Detecta tabagismo, diabetes e dislipidemia simultaneamente |
| `test_sem_fatores` | Relato sem fatores retorna dicionário vazio |

### TestMedicacoes (4 testes)

Valida a extração de medicações (`extratores.py:extrair_medicacoes`):

| Teste | O que valida |
|-------|-------------|
| `test_anti_hipertensivo` | "losartana" detectada como anti-hipertensivo |
| `test_estatina` | "atorvastatina" detectada como estatina |
| `test_multiplas_classes` | Detecta anti-hipertensivo, antiplaquetário e estatina juntos |
| `test_sem_medicacoes` | Relato sem medicações retorna dicionário vazio |

### TestSaidaEstruturada (2 testes)

Valida a serialização de resultados (`modelos.py:ResultadoAnalise.to_json`):

| Teste | O que valida |
|-------|-------------|
| `test_resultado_to_json` | Dicionário retornado é serializável em JSON |
| `test_resultado_campos_completos` | Todos os campos do ResultadoAnalise estão presentes e tipados |

### TestRedFlags (5 testes)

Valida a detecção de emergências cardiovasculares (`inferencia.py:avaliar_red_flags`):

| Teste | O que valida |
|-------|-------------|
| `test_ic_descompensada` | Dispneia + edema + ortopneia dispara alerta de IC descompensada |
| `test_sincope_esforco` | Síncope + esforço físico dispara alerta |
| `test_sca_provavel` | Dor opressiva + dispneia dispara alerta de SCA |
| `test_sem_red_flags` | Relato brando não dispara alertas |
| `test_prioridade_urgente` | Todas as red flags possuem prioridade "URGENTE" |

### TestIntegracao (3 testes)

Valida o pipeline completo de ponta a ponta (`pipeline.py:analisar_relato`):

| Teste | O que valida |
|-------|-------------|
| `test_pipeline_10_relatos` | Os 10 relatos originais produzem os diagnósticos esperados na ordem correta |
| `test_diagnostico_correto_dac` | Relato clássico de DAC resulta em DAC como primeiro diagnóstico |
| `test_diagnostico_correto_pericardite` | Relato clássico de pericardite resulta em pericardite como primeiro |

## Por que os testes existem

O pipeline de extração de sintomas toma decisões clínicas — identificar um sintoma incorretamente ou falhar em detectar uma negação pode alterar o diagnóstico sugerido. Os testes garantem que:

1. Refatorações arquiteturais (como a decomposição do God Module em pacote) não alteram comportamento
2. Otimizações de performance (como pré-compilação de regex e busca binária) preservam resultados
3. Cada camada do pipeline funciona isoladamente (testes unitários) e em conjunto (testes de integração)
4. Novos padrões de regex não quebram detecções existentes (regressão)
