# Benchmark de memória sem QtWebEngine

`tools/memory/benchmark_memory.py` mede o custo do processo principal do
ZapZap usando controllers e widgets reais, mas substituindo a fronteira do
navegador por `StubWebView`, uma subclasse de `QWidget` que não acessa a rede,
não cria perfil e não inicia Chromium.

## Execução no Fedora

Use o mesmo ambiente Python/PyQt6 empregado para desenvolver o ZapZap:

```bash
python tools/memory/benchmark_memory.py \
  --without-webengine \
  --accounts 1,3,5 \
  --repeat 5 \
  --output-dir memory-results
```

`QT_QPA_PLATFORM=offscreen` é aplicado antes do primeiro import de PyQt6 se a
variável não tiver sido definida pelo usuário. Cada repetição roda em um
processo novo e em diretórios XDG temporários. O padrão executa vinte ciclos de
abertura/fechamento de Configurações; `--lifecycle-cycles` permite aumentar esse
número ou reduzi-lo para um ensaio rápido.

A execução produz:

- `benchmark_memory.json`: amostras completas, deltas, metadados, tendência dos
  ciclos e estatísticas agregadas;
- `benchmark_memory.csv`: uma linha por repetição e cenário;
- `benchmark_memory.md`: médias, medianas e deltas resumidos.

Os cenários cobrem o processo-base, `SingleApplication`, janelas com 1, 3 e 5
contas, primeira abertura de Configurações, navegação por todas as páginas,
fechamento com processamento de `deleteLater`, grade e ciclos repetidos. Ao fim
de cada etapa o executor verifica `sys.modules`; encontrar qualquer módulo
`PyQt6.QtWebEngine*` ou `PyQt6.QtWebChannel` encerra a campanha com erro.

## Interpretação

| Métrica | O que representa | Limitação principal |
|---|---|---|
| `tracemalloc current/peak` | alocações rastreadas pelo Python | não mede a maior parte da memória nativa do Qt |
| RSS | páginas residentes mapeadas no processo | conta bibliotecas compartilhadas integralmente e oscila com o ambiente |
| PSS | RSS compartilhado proporcionalmente | disponível via `/proc/self/smaps_rollup` no Linux |
| USS aproximado | `Private_Clean + Private_Dirty + Private_Hugetlb` | aproxima apenas os mapeamentos privados expostos pelo procfs |

Em sistemas sem `/proc/self/smaps_rollup`, RSS/PSS/USS aparecem como `null` e
`tracemalloc` continua disponível. Nenhuma dessas métricas inclui subprocessos
Chromium. O modo isolado também não mede o custo real dos módulos WebEngine
mapeados no processo principal; ele serve para comparar o heap Python e a
árvore QtWidgets sem essa contaminação.

Não use valores absolutos como limite de CI. Compare campanhas feitas na mesma
máquina, ambiente e versão, priorizando mediana, PSS e USS. A tendência dos
ciclos é diagnóstico observacional e não executa `malloc_trim` nem força um
resultado artificial.

## Comparação

Sem uma regra explícita, o comparador é informativo e sempre termina com sucesso:

```bash
python tools/memory/compare_memory_results.py \
  baseline/benchmark_memory.json candidate/benchmark_memory.json
```

Para uma investigação controlada, uma regra relativa pode ser habilitada. Este
exemplo retorna código 2 se a mediana de PSS crescer mais de 10% em qualquer
cenário comum:

```bash
python tools/memory/compare_memory_results.py \
  baseline/benchmark_memory.json candidate/benchmark_memory.json \
  --metric pss_bytes \
  --regression-threshold-percent 10
```

Exemplo meramente ilustrativo, não representativo de uma máquina real:

```text
baseline_process: PSS mediana 12 MiB
main_window_1_account: PSS mediana 60 MiB; delta +48 MiB
settings_close: PSS mediana 92 MiB; observar junto da tendência dos ciclos
```

O teste leve reproduzível é:

```bash
python -m unittest discover -s tests -p 'test_memory_benchmark.py' -v
```
