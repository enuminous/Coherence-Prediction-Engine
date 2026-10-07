# FieldSpace verification report (`enuminous/FieldSpace`, `main` @ 3a5b659)

## Answer: how many new potential laws?

The repository's `THEOREM_REGISTER.md` has a section called **"Candidate consistency laws"** with
**4** entries:

| ID | Name | Current label |
|---|---|---|
| FS-C01 | Projected Atlas Gluing | upgraded to PROVED-PROJECTED-GLUING (proved in `enuminous/EFMW_Post156_Zoo_Audit`) |
| FS-C02 | Master-Action Reciprocity | CANDIDATE-CONSISTENCY-LAW |
| FS-C03 | Noether/Conservation Closure | CANDIDATE-CONSISTENCY-LAW |
| FS-C04 | Parameter-Economy Law | CANDIDATE-CONSISTENCY-LAW |

So there are **4 potential laws in total; 3 are still open candidates** (C02–C04), and C01 is now a
proved *mathematical* theorem. None of them is a law of nature: the register says outright,
"No new fundamental physical law claimed". FS-T08, the "Trilinear Null-Slice Law", is called a
law by name but is labelled as ordinary algebra, not a new law.

## What was checked

1. **Upstream Lean files** (`FieldSpace/Structure.lean`, `Ablations.lean`, `Coupling.lean`) are copied
   into `RequestProject/Upstream/` and build under Lean 4.28 / Mathlib with no `sorry`. Caveat: most of
   them only check arithmetic identities about numbers, e.g. `Nat.choose 11 3 = 165`, `8 = 8`, `1 = 1`,
   `56+56+28+16+8+1 = 165`. They do not state anything about actual sets of sectors.
2. **`RequestProject/Verified.lean`** states FS-T01 to FS-T07 about the real objects (the 11-sector
   type and its 3-element subsets) and proves them. All are true:
   165 triplets; each sector is in 45 of them; each pair of sectors is in 9; the six classes have
   sizes 56/56/28/16/8/1 and cover every triplet; the statement inventory is 45 + 90 + 90 + 360 = 585;
   deleting any set of k sectors leaves `C(11-k,3)` triplets; the overlap spectrum is 1980/6930/4620
   out of 13530 pairs. The finite checks are discharged by `native_decide`.
   The same file also proves the simplest form of FS-C02: a bilinear term `λ φ_i φ_j` gives the
   same coefficient `λ` in both Euler–Lagrange equations.
3. **FS-C01, projected gluing.** `enuminous/EFMW_Post156_Zoo_Audit` was built locally, together with its
   dependency `Einsteinian-156-Aristotle` at the pinned commit. `fieldSpace_projected_atlas_gluing` and
   `projected_atlas_gluing_unique` build without `sorry` and use only the standard axioms
   (`propext`, `Classical.choice`, `Quot.sound`). The theorem holds under its explicit
   component-k-body hypothesis.
4. **Source file.** Running the repository's `scripts/audit_fieldspace.py` gives 165 headings, 165
   populated blocks, no missing or empty blocks, and 45/90/90/360 = 585 statements. This is a script
   check only and was not proved in Lean.

## Observations (from scripts, not proved in Lean)

- About FS-C02: the source writes the directional scalar pair couplings as separate symbols,
  `λ_ij φ_j` and `λ_ji φ_i`. There are 56 ordered scalar pairs. If FS-C02 holds (`λ_ij = λ_ji`),
  they reduce to 28 independent parameters.
- The source uses 550 distinct `λ_…`/`κ_…` symbols. That is the parameter count FS-C04 aims to reduce.
- FS-C03 and FS-C04 cannot be checked in their current form. The source does not define
  `T^(int)`, `Ξ^ν`, gauge groups or units.

