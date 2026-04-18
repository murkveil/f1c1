# I. Validação de schema do mapa de conhecimento

## O incidente

Durante uso da CLI do `cardio_extrator`, uma chamada com argumento
incorreto produziu a seguinte saída:

```
$ PYTHONPATH=scripts python -m cardio_extrator --mapa relatos_cardio.json
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "scripts/cardio_extrator/__main__.py", line 5, in <module>
    main()
    ~~~~^^
  File "scripts/cardio_extrator/cli.py", line 93, in main
    scores_maximos = pre_calcular_scores_maximos(mapa)
  File "scripts/cardio_extrator/inferencia.py", line 113, in pre_calcular_scores_maximos
    chave: _calcular_score_maximo(config.get("scoring", {}))
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "scripts/cardio_extrator/inferencia.py", line 94, in _calcular_score_maximo
    cfg["peso_base"] for cfg in scoring["sintomas"].values()
                                ~~~~~~~^^^^^^^^^^^^
KeyError: 'sintomas'
```

A causa direta: o argumento `--mapa relatos_cardio.json` passou ao CLI
um arquivo que **não é o mapa de conhecimento**. O `relatos_cardio.json`
é um arquivo de **saída** do próprio `cardio_extrator` — um JSON com
estrutura `{meta, resultados}` contendo relatos já processados. O mapa
de conhecimento real vive em `data/textuais/mapa_conhecimento.json` e
tem estrutura completamente diferente: `{doenca: {scoring: {sintomas:
...}}}`.

## Por que a mensagem de erro era ruim

Embora o erro de uso tenha sido legítimo (arquivo errado), a mensagem
produzida **não ajuda** a diagnosticar:

1. **Três frames de stack trace entre o erro e o ponto de uso.** O
   `KeyError` disparou dentro de uma comprehension aninhada
   (`_calcular_score_maximo`), chamada por outra comprehension
   (`pre_calcular_scores_maximos`), chamada por `main()`.
2. **A mensagem é `KeyError: 'sintomas'`.** Nenhum contexto sobre
   qual arquivo estava sendo processado, qual é o schema esperado,
   ou o que o usuário fez de errado.
3. **O erro aparece longe da causa.** O arquivo foi carregado com
   sucesso em `carregar_mapa()` — só três chamadas depois, ao tentar
   iterar campos que o arquivo errado não tem, a validação implícita
   falha.

Um usuário confrontado com esse stack trace precisa: inspecionar o
código-fonte de três arquivos, entender o que é `scoring.sintomas`,
correlacionar com o arquivo passado, e deduzir que o arquivo está no
formato errado. Para um uso operacional (passar um arquivo em um
comando), isso é fricção inaceitável.

## Diagnóstico do anti-padrão

A raiz do problema está em `scripts/cardio_extrator/io.py`, na função
`carregar_mapa()`. Antes da correção, ela era:

```python
def carregar_mapa(caminho: Path) -> dict:
    """Carrega o mapa de conhecimento JSON."""
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)
```

Essa implementação trata o carregamento como **transporte de bytes**:
lê o arquivo, parseia JSON, retorna qualquer coisa que parseie com
sucesso. Não há verificação de que o JSON retornado corresponde ao
contrato semântico esperado pelo resto do pacote (um mapa com
configurações de doença contendo `scoring.sintomas`).

O resultado: a validação é feita *de facto* pelos consumidores, através
de falhas de acesso a campos. Cada função downstream que toca o mapa
acaba sendo um ponto potencial de erro críptico — cada uma ataca uma
parte diferente do schema, cada uma falha com uma mensagem diferente.

Esse é um anti-padrão clássico: **validação implícita espalhada pela
pilha de chamadas**. A correção canônica é centralizar a validação na
fronteira de I/O.

## A correção aplicada

Foi introduzida uma função `_validar_estrutura_mapa()` chamada
imediatamente após o `json.load()` em `carregar_mapa()`:

```python
def carregar_mapa(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    _validar_estrutura_mapa(dados, caminho)
    return dados


def _validar_estrutura_mapa(dados: object, caminho: Path) -> None:
    if not isinstance(dados, dict):
        raise ValueError(
            f"Arquivo {caminho} não contém um mapa de conhecimento "
            f"válido: esperado objeto JSON no topo, encontrado "
            f"{type(dados).__name__}.",
        )

    chaves_doenca = [k for k in dados if k not in _CHAVES_META_MAPA]
    if not chaves_doenca:
        raise ValueError(
            f"Arquivo {caminho} não contém nenhuma doença: todas as "
            f"chaves ({sorted(dados)}) são metadados. Verifique se o "
            f"arquivo é o mapa de conhecimento (ex.: "
            f"data/textuais/mapa_conhecimento.json) e não uma saída "
            f"do próprio cardio_extrator.",
        )

    for chave in chaves_doenca:
        config = dados[chave]
        if not isinstance(config, dict) or "scoring" not in config or \
                "sintomas" not in config.get("scoring", {}):
            raise ValueError(
                f"Arquivo {caminho} não é um mapa de conhecimento "
                f"válido: chave '{chave}' não tem a estrutura esperada "
                f"`scoring.sintomas`. Confirme que está passando o "
                f"arquivo correto via --mapa (ex.: "
                f"data/textuais/mapa_conhecimento.json).",
            )
```

A constante `_CHAVES_META_MAPA = {"intersecoes", "ambiguidades_clinicas",
"red_flags"}` delimita chaves legítimas de metadado — o resto é
considerado chave de doença e validado pelo schema esperado.

## Comparação antes × depois

**Antes** — a mesma chamada incorreta com o arquivo errado:

```
File "scripts/cardio_extrator/inferencia.py", line 94, in _calcular_score_maximo
    cfg["peso_base"] for cfg in scoring["sintomas"].values()
                                ~~~~~~~^^^^^^^^^^^^
KeyError: 'sintomas'
```

Três frames de distância, mensagem de uma palavra, sem contexto.

**Depois** — mesma chamada, comportamento após o fix:

```
File "scripts/cardio_extrator/io.py", line 62, in _validar_estrutura_mapa
    raise ValueError(
    ...<4 lines>...
    )
ValueError: Arquivo relatos_cardio.json não é um mapa de conhecimento
válido: chave 'meta' não tem a estrutura esperada `scoring.sintomas`.
Confirme que está passando o arquivo correto via --mapa
(ex.: data/textuais/mapa_conhecimento.json).
```

Um frame, mensagem que nomeia o arquivo, identifica o campo ausente e
sugere a correção.

## Princípio extraído

**Schema é contrato. Contratos devem ser verificados onde os dados
entram no sistema.**

Três consequências práticas:

1. **Carregadores não carregam — eles validam e carregam.** Qualquer
   função `carregar_X(caminho)` tem duas responsabilidades indivisíveis:
   obter os bytes e verificar que eles formam um X.

2. **Mensagens de erro nomeiam o arquivo, nomeiam o campo, apontam a
   correção.** O usuário que comete um erro de uso deve ter, na
   primeira linha da mensagem, informação suficiente para corrigir
   sozinho. Caminhos absolutos, nomes de campos, sugestões de valores
   canônicos.

3. **`KeyError` e `AttributeError` profundos são sintomas de que a
   validação está espalhada.** Se o primeiro erro vindo de um input
   inválido está em um detalhe de implementação (comprehension
   aninhada, método de biblioteca), a validação foi deixada para tarde
   demais.

## Cobertura de testes

Os 48 testes em `tests/test_extracao.py` continuam passando após a
introdução do validador. O validador é chamado indiretamente em toda
execução do pipeline, então testes de integração que carregam o mapa
real validam automaticamente o caminho feliz. Testes específicos para
mensagens de erro sob inputs inválidos não foram adicionados — o
custo-benefício de manter esses testes excede o valor para este projeto
acadêmico, dado que a regressão ficaria visível na primeira execução
que disparasse o caminho inválido.

## Referências

- Código corrigido: [`scripts/cardio_extrator/io.py`](../../../scripts/cardio_extrator/io.py)
- Função validadora: `_validar_estrutura_mapa()` (privada ao módulo)
- Constante de metadados: `_CHAVES_META_MAPA`
- Mapa de referência: [`data/textuais/mapa_conhecimento.json`](../../../data/textuais/mapa_conhecimento.json)
