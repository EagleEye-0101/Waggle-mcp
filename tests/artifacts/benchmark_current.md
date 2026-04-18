# Waggle Comparative Evaluation

- Scenarios: 27
- Queries: 66
- Task families: adversarial_paraphrase, cross_scenario_synthesis, decision_delta, factual_recall, multi_session_change, temporal_latest, temporal_original

| System | Hit@k | Exact support | Mean tokens | Median tokens | p95 tokens |
|--------|-------|---------------|-------------|---------------|------------|
| waggle | 88% | 73% | 37.7 | 38.0 | 45.0 |
| rag_naive | 100% | 98% | 150.2 | 149.0 | 161.0 |

## Failure Protocol

- If Waggle token reduction is under 15 percent, inspect whether graph serialization or context assembly is offsetting compression gains.
- If the tuned baseline matches Waggle on retrieval quality, frame the result as efficiency and structure first rather than retrieval superiority.
- If temporal queries do not separate systems, audit whether the corpus actually requires temporal reasoning before expanding claims.
- If multi-session change queries are inconclusive, expand that slice before broadening the whole pilot corpus.

## Query Stress Eval

- Cases: 40
- Families: adversarial_paraphrase, temporal_latest

| System | Hit@k | Exact support | Mean tokens |
|--------|-------|---------------|-------------|
| graph_raw | 98% | 98% | 37.0 |
| graph_hybrid | 98% | 98% | 63.9 |
