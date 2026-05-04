# Table: Pairwise Hidden-Edge Ablation — Real Embeddings (all-MiniLM-L6-v2)

> **Synthetic data caveat:** Deterministic synthetic tasks with real production embeddings.
> Do not compare to RLM paper numerically.
>
> **Model:** `all-MiniLM-L6-v2` (384-dim, locally cached). Seeds 42, 43, 44 — all identical.

## Results

| Variant | Scale | Score | Δ vs full | Tokens | Claim |
|---|---:|---:|---:|---:|---|
| `rmca_full` | 128 | 1.000 | — | 397 | Baseline |
| `rmca_full` | 512 | 1.000 | — | 399 | Baseline |
| `rmca_no_graph_expansion` | 128 | 1.000 | 0.000 | 397 | ❌ Not isolated |
| `rmca_no_graph_expansion` | 512 | 1.000 | 0.000 | 399 | ❌ Not isolated |
| `rmca_no_conflict_resolution` | 128 | 1.000 | 0.000 | 327 | ❌ Not isolated |
| `rmca_no_conflict_resolution` | 512 | 1.000 | 0.000 | 329 | ❌ Not isolated |
| `rmca_no_decomposition` | 128 | **0.000** | **-1.000** | 142 | ✅ Confirmed |
| `rmca_no_decomposition` | 512 | **0.000** | **-1.000** | 143 | ✅ Confirmed |

## Deterministic vs Real Embedding Comparison

| Variant | Det. score | Real score | Δ |
|---|---:|---:|---:|
| `rmca_full` | 1.000 | 1.000 | 0.000 |
| `rmca_no_graph_expansion` | 1.000 | 1.000 | 0.000 |
| `rmca_no_conflict_resolution` | 1.000 | 1.000 | 0.000 |
| `rmca_no_decomposition` | 0.000 | 0.000 | 0.000 |

**Switching to the real embedding model does not change any result.**
The root cause is benchmark construction, not the embedding model.

## Claim Status

| Claim | Status | Root cause of non-isolation |
|---|---|---|
| Decomposition is load-bearing | ✅ Confirmed | Score 1.0→0.0, both models, both scales, all seeds |
| Graph expansion is load-bearing | ❌ Not isolated | Node labels semantically distinctive; real model retrieves gold nodes without edge traversal |
| Conflict resolution is load-bearing | ❌ Not isolated | Scorer checks label presence, not explicit conflict annotation |
