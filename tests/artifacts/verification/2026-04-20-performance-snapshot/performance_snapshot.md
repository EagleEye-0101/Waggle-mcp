# Waggle Local Operation Latency Snapshot

- Backend: `sqlite`
- Embedding mode: `deterministic-v1`
- Database: `/Users/abhigyanshekhar/Desktop/MCP/tests/artifacts/verification/2026-04-20-performance-snapshot/performance.db`

| Operation | Samples | Mean (ms) | Median (ms) | p95 (ms) |
|---|---:|---:|---:|---:|
| `observe_conversation` | 120 | 1.54 | 1.51 | 2.24 |
| `query_graph` | 180 | 1.6 | 1.48 | 1.66 |
| `graph_diff` | 120 | 0.8 | 0.79 | 0.88 |

## Notes
- Deterministic embedding mode is used for reproducibility and local/offline benchmarking.
- These timings are local operational references and may differ under other hardware/backends.
