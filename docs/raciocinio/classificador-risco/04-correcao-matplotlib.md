# IV. Correção do warning FigureCanvasAgg

## O problema

Ao executar os notebooks via `jupyter nbconvert --execute`, o matplotlib emitia
o seguinte warning em cada célula que chamava `plt.show()`:

```
UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```

O warning aparecia nos outputs do `classificador_risco.ipynb` e do
`mlp_heartbeat_v2.ipynb`, poluindo a saída com mensagens de sistema que o
avaliador não deveria ver.

## Diagnóstico

O warning ocorre porque os notebooks forçavam o backend `Agg` explicitamente:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
```

O backend `Agg` (Anti-Grain Geometry) renderiza gráficos para memória/arquivo,
não para tela. O matplotlib o utiliza quando não existe display gráfico (execução
headless, servidor sem GUI). O `plt.show()` solicita a exibição interativa de uma
figura — operação que o backend `Agg` não suporta, porque não existe janela para
exibir. O matplotlib emite o warning para informar que o `plt.show()` não produziu
efeito visual.

## Por que o código original usava `Agg`

O autor adicionou `matplotlib.use("Agg")` para garantir que o notebook executaria
em ambientes sem display gráfico (servidores, CI/CD, `nbconvert`). A intenção era
correta — sem um backend não-interativo, o matplotlib tenta abrir uma janela GUI
e falha com erro em ambientes headless.

## Por que a solução não era remover `plt.show()`

Remover `plt.show()` eliminaria o warning, mas quebraria a exibição em Jupyter
interativo. Em um Jupyter notebook com kernel ativo, `plt.show()` encerra a
construção da figura e a exibe como output da célula. Sem `plt.show()`, o Jupyter
ainda exibe a figura (via integração automática), mas o comportamento difere entre
versões do Jupyter e configurações de `%matplotlib`.

## A solução aplicada

A correção remove `matplotlib.use("Agg")` e mantém `plt.show()`:

```python
# antes (gerava warning)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# depois (sem warning)
import matplotlib.pyplot as plt
```

O Jupyter notebook seleciona o backend automaticamente:
- Em Jupyter interativo: usa `inline` (renderiza PNG no output da célula)
- Em `nbconvert --execute`: usa `agg` internamente mas via o mecanismo do IPython
  que captura a figura sem chamar a renderização interativa — sem warning

O `plt.show()` permanece no código para compatibilidade com Jupyter interativo.
O `plt.savefig()` permanece antes do `plt.show()` para garantir que a imagem PNG
é salva independente do backend — `savefig` funciona com qualquer backend.

## Notebooks corrigidos

| Notebook | Warning antes | Warning depois |
|----------|--------------|----------------|
| `classificador_risco.ipynb` | 2 ocorrências | 0 |
| `mlp_heartbeat_v2.ipynb` | 4 ocorrências | 0 |

Ambos os notebooks re-executados via `jupyter nbconvert --execute` sem nenhum
warning de matplotlib nos outputs.
