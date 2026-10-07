# Source provenance

Source identities are fixed in `cpe/registry/source_lock.json`. The release manifest separately hashes every bundled file. Some text snapshots may normalize terminal newlines; the numerical data table is preserved.

| Material | Repository / source | Revision |
|---|---|---|
| Canonical 102 equations and source map | https://github.com/enuminous/Monlithic_EFMW_102_Lean4 | `58f743bd44929049928d0b1d8beee9403c549a0d` |
| Derived metric and other mathematical statements | https://github.com/enuminous/Aristotle-102-Monolithic-Lean | `1d89827ccb914d26055feac13229134651d57700` |
| 165-triplet sector definitions and structural proofs | https://github.com/enuminous/Aristotle-165-Einsteinian-Tensors | `3053b513ec9ff2f42bba86f1d81694cde98a3d86` |
| TORTOISE operation contract | https://github.com/enuminous/Tortoise | `6658128fd2df96ff6c32fce219bfc9ee3e8876da` |
| Historical yearly sunspot table | https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/sunspots/sunspots.csv | Git blob `bf1aec0ce46612fb472d08b66a43115538f405d5` |

The sunspot dataset documentation is https://www.statsmodels.org/stable/datasets/generated/sunspots.html. It attributes the legacy annual 1700–2008 observations to the National Geophysical Data Center and identifies the data as public domain. It is an external historical benchmark, not an independently conducted evaluation of CPE.

`MONOLITHIC_LAWS.md` and `FIELDSPACE_VERIFICATION.md` are historical upstream reports at the revisions above. Statements about what was open or checked describe those reports, not a fresh audit of all later repositories. Their Lean files are retained as references. Lean/Mathlib are not runtime dependencies, and no Lean build was performed for this release.

New CPE implementation decisions, including the lagged coherence gate, are described in `docs/METHOD.md`. They should not be attributed to an upstream theorem or silently folded into the canonical corpus.

The source material was accessed while constructing this package. Public historical observations were available at design time. The release's frozen run receipts attest to local input identities and ordering; they do not attest to external preregistration or blinding.
