# Pairwise Hidden-Edge Ablation — Real Embeddings (all-MiniLM-L6-v2)

> **Synthetic data caveat:** These results use deterministic synthetic Waggle memory tasks
> with Waggle's production embedding model (`all-MiniLM-L6-v2`, 384-dim sentence-transformers).
> They should not be compared numerically to the RLM paper.

## Setup

- **Embedding model:** `all-MiniLM-L6-v2` (Waggle's production model, locally cached)
- **Benchmark:** `pairwise_hidden_edge` — conflict represented only by typed `contradicts` edges;
  node contents contain no conflict vocabulary ("conflict", "contradict", "violates")
- **Scales:** 128, 512
- **Seeds:** 42, 43, 44 (all seeds produced identical scores)

## Results

| Variant | Scale=128 | Scale=512 | Δ vs full | Claim |
|---|---:|---:|---:|---|
| `rmca_full` | 1.000 | 1.000 | — | Baseline |
| `rmca_no_graph_expansion` | 1.000 | 1.000 | **0.000** | ❌ Not isolated |
| `rmca_no_conflict_resolution` | 1.000 | 1.000 | **0.000** | ❌ Not isolated |
| `rmca_no_decomposition` | **0.000** | **0.000** | **-1.000** | ✅ Confirmed |

## Comparison: Deterministic vs Real Embeddings

| Variant | Deterministic score | Real-emb score | Difference |
|---|---:|---:|---:|
| `rmca_full` | 1.000 | 1.000 | 0.000 |
| `rmca_no_graph_expansion` | 1.000 | 1.000 | 0.000 |
| `rmca_no_conflict_resolution` | 1.000 | 1.000 | 0.000 |
| `rmca_no_decomposition` | 0.000 | 0.000 | 0.000 |

**The real embedding model produces identical results to the deterministic model on this benchmark.**

## Why Graph Expansion Is Still Not Isolated

Switching to `all-MiniLM-L6-v2` does not change the outcome because the root cause is
**not** the embedding model — it is the **benchmark construction**.

The `pairwise_hidden_edge` node labels are:
- Choices: "Cloud database", "External vector service", "Remote inference API"
- Constraints: "Local deployment required", "No third-party services", "Offline operation"

These labels are semantically distinctive enough that `all-MiniLM-L6-v2` retrieves the
relevant choice and constraint nodes directly via cosine similarity, without needing to
traverse the `contradicts` edge. The semantic gap between "Cloud database" and
"Local deployment required" is large enough that both appear in the top-k results of
any reasonable query about deployment constraints.

## What Would Actually Isolate Graph Expansion

To isolate graph expansion, the benchmark needs nodes where:

1. **The choice and constraint labels are semantically similar to distractors** — so that
   a semantic query retrieves distractors instead of the gold conflict pair.
2. **The only signal distinguishing the gold pair is the `contradicts` edge** — not the
   node content or label.

Example construction that would work:
- 50 "technology option" nodes with similar labels ("Option A", "Option B", ..., "Option Z")
- 3 of them have `contradicts` edges to a constraint node
- The question asks which options conflict with the constraint
- Without edge traversal, all options look equally relevant semantically

This requires a fundamentally different benchmark design, not just a different embedding model.

## Conclusion

**The real embedding model confirms the deterministic result.** Decomposition is the only
RMCA component causally isolated as load-bearing on the current `pairwise_hidden_edge`
benchmark. Graph expansion and conflict resolution remain unisolated due to benchmark
construction, not embedding model choice.

The benchmark needs to be redesigned with semantically indistinguishable node labels
to isolate graph traversal benefits.
