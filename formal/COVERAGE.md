# Formal coverage

## Frozen target

Source: [`docs/PROOF_OBLIGATIONS.md`](../docs/PROOF_OBLIGATIONS.md), baseline commit `5337c0d9600665b4ac9a0d514d3b84d28cf57f35`.
The definitions and theorem hypotheses in `Memory.lean` are the acceptance target.
The pinned Lean/Mathlib build and strict axiom audit must pass before treating a
statement as machine-checked. The workflow records the exact tested commit/run.

## Statements covered

EWMA closed form, bounded-input estimate, exact forgetting of initial differences, convergence of those differences, prefix causality and the gated correction bound.

## Limits and unresolved obligations

The residual stream is an input, not an assumed bounded real-world observation process. This does not prove forecast superiority, a physical law, or all 102/165 source interpretations. Existing reference files retain their provenance.

## Evidence discipline

These are established algebra, analysis and finite-dimensional mathematics,
not a novelty claim. Formal proofs establish only their stated hypotheses and
conclusions. Computational regression tests are software checks, not independent
experimental evidence. No theorem uses a claimed physical interpretation as a
premise. No custom axioms, `sorry`, or native-evaluation trust exception is allowed.
No new animal operation is invented or claimed to have been executed.

The first evidence status is **unresolved** until the exact-commit workflow
succeeds; thereafter only the covered formal statements are **demonstrated**.
Scientific applicability remains a **hypothesis/postulate** unless separately tested.
