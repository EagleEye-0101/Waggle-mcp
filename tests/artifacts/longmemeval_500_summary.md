# LongMemEval 500-case retrieval-only summary

## graph_raw

```text
=== graph_raw (n=500) ===
overall          R@5=97.4%  Exact@5=89.0%  Exact@10=89.0%  Exact@20=89.0%
cardinality=1    R@5=95.5%  Exact@5=95.5%  Exact@10=95.5%  Exact@20=95.5%   (n=176)
cardinality=2    R@5=98.0%  Exact@5=93.2%  Exact@10=93.2%  Exact@20=93.2%   (n=250)
cardinality=3    R@5=100.0%  Exact@5=73.2%  Exact@10=73.2%  Exact@20=73.2%   (n=41)
cardinality=4    R@5=100.0%  Exact@5=47.4%  Exact@10=47.4%  Exact@20=47.4%   (n=19)
cardinality=5    R@5=100.0%  Exact@5=45.5%  Exact@10=45.5%  Exact@20=45.5%   (n=11)
cardinality=6    R@5=100.0%  Exact@5=0.0%  Exact@10=0.0%  Exact@20=0.0%   (n=3)
divergence: case_072_41e549b7, case_073_9b77e32e, case_078_f97a2da7
```

## graph_hybrid

```text
=== graph_hybrid (n=500) ===
overall          R@5=97.0%  Exact@5=87.2%  Exact@10=94.8%  Exact@20=98.0%
cardinality=1    R@5=95.5%  Exact@5=95.5%  Exact@10=97.2%  Exact@20=98.3%   (n=176)
cardinality=2    R@5=97.6%  Exact@5=90.8%  Exact@10=95.2%  Exact@20=98.4%   (n=250)
cardinality=3    R@5=97.6%  Exact@5=70.7%  Exact@10=92.7%  Exact@20=100.0%   (n=41)
cardinality=4    R@5=100.0%  Exact@5=42.1%  Exact@10=78.9%  Exact@20=84.2%   (n=19)
cardinality=5    R@5=100.0%  Exact@5=36.4%  Exact@10=90.9%  Exact@20=100.0%   (n=11)
cardinality=6    R@5=100.0%  Exact@5=0.0%  Exact@10=66.7%  Exact@20=100.0%   (n=3)
divergence: case_072_41e549b7, case_073_9b77e32e, case_082_db34ce0a
```

On single-gold questions, `R@5` and `Exact@5` are identical by definition, and the reports show that directly. The divergence appears on multi-gold cases: both modes usually retrieve at least one supporting gold chunk, but they often fail to recover the full gold support set inside the top 5. That gap is modest for cardinality `2` and then becomes large for cardinality `3+`, with `Exact@5` collapsing hardest on cardinalities `4-6` even when `R@5` is near or at `100%`. In practice, this says the graph retriever is good at finding some relevant support for multi-hop or multi-evidence questions, but much less reliable at assembling all required supporting chunks within a 5-item budget. The hardest slice is therefore the higher-cardinality multi-gold questions, not the single-gold retrieval cases.

## Divergence examples: graph_raw

```json
{
  "case_id": "case_072_41e549b7",
  "gold_set": [
    "answer_ec904b3c_1",
    "answer_ec904b3c_4",
    "answer_ec904b3c_3",
    "answer_ec904b3c_2"
  ],
  "retrieved_top5": [
    "2e4430d8_2",
    "sharegpt_nVi6tIt_0",
    "sharegpt_zciCXP1_12",
    "sharegpt_J7ZAFLd_0",
    "answer_ec904b3c_1"
  ],
  "missing": [
    "answer_ec904b3c_4",
    "answer_ec904b3c_3",
    "answer_ec904b3c_2"
  ]
}
{
  "case_id": "case_073_9b77e32e",
  "gold_set": [
    "answer_593bdffd_4",
    "answer_593bdffd_1",
    "answer_593bdffd_3",
    "answer_593bdffd_2"
  ],
  "retrieved_top5": [
    "answer_593bdffd_1",
    "answer_593bdffd_4",
    "answer_593bdffd_2",
    "sharegpt_Opm4kTV_0",
    "eb47739f_2"
  ],
  "missing": [
    "answer_593bdffd_3"
  ]
}
{
  "case_id": "case_078_f97a2da7",
  "gold_set": [
    "answer_526354c8_1",
    "answer_526354c8_3",
    "answer_526354c8_2"
  ],
  "retrieved_top5": [
    "answer_526354c8_2",
    "answer_526354c8_1",
    "072b4f50_1",
    "b192ae00_2",
    "sharegpt_ynLoh9N_0"
  ],
  "missing": [
    "answer_526354c8_3"
  ]
}
```

## Divergence examples: graph_hybrid

```json
{
  "case_id": "case_072_41e549b7",
  "gold_set": [
    "answer_ec904b3c_1",
    "answer_ec904b3c_4",
    "answer_ec904b3c_3",
    "answer_ec904b3c_2"
  ],
  "retrieved_top5": [
    "2e4430d8_2",
    "sharegpt_zciCXP1_12",
    "0bab76de",
    "answer_ec904b3c_4",
    "answer_ec904b3c_1"
  ],
  "missing": [
    "answer_ec904b3c_3",
    "answer_ec904b3c_2"
  ]
}
{
  "case_id": "case_073_9b77e32e",
  "gold_set": [
    "answer_593bdffd_4",
    "answer_593bdffd_1",
    "answer_593bdffd_3",
    "answer_593bdffd_2"
  ],
  "retrieved_top5": [
    "a7d014e4_1",
    "answer_593bdffd_1",
    "answer_593bdffd_4",
    "answer_593bdffd_2",
    "eb47739f_2"
  ],
  "missing": [
    "answer_593bdffd_3"
  ]
}
{
  "case_id": "case_082_db34ce0a",
  "gold_set": [
    "answer_cf9e3940_2",
    "answer_cf9e3940_1",
    "answer_cf9e3940_3"
  ],
  "retrieved_top5": [
    "answer_cf9e3940_3",
    "88c8df0e_3",
    "d75245ea",
    "sharegpt_H2ddZjb_13",
    "answer_cf9e3940_1"
  ],
  "missing": [
    "answer_cf9e3940_2"
  ]
}
```
