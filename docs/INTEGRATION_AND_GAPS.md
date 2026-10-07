# Integration and gap ledger

| Gap identified in the conversation | What v0.1 supplies | Evidence / remaining boundary |
|---|---|---|
| Quantitative prediction from explicit assumptions | Fully specified causal one-step predictor | `cpe/core.py`, frozen protocols, mathematical notes |
| Comparison with competing models | Matched EWMA, AR(1), persistence, mean, no-memory ablation | Every run reports all six models |
| Independent observations | Public historical observational data and user CSV adapter | Data source is external; evaluator is not independent and data are not a blind prospective holdout |
| Failure preservation | Negative dispositions, original predictions, revision proposals | Existing run folders cannot be overwritten |
| Revision or rejection | Rule-based rejection/replication decision and next-state tickets | No parameter tuning on the scored holdout |
| Reproducible evidence | Code/config/data freeze, event chain and artifact manifest | Hashes provide integrity, not external attestation |
| Corpus provenance | All 102 source entries and explicit implementation statuses | One direct numerical metric binding, ME-047; no fabricated 102-equation joint solver |
| Atlas completeness | All 165 triples, incidence and overlap tests, higher-order gap queries | Completeness is restricted to the specified eleven labels and rank-three atlas |
| Zoo anti-circularity | Source-grounded TORTOISE regression adapter | A scoped adaptation; no assertion that all Zoo animals ran |
| Physical truth | Explicit experimental boundary | Requires derived observables and physical measurements; remains unresolved |

## Binding details

ME-047 uses x = observed scalar and m = the base forecast. This instantiation respects the metric's numerical type and units. Multiplying residual memory by lagged coherence is this package's candidate-model hypothesis; it is not presented as a corpus theorem.

ME-102 is preserved verbatim in the reference catalogue with disposition `NOT_SATISFIED_BY_THIS_RELEASE`. Its independent-replication, warning lead-time, false-alarm and compute-budget conditions are not replaced by a passing unit test or an MAE comparison.

The 165 atlas has no automatic influence on the numerical forecasts. It is an executable **coverage audit** and a catalogue for future model bindings. Claiming that all sectors are already simulated would require missing dynamics, units, couplings and justified observable mappings. Attempting to run the current predictor with physical-sector bindings is rejected rather than silently ignored.

Example of exposing a gap:

```bash
python -m cpe atlas --sectors E M S F --order 4
```

The output reports zero coverage for the required four-sector interaction. The three-sector atlas cannot certify arbitrary four-body terms. A higher-order extension can be designed as a new model; no such closure is assumed here.

## Minimal next independent study

Select one real sensor stream and a measurable target. Specify units, sampling, exclusions and the observation source before collection. Freeze the baseline, model, horizon, sample count, effect threshold, false-alarm rules if applicable, and stopping rule. Use a separate evaluator or publicly timestamped prediction tickets. Score every registered outcome. Compare against the matched control and preserve null/negative findings. Replicate on a second independent collection before generalizing.

The current release fills software and protocol gaps that can be filled in this workspace. It cannot manufacture independent replication or physical evidence.
