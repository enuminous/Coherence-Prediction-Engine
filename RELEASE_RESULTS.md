# Release results — v0.1.0

All three predeclared experiments were retained. **No experiment met the registered acceptance criteria.** No predictor parameter, threshold or comparison was tuned after these results were observed.

| Experiment | Test observations | CPE MAE | Matched EWMA MAE | Relative gain | Disposition |
|---|---:|---:|---:|---:|---|
| Synthetic drift | 3000 | 0.32437 | 0.2808 | -15.52% | rejected on alert rate |
| Synthetic null | 3000 | 0.24058 | 0.24075 | 0.07% | rejected on alert rate |
| Historical sunspots | 59 | 24.811 | 24.821 | 0.04% | not supported |

Positive gain favors CPE. The registered minimum was +5%, together with a positive descriptive uncertainty lower bound and the applicable diagnostic alert constraint.

The drift candidate was approximately 15.52% worse than matched EWMA by MAE. Its mean-gain interval lay entirely below zero. Persistence also outperformed both in this fixture. The null candidate's gain was approximately 0.072%; its interval crossed zero. Synthetic labelled-normal alert rates were 17.33% (drift) and 18.40% (null), exceeding the registered 10% ceiling. The alert diagnostic is shared by the matched models; this failure limits that diagnostic, not just the gate.

On 59 held-out historical sunspot years, the candidate's MAE gain was approximately 0.041%, well below 5%, with an interval crossing zero. Its nominal 90% empirical band covered approximately 74.58% of test outcomes. The no-memory ablation had lower error in this particular dataset; that exploratory observation is not a new independently confirmed winner. Event labels were unavailable, so alert rates are unevaluated.

## Software verification

21 contract tests pass. They cover forecast causality, unchanged training/calibration under future-data changes, preservation of failures, input and source freeze mismatches, ledger tampering, correct handling of missing labels, standalone ticket resolution, recurrence bounds, and the distinction between triple coverage and higher-order dynamics. See `validation/tests.log`.

## Evidence disposition

- Demonstrated: runnable causal prediction/observation/scoring workflow, evidence records and combinatorial atlas checks.
- Rejected or unsupported in these benchmarks: the registered 5% coherence-gating advantage.
- Unresolved: independent prospective replication, adequate real-application calibration, the full ME-102 empirical gate, physical dynamics for the reference atlas, and broader physical claims.

The correct experimental action is to retain the matched conventional alternative, preserve these failed candidate results, and formulate any revised candidate in a new frozen experiment using new test observations. A functioning engine can reject its own candidate model.

## Reproduction

Run `python scripts/run_release.py my-reproduction` from the extracted folder. It creates a new set of complete run directories. Source or data changes invalidate old receipts. Each run can be checked with `python -m cpe verify RUN_DIRECTORY`.
