# Estratégia de Compilação de Expressões Regulares

Documento técnico sobre a arquitetura de regex pré-compilados do pacote `cardio_extrator`. O pacote acumula **197 chamadas `re.compile()`** distribuídas em 9 módulos Python, com **233 padrões lógicos** (agrupados por domínio clínico), todos compilados em tempo de importação.

---

## 1. Por que `re.compile()` em tempo de importação

### O que o CPython faz ao executar `re.compile(pattern)`

O módulo `re` delega a compilação para `sre_compile.compile()`, que executa duas fases. Na fase de parsing, o parser `sre_parse` converte a string do padrão em uma árvore de nós (sequência de opcodes SRE — `LITERAL`, `BRANCH`, `REPEAT`, `SUBPATTERN`, etc.). Na fase de compilação, `sre_compile._code()` transforma essa árvore em bytecode compacto que o motor SRE do CPython (implementado em C no módulo `_sre`) consome diretamente. O resultado é um objeto `re.Pattern` alocado na heap, que encapsula o bytecode e expõe os métodos `.search()`, `.match()`, `.finditer()` e `.sub()`. Esses métodos executam apenas a fase de matching — o bytecode já existe pronto na memória.

### O que o CPython faz ao executar `re.search(pattern_string, text)` sem pré-compilação

O módulo `re` intercepta a chamada e verifica se `pattern_string` já existe no cache interno (`re._cache`, implementado como `dict` limitado a `re._MAXCACHE = 512` entradas no CPython 3.11+). Se a chave `(pattern_string, flags)` existe no cache, o `re` recupera o objeto `Pattern` e executa o matching diretamente. Se não existe, o `re` executa todo o ciclo de compilação (parsing + geração de bytecode + alocação do `Pattern`) e armazena o resultado no cache. Quando o cache atinge 512 entradas, o CPython aplica uma política de flush completo — esvazia o dicionário inteiro e recomeça. O cache **não** implementa LRU, LFU ou qualquer política de evicção granular.

### Por que o cache interno do `re` não basta para este projeto

O CardioIA acumula 233 padrões lógicos (197 chamadas `re.compile()` diretas nos módulos de vocabulário e preprocessamento, mais padrões compostos que agregam sub-padrões). Os 197 slots individuais cabem em 512 entradas, mas qualquer outro código Python no mesmo processo (frameworks web, bibliotecas de logging, código de terceiros) compete pelo mesmo cache global. Uma única biblioteca que registre 320+ padrões próprios empurraria o cache para o limite de 512, desencadeando flush e forçando a re-compilação de todos os padrões clínicos no próximo uso. A pré-compilação explícita elimina essa dependência de estado global compartilhado: cada padrão existe como atributo de módulo referenciado permanentemente, imune a evicção.

### Trade-off de memória vs CPU

A compilação em tempo de importação aloca 197 objetos `Pattern` permanentes na heap. Cada `Pattern` contém o bytecode SRE compacto — para padrões típicos do projeto (20-80 caracteres de source), o bytecode ocupa centenas de bytes a poucos kilobytes. O custo total de memória permanente fica abaixo de 200 KB (197 objetos × ~1 KB médio). O ganho de CPU compensa esse custo: o pipeline processa cada relato executando até ~150 chamadas `.search()` que resolvem em tempo de matching puro, sem overhead de lookup no cache global nem risco de re-compilação. No benchmark de 10.000 relatos, a pré-compilação contribui para um throughput de 0.163ms por relato (3.7x mais rápido que a versão sem pré-compilação).

### Determinismo e auditabilidade clínica

Padrões compilados como constantes de módulo formam um inventário estático e inspecionável. Um auditor clínico abre `vocabulario/sintomas.py` e verifica exatamente quais expressões o sistema reconhece como "dor torácica" (9 padrões) ou "dispneia" (5 padrões). A alternativa de construir padrões dinamicamente em runtime (via configuração externa ou geração de código) ocultaria o inventário real atrás de caminhos de execução condicionais, impossibilitando auditoria estática.

---

## 2. Inventário completo de padrões por módulo

### `vocabulario/sintomas.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/sintomas.py` |
| Padrões `re.compile()` | 78 |
| Estrutura | `dict[str, list[re.Pattern[str]]]` |
| Chaves (sintomas canônicos) | 21 |
| Consumido por | `extratores.py:extrair_sintomas()` |

O módulo mapeia 21 sintomas cardiovasculares canônicos para listas de variantes lexicais. Cada chave do dicionário representa o nome interno do sintoma (ex: `dor_toracica`, `dispneia`), e cada lista contém os padrões regex que detectam esse sintoma em texto livre.

Distribuição de padrões por sintoma:

| Sintoma | Padrões | Exemplos de expressões detectadas |
|---------|---------|-----------------------------------|
| `dor_toracica` | 9 | "dor forte no peito", "aperto no tórax", "desconforto precordial" |
| `dispneia` | 5 | "falta de ar", "dificuldade para respirar", "sufocamento" |
| `ortopneia` | 3 | "falta de ar ao deitar", "preciso usar travesseiros" |
| `dispneia_paroxistica_noturna` | 3 | "acordo no meio da noite com falta de ar" |
| `edema_membros_inferiores` | 3 | "pernas inchadas", "edema bilateral" |
| `fadiga` | 6 | "cansaço constante", "fraqueza", "astenia" |
| `palpitacao` | 5 | "palpitações", "coração disparado", "batimentos irregulares" |
| `sincope` | 4 | "desmaiei", "perda de consciência", "síncope" |
| `tontura` | 5 | "tontura", "vertigem", "escurecimento da visão" |
| `cefaleia` | 3 | "dor de cabeça", "cefaleia", "enxaqueca" |
| `febre` | 3 | "febre", "febril", "temperatura elevada" |
| `tosse_seca_noturna` | 3 | "tosse seca noturna", "tosse à noite" |
| `nocturia` | 3 | "urinando à noite", "noctúria" |
| `nausea` | 3 | "náusea", "enjoo", "vontade de vomitar" |
| `sudorese` | 3 | "suor frio", "sudorese", "transpiração fria" |
| `epistaxe` | 3 | "sangramento nasal", "sangue pelo nariz" |
| `visao_turva` | 2 | "visão embaçada", "enxergar mal" |
| `zumbido` | 3 | "zumbido", "chiado no ouvido" |
| `mialgia` | 3 | "dor muscular", "mialgia", "corpo doendo" |
| `distensao_abdominal` | 3 | "barriga inchada", "distensão abdominal" |
| `confusao_mental` | 3 | "confusão mental", "desnorteado" |

### `vocabulario/qualificadores.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/qualificadores.py` |
| Padrões `re.compile()` | 27 |
| Estrutura | `dict[str, dict[str, list[re.Pattern[str]]]]` |
| Sintomas qualificados | 3 (`dor_toracica`, `palpitacao`, `dispneia`) |
| Qualificadores totais | 16 |
| Consumido por | `extratores.py:extrair_qualificadores()` |

A estrutura possui dois níveis de aninhamento: o primeiro nível indexa pelo sintoma, o segundo pelo qualificador semiológico. Cada qualificador contém os padrões regex que o detectam.

Qualificadores de `dor_toracica` (10):

| Qualificador | Padrões | Detecta |
|-------------|---------|---------|
| `tipo_opressiva` | 6 | "aperto", "opressão", "pressão", "peso", "constritiva", "sufocante" |
| `tipo_pleuritica` | 4 | "aguda", "pontada", "lancinante", piora com respiração |
| `irradiacao_mse` | 2 | irradiação para braço esquerdo / MSE |
| `irradiacao_mandibula` | 1 | irradiação para mandíbula |
| `irradiacao_trapezio` | 1 | irradiação para trapézio / ombro |
| `piora_esforco` | 2 | piora durante esforço / exercício / caminhada |
| `piora_respiracao` | 2 | piora com respiração / inspiração |
| `piora_decubito` | 2 | piora ao deitar / em decúbito |
| `alivio_repouso` | 1 | alívio com repouso / descanso / parar |
| `alivio_inclinado` | 2 | alívio ao inclinar / sentar para frente |

Qualificadores de `palpitacao` (4): `irregular`, `inicio_subito`, `precipitante_cafe`, `precipitante_estresse`.

Qualificadores de `dispneia` (2): `aos_esforcos`, `ao_deitar`.

### `vocabulario/contexto.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/contexto.py` |
| Padrões `re.compile()` | 6 |
| Estrutura | `dict[str, list[re.Pattern[str]]]` |
| Chaves | 3 |
| Consumido por | `extratores.py:extrair_contexto()` |

| Contexto | Padrões | Detecta |
|----------|---------|---------|
| `prodomo_viral` | 2 | "depois de uma gripe", "pródromo viral" |
| `historico_familiar_morte_subita` | 3 | "pai faleceu de morte súbita", "irmão tem doença no coração" |
| `esforco_fisico` | 1 | "ao esforço", "durante exercício", "quando corro" |

### `vocabulario/fatores_risco.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/fatores_risco.py` |
| Padrões `re.compile()` | 21 |
| Estrutura | `dict[str, list[re.Pattern[str]]]` |
| Chaves (fatores) | 6 |
| Consumido por | `extratores.py:extrair_fatores_risco()` |

| Fator | Padrões | Exemplos |
|-------|---------|----------|
| `tabagismo` | 4 | "fumante", "tabagista", "cigarro" |
| `diabetes` | 4 | "diabetes", "açúcar no sangue alto", "insulina" |
| `hipertensao` | 3 | "pressão alta", "hipertenso" |
| `dislipidemia` | 3 | "colesterol alto", "triglicerídeos altos" |
| `obesidade` | 3 | "obeso", "sobrepeso", "acima do peso" |
| `sedentarismo` | 4 | "sedentário", "não faço exercício" |

### `vocabulario/medicacoes.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/medicacoes.py` |
| Padrões `re.compile()` | 30 |
| Estrutura | `dict[str, list[re.Pattern[str]]]` |
| Classes farmacológicas | 7 |
| Padrões lógicos | 52 |
| Consumido por | `extratores.py:extrair_medicacoes()` |

Nota: o módulo usa nomes genéricos individuais como padrões simples (ex: `re.compile(r"losartana")`), resultando em múltiplas compilações por linha quando separados por vírgula. A contagem de 30 `re.compile()` no arquivo gera 52 padrões lógicos porque várias linhas agrupam 2-3 medicamentos.

| Classe | Padrões | Medicamentos cobertos |
|--------|---------|----------------------|
| `anti_hipertensivo` | 12 | losartana, enalapril, amlodipina, atenolol, captopril, valsartana, nifedipina, metoprolol, propranolol, carvedilol, hidralazina, "remédio da pressão" |
| `anticoagulante` | 9 | varfarina, rivaroxabana, apixabana, dabigatrana, edoxabana, heparina, marevan, xarelto, eliquis |
| `antiplaquetario` | 5 | AAS, aspirina, clopidogrel, ticagrelor, prasugrel |
| `estatina` | 6 | sinvastatina, atorvastatina, rosuvastatina, pravastatina, fluvastatina, "remédio do colesterol" |
| `diuretico` | 6 | furosemida, hidroclorotiazida, espironolactona, indapamida, clortalidona, lasix |
| `antidiabetico` | 9 | metformina, glibenclamida, gliclazida, insulina, glargina, dapagliflozina, empagliflozina, sitagliptina, "remédio do diabetes" |
| `antiarritmico` | 5 | amiodarona, sotalol, propafenona, flecainida, digoxina |

### `vocabulario/negacao.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/negacao.py` |
| Padrões `re.compile()` | 15 |
| Estrutura | 4 listas + 1 constante inteira |
| Padrões lógicos | 25 |
| Consumido por | `negacao.py` (módulo de lógica) |

| Constante | Tipo | Padrões | Função |
|-----------|------|---------|--------|
| `NEGADORES` | `list[re.Pattern]` | 7 | Detecta "não", "nego", "nega", "sem", "nunca", "nenhum(a)", "ausência de" |
| `RESTAURADORES` | `list[re.Pattern]` | 8 | Reverte negação: "mas", "porém", "entretanto", "contudo", "todavia", "no entanto", "agora sim", "recentemente" |
| `DUPLA_NEGACAO` | `list[re.Pattern]` | 3 | Detecta afirmação por negação dupla: "não posso negar", "não nego", "impossível negar" |
| `DELIMITADORES_ESCOPO` | `list[re.Pattern]` | 7 | Encerra escopo de negação: "e", "ou", vírgula, ponto, ponto-e-vírgula, dois-pontos, "que" (exceto "que não") |
| `JANELA_NEGACAO` | `int` | — | Número máximo de tokens entre negador e sintoma (5) |

### `vocabulario/temporal.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/vocabulario/temporal.py` |
| Padrões `re.compile()` | 16 |
| Estrutura | `dict[str, list[re.Pattern[str]]]` |
| Atributos | 4 |
| Consumido por | `extratores.py:extrair_temporal()` |

| Atributo | Padrões | Exemplos de detecção |
|----------|---------|---------------------|
| `inicio` | 5 | "há 3 dias", "desde ontem", "começou há 2 semanas" |
| `duracao` | 4 | "dura 10 minutos", "persistente", "durante 2 horas" |
| `frequencia` | 3 | "toda noite", "2x por semana", "esporádico" |
| `progressao` | 4 | "vem piorando", "melhorando", "estável", "cada vez pior" |

### `preprocessamento.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/preprocessamento.py` |
| Padrões `re.compile()` | 3 |
| Consumido por | `pipeline.py:analisar_relato()` |

| Constante | Padrão fonte | Técnica |
|-----------|-------------|---------|
| `_RE_ESPACOS` | `r"\s+"` | Padrão simples para normalizar whitespace |
| `_PADRAO_CONTRACOES` | 20 sub-padrões unidos por `\|` com grupos capturantes | Padrão composito de alternância |
| `_PADRAO_CORRECOES` | 20 termos unidos por `\|` com word boundaries | Padrão composito de alternância |

### `negacao.py`

| Propriedade | Valor |
|-------------|-------|
| Caminho | `scripts/cardio_extrator/negacao.py` |
| Padrões `re.compile()` | 1 |
| Consumido por | `extratores.py:extrair_sintomas()` via `_tokenizar()` |

| Constante | Padrão | Função |
|-----------|--------|--------|
| `_RE_TOKEN` | `r"\S+"` | Tokeniza texto em sequências de caracteres não-whitespace |

---

## 3. Padrões de construção de regex utilizados

### Word boundaries (`\b`)

O projeto utiliza `\b` nos padrões de negação e pré-processamento para evitar matches parciais em palavras compostas. O motor SRE do CPython define `\b` como a transição entre um caractere `\w` (alfanumérico ou underscore) e um caractere `\W` (ou início/fim da string).

```python
# vocabulario/negacao.py
re.compile(r"\bnão\b")
```

Sem `\b`, o padrão `não` faria match dentro de "canão" ou "panão". Com `\b`, o motor SRE exige que "não" apareça como palavra isolada — precedida e seguida por caractere não-alfanumérico ou limite da string.

O subpacote `vocabulario/sintomas.py` **não** utiliza `\b` na maioria dos padrões porque os padrões de sintomas já incluem contexto suficiente (preposições, espaços obrigatórios via `\s+`) para ancorar o match. O uso de `\b` nos padrões de `medicacoes.py` é seletivo — apenas `\baas\b` utiliza boundaries para evitar que "aas" (ácido acetilsalicílico) faça match dentro de palavras como "baas" ou "vaas".

### Grupos não-capturantes (`(?:...)`)

O projeto utiliza grupos não-capturantes para agrupar alternativas sem poluir `match.groups()`. O motor SRE trata `(?:...)` como agrupamento puro para quantificação ou alternação, sem alocar slot de captura.

```python
# vocabulario/sintomas.py — dor_toracica
re.compile(r"dor\s+(?:\w+\s+){0,3}(?:peito|tórax|torax)")
```

O grupo `(?:\w+\s+){0,3}` permite até 3 palavras intermediárias entre "dor" e "peito/tórax". O grupo `(?:peito|tórax|torax)` agrupa as alternativas sem captura. Se o projeto utilizasse grupos capturantes `(...)`, cada match retornaria grupos extras em `match.groups()` que nenhum código do pipeline consome — desperdício de alocação e fonte de confusão durante depuração.

A exceção proposital está em `preprocessamento.py`, onde `_PADRAO_CONTRACOES` utiliza grupos **capturantes** `(...)`:

```python
# preprocessamento.py
_PADRAO_CONTRACOES = re.compile(
    "|".join(f"({padrao})" for padrao, _ in CONTRACOES)
)
```

Neste caso, a captura é intencional: a função `_substituir_contracao()` itera sobre `m.groups()` para identificar qual sub-padrão fez match e selecionar a substituição correta via índice.

### Quantificadores com janela `{0,N}`

O padrão `(?:\w+\s+){0,N}` é a técnica central para capturar variações naturais da linguagem clínica coloquial. Pacientes inserem palavras intermediárias ao descrever sintomas: "dor **forte no meio do** peito" em vez de "dor no peito".

```python
# vocabulario/sintomas.py — dor_toracica
re.compile(r"aperto\s+(?:\w+\s+){0,4}(?:peito|tórax)")
# Detecta: "aperto no peito", "aperto forte no peito", "aperto forte no meio do peito"
```

O valor de N varia conforme o contexto clínico:
- `{0,2}` para pares próximos: "pressão no peito", "tosse à noite"
- `{0,3}` para a maioria dos sintomas: permite até 3 palavras intermediárias
- `{0,4}` para padrões que toleram descrições mais longas: "aperto forte no meio do peito"
- `{0,5}` para DPN, que requer contexto temporal: "acordo no meio da noite sentindo falta de ar"
- `{0,6}` para histórico familiar, que inclui relações de parentesco e circunstâncias: "pai faleceu de morte súbita aos 45 anos"

A alternativa de usar `.*` (wildcard greedy) em vez de `(?:\w+\s+){0,N}` capturaria matches excessivamente amplos (atravessando frases inteiras) e degradaria a precisão do sistema. A janela delimitada garante que o match permanece dentro de uma janela lexical clinicamente razoável.

### Alternação (`|`)

O projeto utiliza alternação dentro de grupos para cobrir sinônimos clínicos sem duplicar padrões inteiros.

```python
# vocabulario/sintomas.py — dispneia
re.compile(r"dificuldade\s+(?:para|de|em)\s+respirar")
# Cobre: "dificuldade para respirar", "dificuldade de respirar", "dificuldade em respirar"
```

```python
# vocabulario/qualificadores.py — tipo_opressiva
re.compile(r"aperto"), re.compile(r"opressão"), re.compile(r"pressão"), re.compile(r"peso")
```

Para qualificadores simples (palavras isoladas), o projeto utiliza padrões separados em vez de alternação dentro de um único padrão. O motor SRE percorre o texto uma vez por padrão, mas cada padrão simples compila para bytecode mínimo (~4-8 opcodes). A alternativa de consolidar todos os sinônimos em um único padrão `(?:aperto|opressão|pressão|peso|constri\w+|sufoc\w+)` reduziria o número de chamadas `.search()` de 6 para 1 por qualificador, mas adicionaria complexidade de manutenção — cada sinônimo ficaria enterrado dentro de uma alternância longa em vez de visível como entrada separada na lista.

### Classes de caracteres e escapes (`\w`, `\s`, `\S`)

- `\w` — match em `[a-zA-Z0-9_]` mais caracteres Unicode alfanuméricos. No contexto de texto clínico em pt-BR, `\w` captura letras acentuadas (á, é, ç, etc.) porque o CPython implementa `\w` com suporte Unicode por padrão.
- `\s` — match em whitespace (espaço, tab, newline). O pré-processamento normaliza todo whitespace para espaço único antes da extração, garantindo que `\s` sempre corresponde a um espaço simples nos padrões de matching.
- `\S` — match em qualquer caractere que **não** seja whitespace. O tokenizador (`_RE_TOKEN = re.compile(r"\S+")`) utiliza `\S+` para segmentar o texto em tokens que preservam pontuação como tokens independentes — essencial para que vírgulas e pontos funcionem como delimitadores de escopo no motor de negação.

### Padrões compositos via concatenação de strings

O módulo `preprocessamento.py` constrói dois padrões compositos em tempo de importação via concatenação programática de strings.

```python
# _PADRAO_CONTRACOES: une 20 sub-padrões com grupos capturantes
_PADRAO_CONTRACOES = re.compile(
    "|".join(f"({padrao})" for padrao, _ in CONTRACOES)
)
# Resultado: (\bpro\b)|(\bpra\b)|(\btô\b)|... (20 alternativas)
```

O motor SRE compila essa alternância em um autômato que percorre o texto uma única vez, testando todas as 20 alternativas em cada posição. A alternativa de executar 20 chamadas `re.sub()` sequenciais percorreria o texto 20 vezes — complexidade O(20 × n) vs O(n) do padrão composito.

```python
# _PADRAO_CORRECOES: une 20 termos com word boundaries
_PADRAO_CORRECOES = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in CORRECOES_ORTOGRAFICAS) + r")\b"
)
```

A chamada `re.escape()` precede cada termo para neutralizar caracteres especiais de regex. Os termos atuais ("dispineia", "pressao", etc.) não contêm metacaracteres, mas `re.escape()` funciona como defesa preventiva — futuras adições ao dicionário que contenham `.`, `(` ou `+` não introduzirão bugs silenciosos.

### Sufixo wildcard `\w+` e `\w*`

O projeto utiliza radical + wildcard para capturar flexões do português sem enumerar cada conjugação verbal ou variação nominal.

```python
# vocabulario/fatores_risco.py — tabagismo
re.compile(r"(?:sou\s+)?fum(?:o|ante|ava|ei)")
# Captura: "fumo", "fumante", "fumava", "fumei", "sou fumante"
```

```python
# vocabulario/fatores_risco.py — hipertensão
re.compile(r"hipertens\w+")
# Captura: "hipertenso", "hipertensa", "hipertensão", "hipertensivo"
```

O sufixo `\w+` (uma ou mais letras) exige pelo menos um caractere após o radical, evitando match no radical isolado. O sufixo `\w*` (zero ou mais letras) aceita o radical como match completo — usado quando o radical sozinho é uma forma válida.

---

## 4. Arquitetura do subpacote `vocabulario/`

### Por que um subpacote e não um único arquivo

O subpacote `vocabulario/` contém 233 padrões lógicos distribuídos em 7 módulos temáticos. Concentrar todos os padrões em um único arquivo geraria ~400+ linhas de declarações de dicionário sem lógica, onde um desenvolvedor que precisasse ajustar um padrão de "dispneia" teria que navegar por dicionários de medicações, fatores de risco e negação para encontrar a seção correta. A separação por domínio clínico permite que um cardiologista revise `sintomas.py` e `qualificadores.py` sem ser exposto a padrões farmacológicos em `medicacoes.py`. A alternativa de um arquivo único simplificaria imports (um `from vocabulario import *`) mas sacrificaria legibilidade e manutenibilidade por domínio — o trade-off favorece módulos menores e coesos.

### Papel do `__init__.py`

O `vocabulario/__init__.py` re-exporta todas as constantes dos 7 módulos via importações explícitas e `__all__`, criando uma fachada que permite dois estilos de importação igualmente válidos:

```python
# via fachada (usado por extratores.py)
from .vocabulario import EXPRESSOES_SINTOMAS, EXPRESSOES_QUALIFICADORES

# via módulo específico (usado por negacao.py)
from .vocabulario.negacao import NEGADORES, RESTAURADORES
```

O módulo `negacao.py` importa diretamente de `vocabulario.negacao` em vez de usar a fachada porque precisa apenas das constantes de negação — importar via fachada carregaria desnecessariamente os dicionários de medicações e fatores de risco.

### Convenção de nomenclatura

Todas as constantes seguem dois padrões:
- `EXPRESSOES_{DOMÍNIO}` para dicionários que mapeiam termos canônicos a listas de padrões regex (sintomas, qualificadores, contexto, fatores de risco, medicações)
- `PADROES_{DOMÍNIO}` para o dicionário temporal que mapeia atributos a listas de padrões
- `UPPER_SNAKE_CASE` sinaliza imutabilidade por convenção Python (PEP 8) — o dicionário é atribuído uma vez no carregamento do módulo e nunca modificado em runtime

### Tipagem das estruturas

| Estrutura | Tipo | Módulos |
|-----------|------|---------|
| Domínio simples | `dict[str, list[re.Pattern[str]]]` | sintomas, contexto, fatores_risco, medicacoes, temporal |
| Domínio aninhado | `dict[str, dict[str, list[re.Pattern[str]]]]` | qualificadores (sintoma → qualificador → padrões) |
| Listas de padrões | `list[re.Pattern[str]]` | negacao (NEGADORES, RESTAURADORES, DUPLA_NEGACAO, DELIMITADORES_ESCOPO) |

---

## 5. Padrões compositos em `preprocessamento.py`

### `_PADRAO_CONTRACOES`

O módulo `preprocessamento.py` une 20 padrões de contrações coloquiais (`\bpro\b`, `\bpra\b`, `\btô\b`, `\btá\b`, `\bnum\b`, etc.) em um único objeto `re.Pattern` com grupos capturantes indexados:

```python
_PADRAO_CONTRACOES = re.compile(
    "|".join(f"({padrao})" for padrao, _ in CONTRACOES)
)
_SUBST_CONTRACOES = [subst for _, subst in CONTRACOES]
```

O padrão resultante contém 20 alternativas, cada uma dentro de um grupo capturante numerado: `(\bpro\b)|(\bpra\b)|(\bpros\b)|...`. Quando o motor SRE encontra um match, exatamente um grupo contém o texto capturado e os demais retornam `None`. A função `_substituir_contracao()` itera sobre `m.groups()` para identificar o grupo que fez match e retorna a substituição correspondente via `_SUBST_CONTRACOES[i]`.

A alternativa de executar 20 chamadas `_PADRAO_CONTRACOES_N.sub()` sequenciais percorreria o texto 20 vezes (cada `sub` varre o texto inteiro). Para um texto de n caracteres, o custo seria 20n. O padrão composito percorre o texto uma vez: custo n. O speedup teórico é 20x para esta etapa, embora na prática o overhead de alternância no autômato SRE reduza o ganho para ~5-10x (o motor testa cada alternativa em cada posição, mas abandona cedo em caso de mismatch).

### `_PADRAO_CORRECOES`

O módulo une 20 termos com erros ortográficos em um único padrão:

```python
_PADRAO_CORRECOES = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in CORRECOES_ORTOGRAFICAS) + r")\b"
)
```

O padrão resultante é `\b(dispineia|dispinéia|palpitassão|...|coracao)\b`. A substituição utiliza lookup em dicionário via lambda:

```python
texto = _PADRAO_CORRECOES.sub(
    lambda m: CORRECOES_ORTOGRAFICAS[m.group()], texto,
)
```

O `re.escape()` aplica escaping preventivo a cada chave do dicionário. Os termos atuais contêm apenas letras e acentos (seguros para regex), mas `re.escape()` protege contra futuras adições que possam conter metacaracteres como ponto ou parênteses.

### `_RE_ESPACOS`

```python
_RE_ESPACOS = re.compile(r"\s+")
```

O padrão `\s+` normaliza sequências de whitespace (espaços, tabs, newlines) para espaço único. A pré-compilação explícita é redundante do ponto de vista de performance — o cache interno do `re` reteria este padrão trivial indefinidamente. O projeto pré-compila por consistência com a convenção adotada: todos os padrões regex do pacote existem como constantes de módulo, sem exceção. Essa uniformidade elimina a necessidade de avaliar caso a caso se um padrão "merece" pré-compilação.

---

## 6. Interação entre padrões compilados e o motor de negação

### Fluxo completo

1. O `pipeline.py` chama `_tokenizar(texto_norm)` do módulo `negacao.py`, que aplica `_RE_TOKEN.finditer(texto)` para gerar a lista de tokens com posições e o vetor de posições para `bisect_left`.

2. O `extratores.py` itera sobre `EXPRESSOES_SINTOMAS` e chama `padrao.search(texto_norm)` para cada padrão pré-compilado. Quando um padrão faz match, o extrator passa a posição do match (`match.start()`) para `detectar_negacao()`.

3. O motor de negação executa as seguintes verificações, todas usando padrões pré-compilados de `vocabulario/negacao.py`:
   - Verifica `DUPLA_NEGACAO` (3 padrões) na janela de 40 caracteres antes do match. Se algum padrão faz match, o sintoma é afirmado (return False).
   - Busca `NEGADORES` (7 padrões) na fatia de texto antes da posição do match, usando `_idx_token()` com `bisect_left` para localizar tokens em O(log n).
   - Se encontra um negador, verifica `DELIMITADORES_ESCOPO` (7 padrões) no trecho entre o negador e o sintoma. Se algum delimitador faz match, a negação não se aplica.
   - Se não há delimitador, verifica `RESTAURADORES` (8 padrões) no mesmo trecho. Se algum restaurador faz match, a negação é revertida.
   - Se nenhum delimitador nem restaurador interrompe, o sintoma é marcado como negado.

### Por que os padrões de negação residem em `vocabulario/negacao.py` e não em `negacao.py`

O módulo `vocabulario/negacao.py` contém exclusivamente constantes pré-compiladas — 25 objetos `re.Pattern` organizados em 4 listas. O módulo `negacao.py` contém exclusivamente lógica algorítmica — funções que consomem essas constantes para implementar o algoritmo de janela de tokens com busca binária. Essa separação permite que um linguista adicione um novo negador (ex: `re.compile(r"\bjamais\b")`) editando apenas o vocabulário, sem compreender o algoritmo de busca binária, delimitadores de escopo ou janela de tokens.

### `_RE_TOKEN` em `negacao.py`

O padrão `re.compile(r"\S+")` tokeniza o texto em sequências de caracteres não-whitespace. A escolha de `\S+` em vez de `\w+` é deliberada: `\w+` ignora pontuação, colapsando "dor," em "dor" e descartando a vírgula. `\S+` preserva pontuação como parte do token ("dor," permanece como token único) ou como token independente (quando separada por espaço). O pré-processamento normaliza o texto removendo whitespace excessivo, garantindo que pontuação adjacente a palavras (sem espaço) forme um token único. Essa preservação de pontuação é essencial para que vírgulas e pontos funcionem como delimitadores de escopo no motor de negação — o padrão `re.compile(r",")` em `DELIMITADORES_ESCOPO` faz match apenas se a vírgula existe como substring no trecho entre negador e sintoma.

---

## 7. Performance e complexidade

### Tempo de importação

As 197 chamadas `re.compile()` executam durante `import cardio_extrator`. No CPython, a compilação de um padrão regex simples (20-80 caracteres) leva 5-50 microsegundos dependendo da complexidade. Para 197 padrões, o overhead total de importação é da ordem de 2-10 milissegundos — imperceptível para o usuário e amortizado em todas as chamadas subsequentes ao pipeline.

### Tempo de matching por relato

Para cada relato, o pipeline executa até ~150 chamadas `.search()` no caminho típico:
- 78 padrões de sintomas (pior caso: todos os 21 sintomas testam todos os padrões; caso típico: early-exit após o primeiro match por sintoma reduz para ~40-60)
- 35 padrões de qualificadores (apenas para sintomas presentes)
- 6 padrões de contexto
- 21 padrões de fatores de risco
- 52 padrões de medicações (sem early-exit por classe)
- 16 padrões temporais
- Padrões de negação: até 25 por sintoma detectado

Cada `.search()` percorre o texto uma vez — complexidade O(n) no tamanho do texto por padrão. O custo total por relato é O(P × n), onde P é o número de padrões avaliados e n é o comprimento do texto normalizado. Para relatos clínicos curtos (50-300 palavras, ~200-1500 caracteres), este custo é desprezível: benchmark medido em 0.163ms por relato (10.000 relatos).

### Comparação com alternativas

**spaCy/Stanza:** essas bibliotecas oferecem Named Entity Recognition (NER) e dependency parsing que resolveriam extração de sintomas com modelos pré-treinados. O custo é proibitivo para o contexto: ~500 MB de modelos de linguagem como dependência, necessidade de GPU para throughput aceitável em NER, inexistência de modelo pt-BR treinado especificamente em terminologia cardiológica, e violação do requisito acadêmico de zero dependências externas. O projeto teria que treinar um modelo NER customizado com dados anotados — esforço desproporcional ao escopo de uma atividade de Fase 2.

**Aho-Corasick (pyahocorasick):** o algoritmo de Aho-Corasick resolve busca multi-padrão de strings fixas em O(n + m) (n = tamanho do texto, m = total de matches), eliminando o fator P da complexidade. Para os ~50 nomes de medicamentos (strings fixas), Aho-Corasick reduziria as 52 buscas para uma única travessia do texto. O problema: a maioria dos padrões do CardioIA **não** são strings fixas. Padrões como `dor\s+(?:\w+\s+){0,3}(?:peito|tórax|torax)` contêm quantificadores, alternações e wildcards que Aho-Corasick não suporta. A adoção exigiria dividir o vocabulário em padrões fixos (Aho-Corasick) e padrões regex (motor SRE), adicionando complexidade arquitetural e uma dependência externa compilada em C.

**Compilação lazy (compilar no primeiro uso):** compilar padrões sob demanda reduziria o tempo de importação a zero, ao custo de um spike de latência no primeiro relato processado. Em cenário multi-threaded, compilação lazy exigiria sincronização (lock ou `threading.Lock`) para evitar race conditions na inicialização do `Pattern`. O projeto processa relatos sequencialmente na CLI, tornando thread-safety irrelevante — mas a compilação eager em tempo de importação é mais simples, determinística e auditável (o inventário de padrões existe completo após o import, independente de quais caminhos de execução o código percorre).

---

## 8. Extensibilidade

### Adicionar um novo sintoma

Editar `vocabulario/sintomas.py` adicionando uma entrada ao dicionário:

```python
"novo_sintoma": [
    re.compile(r"expressão\s+regex\s+do\s+sintoma"),
    re.compile(r"variação\s+coloquial"),
],
```

O extrator em `extratores.py:extrair_sintomas()` itera automaticamente sobre todas as chaves de `EXPRESSOES_SINTOMAS` — nenhuma alteração de código é necessária. Para que o scoring considere o novo sintoma, adicioná-lo às seções `scoring.sintomas` das doenças relevantes em `mapa_conhecimento.json`.

### Adicionar um novo qualificador

Editar `vocabulario/qualificadores.py` adicionando entrada aninhada sob o sintoma correspondente:

```python
"dor_toracica": {
    "novo_qualificador": [re.compile(r"padrão\s+regex")],
    # qualificadores existentes...
},
```

O extrator `extrair_qualificadores()` itera automaticamente sobre todos os qualificadores de cada sintoma presente.

### Adicionar um novo fator de risco

Editar `vocabulario/fatores_risco.py`:

```python
"novo_fator": [
    re.compile(r"padrão\s+regex"),
],
```

Opcionalmente, adicionar o fator à seção `scoring.fatores_risco` das doenças relevantes em `mapa_conhecimento.json` para que influencie o scoring.

### Adicionar uma nova medicação

Editar `vocabulario/medicacoes.py` sob a classe farmacológica correspondente, ou criar nova classe:

```python
"nova_classe": [
    re.compile(r"nome_generico_1"),
    re.compile(r"nome_generico_2"),
    re.compile(r"nome_comercial"),
],
```

### Adicionar um novo negador

Editar `vocabulario/negacao.py` adicionando à lista `NEGADORES`:

```python
NEGADORES: list[re.Pattern[str]] = [
    # existentes...
    re.compile(r"\bjamais\b"),  # novo negador
]
```

O motor de negação consome a lista inteira via iteração — nenhuma alteração no algoritmo.

### Testar o novo padrão

Adicionar caso de teste em `tests/test_extracao.py` utilizando os helpers `_extrair()` e `_norm()`:

```python
def test_novo_sintoma(self):
    achados = _extrair("Relato que contém o novo sintoma")
    presentes = achados_presentes(achados)
    assert "novo_sintoma" in presentes
```

---

## 9. Tabela-resumo de todos os padrões

| Módulo | Estrutura de dados | Chamadas `re.compile()` | Padrões lógicos | Tipo de match | Consumido por |
|--------|--------------------|------------------------|-----------------|---------------|---------------|
| `vocabulario/sintomas.py` | `dict[str, list[Pattern]]` | 78 | 78 | `.search()` | `extratores.extrair_sintomas` |
| `vocabulario/qualificadores.py` | `dict[str, dict[str, list[Pattern]]]` | 27 | 35 | `.search()` | `extratores.extrair_qualificadores` |
| `vocabulario/contexto.py` | `dict[str, list[Pattern]]` | 6 | 6 | `.search()` | `extratores.extrair_contexto` |
| `vocabulario/fatores_risco.py` | `dict[str, list[Pattern]]` | 21 | 21 | `.search()` | `extratores.extrair_fatores_risco` |
| `vocabulario/medicacoes.py` | `dict[str, list[Pattern]]` | 30 | 52 | `.search()` | `extratores.extrair_medicacoes` |
| `vocabulario/temporal.py` | `dict[str, list[Pattern]]` | 16 | 16 | `.search()` | `extratores.extrair_temporal` |
| `vocabulario/negacao.py` | 4 × `list[Pattern]` + `int` | 15 | 25 | `.finditer()`, `.search()` | `negacao.detectar_negacao` |
| `preprocessamento.py` | 3 constantes `Pattern` | 3 | 3 (+ 20+20 sub-padrões compositos) | `.sub()` | `pipeline.analisar_relato` |
| `negacao.py` | 1 constante `Pattern` | 1 | 1 | `.finditer()` | `negacao._tokenizar` |
| **Total** | | **197** | **237** | | |
