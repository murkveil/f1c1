# I. Construção e rotulação do dataset

## O problema que o dataset resolve

O enunciado exige um arquivo CSV com frases médicas rotuladas como "alto risco"
ou "baixo risco" para treinar um classificador de texto. O dataset não existe
publicamente neste formato — frases clínicas em português brasileiro com rotulação
binária de risco cardiovascular. O engenheiro constrói o dataset manualmente,
definindo critérios explícitos de rotulação antes de escrever a primeira frase.

## Critérios de rotulação

Cada frase recebe um rótulo com base em três critérios clínicos hierárquicos:

**Alto risco** — o rótulo indica que o paciente descrito na frase necessita de
avaliação médica urgente. A frase descreve ao menos um dos seguintes:
- Dor torácica opressiva ou com irradiação (braço esquerdo, mandíbula, trapézio)
- Dispneia aguda (início súbito ou em repouso)
- Síncope (perda de consciência) ou pré-síncope de esforço
- Palpitações com instabilidade hemodinâmica (tontura, quase desmaio)
- Sinais de insuficiência cardíaca descompensada (ortopneia, DPN, edema bilateral)
- Combinação dor torácica + sudorese/náusea (tríade sugestiva de SCA)

**Baixo risco** — o rótulo indica que a queixa descrita não requer avaliação
urgente. A frase descreve ao menos um dos seguintes:
- Dor musculoesquelética com causa mecânica identificável (carregar peso, academia)
- Dor localizada e reprodutível à palpação ("piora quando aperto o local")
- Cansaço fisiológico que resolve com repouso
- Incômodo fugaz (segundos) sem relação com esforço
- Sintomas gastrointestinais (azia, gases, queimação pós-prandial)
- Queixas articulares, respiratórias superiores ou dermatológicas

## Frases ambíguas intencionais (~15-20%)

O dataset inclui 25-30 frases na fronteira de decisão clínica. Essas frases
testam a robustez da fronteira de decisão dos modelos e simulam a incerteza
real da prática clínica. Exemplos:

- "sinto uma dor no peito que aparece quando faço esforço mas não sei se é grave"
  → alto risco (dor torácica desencadeada por esforço satisfaz critério
  Diamond-Forrester para angina típica, independente da percepção subjetiva)

- "tenho palpitações de vez em quando mas não sinto mais nada"
  → baixo risco (palpitações isoladas sem instabilidade hemodinâmica possuem
  baixo valor preditivo positivo para arritmia maligna)

- "sinto uma pressão no peito que vai e vem sem padrão definido"
  → alto risco (desconforto torácico recorrente sem padrão claro exige
  investigação — o critério clínico favorece sensibilidade sobre especificidade)

## Balanceamento 51/49

O dataset contém 81 frases de alto risco (50.6%) e 79 de baixo risco (49.4%).
O balanceamento quase perfeito elimina o viés de classe majoritária: com
distribuição desbalanceada (ex: 80/20), um classificador trivial que sempre prediz
a classe majoritária obteria 80% de acurácia sem aprender nenhum padrão
discriminativo. O balanceamento 50/50 força os modelos a discriminar com base no
conteúdo lexical das frases, não na prevalência de classe.

## Limitações da rotulação

Um único rotulador (estudante de IA, não cardiologista) classificou todas as 160
frases com base em critérios semiológicos documentados. O Cohen's Kappa
interanotador não pode ser calculado sem segundo anotador independente. Em NLP
clínico de produção, o padrão mínimo exige 2-3 anotadores com concordância Kappa
maior ou igual a 0.80.
