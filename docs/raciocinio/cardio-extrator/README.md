# Raciocínio Técnico: Pipeline de Extração de Sintomas (cardio_extrator)

Documento que expõe decisões e incidentes registrados durante o
desenvolvimento do pacote `scripts/cardio_extrator/` — o pipeline de
extração de sintomas e sugestão diagnóstica da Parte 1 obrigatória da
Fase 2.

## Estrutura

| Capítulo | Arquivo | Conteúdo |
|----------|---------|----------|
| I | [01-validacao-schema-do-mapa.md](01-validacao-schema-do-mapa.md) | Incidente de carregamento do mapa de conhecimento: um `KeyError` críptico em terceiro nível de stack trace virou uma `ValueError` acionável na camada de I/O. Princípio: validar schema na fronteira, não no consumidor. |

## Artefatos relacionados

| Artefato | Caminho | Relação |
|----------|---------|---------|
| Pacote do pipeline | [`scripts/cardio_extrator/`](../../../scripts/cardio_extrator/) | Código de produção coberto pelos capítulos |
| Testes | [`tests/test_extracao.py`](../../../tests/test_extracao.py) | 48 testes automatizados do pipeline |
| Mapa de conhecimento | [`data/textuais/mapa_conhecimento.json`](../../../data/textuais/mapa_conhecimento.json) | Ontologia de doenças, sintomas e regras de scoring |
| Relatos de entrada | [`data/textuais/sintomas_pacientes.txt`](../../../data/textuais/sintomas_pacientes.txt) | 10 frases de pacientes processadas pelo pipeline |
