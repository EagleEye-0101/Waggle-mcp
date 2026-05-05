# RMCA Answer-Level Evaluation Results

> **DISCLAIMER:** Deterministic answer-level metrics are reproducible lower bounds. They are not equivalent to human preference ratings or LLM-judge quality assessments. Scores should be interpreted as retrieval-quality proxies, not end-to-end answer quality.

> **LLM EVAL CAVEAT:** These results use one answering model (Groq llama-3.3-70b-versatile) and should be replicated across models. The model is an answerer, not an independent human judge.

| Family | Scale | Method | Answerer | EM | F1 | Ev.Used | Contra.Corr | Hall.Rate | Tokens |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| pairwise | 128 | rmca_full | groq | 1.000 | 1.000 | 0.333 | 1.000 | 0.000 | 515 |
| pairwise | 128 | query_graph | groq | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 98 |
| pairwise | 128 | bm25_topk | groq | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1422 |
| pairwise | 128 | raw_context | groq | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1422 |
| pairwise | 128 | hybrid_rrf | groq | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1422 |
| pairwise | 512 | rmca_full | groq | 1.000 | 1.000 | 0.333 | 1.000 | 0.000 | 435 |
| pairwise | 512 | query_graph | groq | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 98 |
| pairwise | 512 | bm25_topk | groq | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1390 |
| pairwise | 512 | raw_context | groq | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1390 |
| pairwise | 512 | hybrid_rrf | groq | 0.000 | 0.125 | 0.000 | 0.000 | 0.000 | 1389 |

