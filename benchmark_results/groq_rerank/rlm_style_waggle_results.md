# Waggle RLM-style Benchmark Results

> **Warning:** This benchmark follows the benchmark families used in the RLM paper,
> but uses deterministic synthetic memory tasks mapped to Waggle's graph/transcript
> environment. It should **not** be compared numerically to the RLM paper until the
> exact public datasets and matching model setup are run.

| Benchmark family | Scale | Method | Score | F1 | Ev. Coverage | Tokens returned | Latency (ms) |
|---|---:|---|---:|---:|---:|---:|---:|
| OOLONG-Pairs-style | 128 | raw_context | 0.000 | 0.000 | 0.000 | 1422 | 4 |
| OOLONG-Pairs-style | 128 | query_graph | 0.000 | 0.000 | 0.000 | 98 | 6 |
| OOLONG-Pairs-style | 128 | build_context | 1.000 | 1.000 | 1.000 | 515 | 39 |
| CodeQA-style | 128 | raw_context | 0.000 | 0.500 | 0.500 | 1382 | 3 |
| CodeQA-style | 128 | query_graph | 1.000 | 1.000 | 1.000 | 150 | 6 |
| CodeQA-style | 128 | build_context | 1.000 | 1.000 | 1.000 | 509 | 50 |
| ContextReset | 128 | raw_context | 0.000 | 0.000 | 0.250 | 1413 | 5 |
| ContextReset | 128 | query_graph | 0.000 | 0.000 | 0.000 | 76 | 9 |
| ContextReset | 128 | build_context | 0.000 | 0.000 | 0.000 | 121 | 33 |

## Token efficiency: build_context vs baselines

| Benchmark family | Scale | Method | Tokens returned | Score |
|---|---:|---|---:|---:|
| CodeQA-style | 128 | query_graph | 150 | 1.000 |
| CodeQA-style | 128 | build_context | 509 | 1.000 |
| CodeQA-style | 128 | raw_context | 1382 | 0.000 |
| ContextReset | 128 | query_graph | 76 | 0.000 |
| ContextReset | 128 | build_context | 121 | 0.000 |
| ContextReset | 128 | raw_context | 1413 | 0.000 |
| OOLONG-Pairs-style | 128 | query_graph | 98 | 0.000 |
| OOLONG-Pairs-style | 128 | build_context | 515 | 1.000 |
| OOLONG-Pairs-style | 128 | raw_context | 1422 | 0.000 |
