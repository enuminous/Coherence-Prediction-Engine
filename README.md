# Coherence Prediction Engine

**Version 0.1.0 · Matthew Chenoweth Wright / Monolithic · October 7, 2026**

A runnable, auditable forecasting and experimental-evaluation package connecting an EFMW coherence metric, a TORTOISE-derived Zoo workflow, the Monolithic 102 reference catalogue, and the complete eleven-sector / 165-triplet combinatorial atlas.

**Open `index.html` first** for the release dashboard, actual benchmark results and links to every report. All examples and reports work offline after extraction. The numerical engine needs **Python 3.10 or newer and no third-party dependencies**.

The implemented research loop is:

**Specify → Freeze → Predict → Observe → Compare → Ablate → Record → Retain or reject → New experiment.**

## Quick start

Unzip, open a terminal in this folder, and run:

```bash
python -m unittest discover -s tests -v
python -m cpe verify runs/sunspots
python -m cpe atlas
python -m cpe catalog ME-047
```

To reproduce every experiment into a new directory:

```bash
python scripts/run_release.py my-reproduction
```

The engine refuses to overwrite an existing experiment directory. Open `my-reproduction/sunspots/report.html` to inspect the result. Local creation timestamps can differ; predictions and numerical metrics should reproduce under the same Python version and inputs.

To evaluate your own equally spaced numeric observations, use `docs/DATA_AND_PROTOCOL.md`. The commands are:

```bash
python -m cpe freeze --data your-data.csv --protocol your-protocol.json --out your-freeze.json
python -m cpe run --data your-data.csv --freeze your-freeze.json --out your-run
python -m cpe verify your-run
```

## A prediction before its outcome

Use the final state of a completed run to issue the next forecast:

```bash
python -m cpe forecast --checkpoint runs/sunspots/checkpoints.json --series sunspots --out forecast-ticket.json
```

The bundled legacy sunspot series ends in 2008, so that example issues a **historical demonstration** for 2009. For a genuinely future prediction, first build a checkpoint from observations through your actual present cutoff, then publish or independently timestamp the ticket before the outcome arrives.

Once the matching outcome exists, place it in `observation.json`:

```json
{"series":"sunspots","time":2009,"y":0.0,"source":"REPLACE WITH THE ACTUAL OBSERVATION AND SOURCE"}
```

The `0.0` above is an illustrative placeholder, not a reported observation. Replace it before resolving.

```bash
python -m cpe resolve --ticket forecast-ticket.json --observation observation.json --out resolution.json
python -m cpe forecast --checkpoint resolution.json --out next-ticket.json
```

The outcome must match the ticket's series and time. The resolver recomputes the predictions from the frozen state, scores the outcome, and supplies the next checkpoint. It records the operator's source assertion without pretending to verify independent collection.

## What is implemented

| Component | Actual v0.1 capability |
|---|---|
| EFMW / Monolithic | ME-047 scalar coherence is executable; all 102 source equations are indexed with explicit binding status. |
| Predictor | Train-only AR(1) plus lagged coherence-gated EWMA residual correction. |
| Matched control | Same AR(1), data, history, decay and residual memory, with the coherence gate removed. |
| Ablations and baselines | No-memory correction, no-correction AR(1), persistence, and training mean. |
| Zoo workflow | Explicit regression adaptation of TORTOISE's freeze–predict–score–ablate–replicate cycle. |
| 165 atlas | Exact enumeration, sector/pair incidence and overlap checks; explicit reports of higher-order coverage gaps. |
| Calibration | Separate chronological calibration data for fixed empirical prediction bands and diagnostic thresholds. |
| Falsification | Frozen primary comparator, minimum effect size, uncertainty interval, negative-result records and revision decisions. |
| Reproducibility | Source/data/protocol hashes, prediction-before-observation journal, artifact verification and no-overwrite outputs. |
| External observations | A public historical sunspot benchmark plus a strict CSV adapter for other datasets. |
| Future observations | Standalone forecast tickets and later resolution into the next checkpoint. |

## What the release establishes

This release supplies a working **bounded science-engine prototype**. Its benchmarks evaluate a particular forecasting construction. Review `RELEASE_RESULTS.md` for the actual dispositions, including failures.

The atlas checks are combinatorial facts. Source equations retained from the corpus are not automatically executable models, independently proved theorems, or validated physical laws. This release does not instantiate all 102 equations as one physical system. It does not assert that the full Zoo has passed. It does not claim that standard EWMA mathematics is new.

**ME-102 remains unsatisfied:** the source criterion calls for warning lead-time advantage, false-alarm and compute limits, and independent replication. This package's one-step forecasting experiment does not substitute for those obligations.

## Files worth opening

- `docs/METHOD.md`: exact equations, causal ordering, decision rule and limitations.
- `docs/INTEGRATION_AND_GAPS.md`: completed implementation gaps and unresolved scientific obligations.
- `docs/DATA_AND_PROTOCOL.md`: external observation schema and experiment configuration.
- `docs/PROOF_OBLIGATIONS.md`: mathematical arguments and what has or has not been machine checked.
- `cpe/registry/`: 102 equations, 165 triples, claims, Zoo contract and pinned source identities.
- `references/`: preserved source material and provenance.
- `runs/`: complete shipped experiments, reports, forecasts, failures and revision records.
- `tests/test_engine.py`: checks for causality, integrity, numerical edge cases and scope boundaries.

The original implementation is small enough to audit. All computation is local; it makes no network calls and sends no observations elsewhere.
