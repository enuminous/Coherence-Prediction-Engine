# Laws derived from the Monolithic EFMW-102 corpus

Source: `enuminous/Monlithic_EFMW_102_Lean4` (commit `58f743b`). That repository stores all 102
equations and gives typed definitions for some of them. Its only theorem is `ME043.scalar46_eq_scalar23_sq`.

This project adds **machine-checked laws** that follow from the corpus equations. Every
statement below is a Lean theorem in `RequestProject/` and builds with no `sorry`. The only
axioms used are Lean's standard ones (`propext`, `Classical.choice`, `Quot.sound`).

**Scope.** These are *mathematical* consequences of the equations as written, under the
hypotheses stated in each theorem. None of them is evidence that EFMW describes the physical
world. Testing that is the job of the empirical gate ME-102.

## 1. Golden-ratio / Scalar-φ cluster (`Golden.lean`)
| Law | Corpus items | Lean name |
|---|---|---|
| φ² = φ + 1, φ − 1 = 1/φ | ME-041, ME-046 | `phi_sq`, `phi_sub_one` |
| φⁿ⁺¹ = Fₙ₊₁ φ + Fₙ (Fibonacci) | ME-041–044 | `phi_pow_succ` |
| Φ₂₃ = φ²³ = 28657 φ + 17711 | ME-042 | `scalar23_closed_form` |
| Φ₄₆ = (φ²³)² = 1836311903 φ + 1134903170 | ME-043 | `scalar46_closed_form` |
| V₁₃ = φ¹³ = 233 φ + 144 | ME-044 | `veto13_closed_form` |
| C_φ[X] = φ⁻¹X + φ⁻²A(φX), with φ⁻¹ + φ⁻² = 1 (a **convex combination**) | ME-046 | `phiTiled_convex` |
| S₂₃ is invertible (inverse: multiply by φ⁻²³) | ME-085 | `S23_inverse` |
| **No-go:** S₂₃(0) = 0, and S₂₃X = 0 ⇔ X = 0, so linear scaling cannot "reborn" a null state | ME-086, ME-088 | `S23_null` |

## 2. Coherence order parameter and Red Queen cluster (`Coherence.lean`)
| Law | Corpus items | Lean name |
|---|---|---|
| U(−Φ) = U(Φ) | ME-025 | `U_even` |
| U′(Φ) = aΦ³ − bΦ, so the uncoupled ME-024 is the gradient flow τΦ̇ = −U′(Φ) | ME-024, ME-025 | `U_hasDerivAt` |
| For a > 0: the equilibria are exactly Φ = 0 and Φ² = b/a | ME-024/025 | `U_critical_iff` |
| U ≥ −b²/(4a), with equality iff Φ² = b/a (double-well minimum) | ME-025 | `U_ge_min` |
| **Lyapunov law:** along τΦ̇ = bΦ − aΦ³ (τ > 0), dU/dt = −(U′)²/τ ≤ 0, so U(Φ(t)) never increases | ME-024 | `U_lyapunov` |
| dC/dt = 0 ⇔ αC(1 − C/K) = βD − γḊ | ME-062 ⇒ ME-063 | `redQueen_equilibrium` |
| **Maximum disorder load:** for α, K > 0 an equilibrium exists **iff** βD − γḊ ≤ αK/4 | ME-063 | `redQueen_equilibrium_exists_iff` |

## 3. Relaxation, decay and emergent time (`Dynamics.lean`)
| Law | Corpus items | Lean name |
|---|---|---|
| Every solution of dη/dt = (η_eq − η)/τ is η_eq + (η(0) − η_eq)e^(−t/τ) (uniqueness) | ME-082 | `relaxation_unique`, `relaxation_solves` |
| ME-078 is **exactly** the unique solution of ME-082 with η_eq = η₀ and η(0) = 0 | ME-078 ⇔ ME-082 | `thixo_eq_relaxation` |
| η(t) → η₀ as t → ∞ (τ > 0) | ME-078 | `thixo_tendsto` |
| ρ₀e^(−t/τₙ) is the unique solution of ρ′ = −ρ/τₙ with ρ(0) = ρ₀ | ME-079 | `decay_ode` |
| Half-life: ρ(τₙ ln 2) = ρ₀/2 | ME-079 | `decay_half_life` |
| Θ(t) = ∫₀ᵗ ω_rec gives dΘ/dt = ω_rec (this is ME-075). If ω_rec > 0, Θ is strictly increasing, so it is a valid clock | ME-075 ⇔ ME-076 | `emergent_time` |

## 4. Metrics cluster (`Metrics.lean`)
| Law | Corpus items | Lean name |
|---|---|---|
| For ε > 0: 0 ≤ C ≤ 1, C is symmetric in x and m, and C = 1 ⇔ x = m (any normed space) | ME-047 | `coherenceScore_laws` |
| 0 ≤ I_rec ≤ C | ME-048 | `recursiveIntegrity_laws` |
| 0 ≤ K ≤ 1, and K = 1 for phase-locked oscillators | ME-091 | `kuramoto_laws` |
| Gibbs' inequality D_KL(P‖Q) ≥ 0 | ME-092 | `kl_nonneg` |
| 0 ≤ H_phrase ≤ log n | ME-034 | `phraseEntropy_bounds` |
| Collapse probabilities are ≥ 0 and sum to 1 (Born-compatible) | ME-061 | `collapseProb_distribution` |
| Collapse-Ω argmin exists for any finite, non-empty outcome set | ME-059 | `collapseOmega_exists` |
| For P(H), C ∈ [0,1]: 0 ≤ Risk ≤ P(H), and Risk does not increase as C grows | ME-089 | `recursiveRisk_laws` |

## 5. Field, quantum, cognitive-PDE and recursion cluster (`Fields.lean`)
| Law | Corpus items | Lean name |
|---|---|---|
| g^{μν}∂_μ∂_νφ with the Minkowski metric (+ − − −) = (1/c²)φ_tt − ∇²φ | ME-003 ⇒ ME-004 | `dAlembert_flat` |
| ME-005 = ((1 − α²)/c²)φ_tt − ∇²φ. When α² = 1 it **degenerates** to the Poisson equation −∇²φ = (4π/c²)(E + Pc), i.e. there is no wave propagation | ME-002, ME-004, ME-005 | `me005_reduction` |
| I_{μν} = T^(φ)_{μν} + R_{μν} | ME-006 vs ME-015 | `infoTensor_eq_stress_add` |
| ME-007 ⇔ ME-008, component by component | ME-007, ME-008 | `einstein_expanded` |
| \|ρe^{iθ}\|² = ρ² | ME-016 ⇒ ME-017 | `polar_density` |
| **Only α + β matters** in the S–O equations, and ME-037 is ME-036 with S and O swapped | ME-036, ME-037 | `puddle_laws` |
| S_{n+1} = S_n ∘ O_n ∘ S_n | ME-065 | `closure_law` |
| If T² = 1 and T⁻¹UT = U⁻¹, then T∘U is an involution | ME-073, ME-074 | `chronologos_involution` |
| Eₙ = E₀ + n·ΔE·C, which grows without bound if ΔE·C > 0 | ME-094, ME-101 | `linear_accumulation` |

## What could *not* be derived (open obligations)
- **ME-001, ME-009, ME-013, ME-014:** deriving field equations from the actions needs a
  formal metric-variation (Euler–Lagrange) framework, which is not set up here.
- **ME-007 / ME-008 consistency:** the contracted Bianchi identity requires
  ∇^μ(T_{μν} + κI_{μν}) = 0. Because I contains R_{μν}, and ∇^μR_{μν} = ½∇_νR is generally
  non-zero, this is a real constraint on the theory. It needs a differential-geometry setting to formalize.
- **ME-022–033** (existence and uniqueness, attractors, Lyapunov exponents), **ME-036/037**
  (well-posedness of the PDEs), **ME-056** (the rotating Friedmann equation needs a specified metric), and
  **ME-077–081** (the relativistic thixotropic fluid) all remain open theorem programmes.
- **ME-089–102:** apart from the algebraic bounds above, these are empirical claims and
  cannot be proved in Lean.

