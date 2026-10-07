# Mathematical and empirical obligations

## Demonstrated mathematical identities under stated assumptions

For real x,m and epsilon>0, the triangle inequality gives
`0 <= |x-m| <= |x|+|m| < |x|+|m|+epsilon` unless x=m=0, when the numerator is zero. Thus ME-047's scalar coherence lies in [0,1], and is 1 exactly when x=m. Floating-point underflow may attain 0 at extreme scales. The upstream Monolithic `Metrics.lean` states the normed-space version; this release includes that source as a reference and does not claim a fresh Lean build.

For `0 <= lambda < 1`, unrolling residual memory gives

\[
m_t=\lambda^t m_0+(1-\lambda)\sum_{j=1}^{t}\lambda^{t-j}r_j.
\]

If all |r_j|<=R, then

\[
|m_t|\le\lambda^t|m_0|+(1-\lambda^t)R.
\]

Two memories receiving identical residuals differ by `lambda^t` times their initial difference. Since |C|<=1, the candidate correction satisfies `|C_(t-1)m_(t-1)| <= |m_(t-1)|`. These are ordinary linear-recurrence and norm inequalities. They do not prove superior prediction or bounded real-world observations.

The atlas is all three-element subsets of eleven distinct sector labels. Therefore its size is choose(11,3)=165. Each sector appears in choose(10,2)=45 triples; each pair appears in 9. The supplied Python enumerator checks these counts and the full overlap spectrum, independently of the preserved Lean source. These are exhaustive finite checks in Python, not new kernel-checked proofs.

## Obligation ledger

| Obligation | Status in this release |
|---|---|
| Explicit predictor equations, assumptions and units | Specified |
| Forecast uses only past observations | Implementation plus noninterference and ticket tests |
| Recurrence forgetting and bounded-input bound | Algebraic argument above plus numerical tests |
| CPE forecast gate improves prediction | Empirical hypothesis; see actual per-run dispositions |
| All 102 equations implemented | Not claimed; source catalogue distinguishes reference-only entries |
| All 165 triples have physical dynamics | Not claimed; coverage catalogue only |
| Three-sector coverage guarantees arbitrary global physics | Rejected as a general assertion; higher-order interactions can be absent |
| New Lean proofs checked in this workspace | Not performed; preserved upstream proofs have their own provenance |
| New fundamental physical law | Not demonstrated |
| ME-102 empirical gate | Unfulfilled by this release |
| Independent prospective replication | Outstanding |

The code test suite validates software contracts. It is never promoted to empirical evidence for a physical hypothesis.
