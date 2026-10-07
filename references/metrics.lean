module

public import Mathlib

/-!
# Laws of the EFMW metrics: coherence score (ME-047), recursive integrity (ME-048),
phrase entropy (ME-034), Kuramoto synchronisation (ME-091), KL divergence (ME-092),
collapse probabilities (ME-061), Collapse-Ω argmin (ME-059), recursive risk (ME-089).
-/

@[expose] public section

open Real

namespace EFMW

section Coherence

variable {E : Type*} [NormedAddCommGroup E]

/-- ME-047: recursive coherence score `C = 1 − ‖x − m‖ / (‖x‖ + ‖m‖ + ε)`. -/
noncomputable def coherenceScore (x m : E) (ε : ℝ) : ℝ := 1 - ‖x - m‖ / (‖x‖ + ‖m‖ + ε)

/-- ME-047 law: for `ε > 0` the score lies in `[0, 1]`, is symmetric in `x, m`,
and equals `1` exactly when the self-model matches the state (`x = m`). -/
theorem coherenceScore_laws (x m : E) {ε : ℝ} (hε : 0 < ε) :
    0 ≤ coherenceScore x m ε ∧ coherenceScore x m ε ≤ 1 ∧
    coherenceScore x m ε = coherenceScore m x ε ∧
    (coherenceScore x m ε = 1 ↔ x = m) := by
  have hden : 0 < ‖x‖ + ‖m‖ + ε := by positivity
  have htri : ‖x - m‖ ≤ ‖x‖ + ‖m‖ := norm_sub_le x m
  refine ⟨?_, ?_, ?_, ?_⟩
  · unfold coherenceScore
    have : ‖x - m‖ / (‖x‖ + ‖m‖ + ε) ≤ 1 := by
      rw [div_le_one hden]; linarith
    linarith
  · unfold coherenceScore
    have : 0 ≤ ‖x - m‖ / (‖x‖ + ‖m‖ + ε) := by positivity
    linarith
  · unfold coherenceScore; rw [norm_sub_rev, add_comm ‖x‖]
  · unfold coherenceScore
    constructor
    · intro h
      have : ‖x - m‖ / (‖x‖ + ‖m‖ + ε) = 0 := by linarith
      rcases div_eq_zero_iff.1 this with h1 | h1
      · exact sub_eq_zero.1 (norm_eq_zero.1 h1)
      · linarith
    · rintro rfl; simp

/-- ME-048: recursive integrity `I_rec = C · (1 − ‖ẋ − ṁ‖/(‖ẋ‖ + ‖ṁ‖ + ε))`. -/
noncomputable def recursiveIntegrity (x m xd md : E) (ε : ℝ) : ℝ :=
  coherenceScore x m ε * coherenceScore xd md ε

/-- ME-048 law: `0 ≤ I_rec ≤ C ≤ 1`; integrity never exceeds state coherence. -/
theorem recursiveIntegrity_laws (x m xd md : E) {ε : ℝ} (hε : 0 < ε) :
    0 ≤ recursiveIntegrity x m xd md ε ∧
    recursiveIntegrity x m xd md ε ≤ coherenceScore x m ε := by
  obtain ⟨h0, h1, -, -⟩ := coherenceScore_laws x m hε
  obtain ⟨h0', h1', -, -⟩ := coherenceScore_laws xd md hε
  exact ⟨mul_nonneg h0 h0', mul_le_of_le_one_right h0 h1'⟩

end Coherence

/-- ME-091: Kuramoto order parameter `K = (1/N) |Σⱼ e^{iθⱼ}|`. -/
noncomputable def kuramoto {N : ℕ} (θ : Fin N → ℝ) : ℝ :=
  (1 / (N : ℝ)) * ‖∑ j, Complex.exp (θ j * Complex.I)‖

/-- ME-091 law: `0 ≤ K ≤ 1`, and `K = 1` for perfect phase locking. -/
theorem kuramoto_laws {N : ℕ} (hN : 0 < N) (θ : Fin N → ℝ) :
    0 ≤ kuramoto θ ∧ kuramoto θ ≤ 1 ∧ (∀ c, (∀ j, θ j = c) → kuramoto θ = 1) := by
  have hN' : (0 : ℝ) < N := by exact_mod_cast hN
  refine ⟨by unfold kuramoto; positivity, ?_, ?_⟩
  · unfold kuramoto
    have : ‖∑ j, Complex.exp (θ j * Complex.I)‖ ≤ N := by
      refine (norm_sum_le _ _).trans ?_
      simp [Complex.norm_exp_ofReal_mul_I]
    rw [one_div, inv_mul_le_iff₀ hN']; linarith
  · intro c hc
    unfold kuramoto
    simp only [hc, Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
    rw [norm_mul, Complex.norm_exp_ofReal_mul_I]
    simp [hN'.ne']

/-- ME-092 law (Gibbs' inequality): for probability vectors `p, q` with `q > 0`,
`D_KL(P‖Q) = Σ p log(p/q) ≥ 0`. -/
theorem kl_nonneg {n : ℕ} (p q : Fin n → ℝ) (hp : ∀ i, 0 ≤ p i) (hq : ∀ i, 0 < q i)
    (hps : ∑ i, p i = 1) (hqs : ∑ i, q i = 1) :
    0 ≤ ∑ i, p i * log (p i / q i) := by
  have key : ∀ i, p i - q i ≤ p i * log (p i / q i) := by
    intro i
    rcases (hp i).eq_or_lt with h | h
    · rw [← h]; simp [(hq i).le]
    · have h1 := Real.log_le_sub_one_of_pos (div_pos (hq i) h)
      have h2 : log (q i / p i) = - log (p i / q i) := by
        rw [← log_inv, inv_div]
      rw [h2] at h1
      have h3 : p i * (q i / p i - 1) = q i - p i := by field_simp
      nlinarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ Finset.univ) => key i)
  rw [Finset.sum_sub_distrib, hps, hqs, sub_self] at this
  exact this

/-- ME-034: phrase entropy `H = −Σ pᵢ log pᵢ`. -/
noncomputable def phraseEntropy {n : ℕ} (p : Fin n → ℝ) : ℝ := ∑ i, -(p i * log (p i))

/-- ME-034 law: `0 ≤ H ≤ log n` for any probability vector on `n` phrases
(the upper bound follows from Gibbs' inequality against the uniform distribution). -/
theorem phraseEntropy_bounds {n : ℕ} (p : Fin n → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hps : ∑ i, p i = 1) : 0 ≤ phraseEntropy p ∧ phraseEntropy p ≤ log n := by
  have hle1 : ∀ i, p i ≤ 1 := fun i => by
    rw [← hps]
    exact Finset.single_le_sum (fun j _ => hp j) (Finset.mem_univ i)
  refine ⟨Finset.sum_nonneg fun i _ => ?_, ?_⟩
  · have := Real.negMulLog_nonneg (hp i) (hle1 i)
    simpa [Real.negMulLog] using this
  · have hn : 0 < n := by
      rcases Nat.eq_zero_or_pos n with h | h
      · subst h; simp at hps
      · exact h
    have hn' : (0 : ℝ) < n := by exact_mod_cast hn
    have hkl := kl_nonneg p (fun _ => 1 / (n : ℝ)) hp (fun _ => by positivity) hps
      (by simp [Finset.sum_const]; field_simp)
    have e : ∀ i, p i * log (p i / (1 / (n : ℝ))) = p i * log (p i) + p i * log n := by
      intro i
      rcases (hp i).eq_or_lt with h | h
      · rw [← h]; simp
      · rw [div_div_eq_mul_div, div_one, log_mul h.ne' hn'.ne']; ring
    simp only [e, Finset.sum_add_distrib, ← Finset.sum_mul, hps, one_mul] at hkl
    unfold phraseEntropy
    simp only [Finset.sum_neg_distrib]
    linarith

/-- ME-061: collapse probabilities `Pᵢ = |aᵢ|² / Σⱼ |aⱼ|²` from amplitudes `aᵢ = ⟨i|Ω̂|ψ⟩`. -/
noncomputable def collapseProb {n : ℕ} (a : Fin n → ℂ) (i : Fin n) : ℝ :=
  ‖a i‖ ^ 2 / ∑ j, ‖a j‖ ^ 2

/-- ME-061 law (Born compatibility): whenever some amplitude is non-zero, the collapse
probabilities are non-negative and sum to `1`. -/
theorem collapseProb_distribution {n : ℕ} (a : Fin n → ℂ) (ha : ∃ i, a i ≠ 0) :
    (∀ i, 0 ≤ collapseProb a i) ∧ ∑ i, collapseProb a i = 1 := by
  obtain ⟨i0, hi0⟩ := ha
  have hpos : 0 < ∑ j, ‖a j‖ ^ 2 :=
    lt_of_lt_of_le (by positivity : 0 < ‖a i0‖ ^ 2)
      (Finset.single_le_sum (f := fun j => ‖a j‖ ^ 2) (fun j _ => by positivity)
        (Finset.mem_univ i0))
  refine ⟨fun i => by unfold collapseProb; positivity, ?_⟩
  unfold collapseProb
  rw [← Finset.sum_div, div_self hpos.ne']

/-- ME-059 law: on any finite, non-empty set of candidate outcomes `s`, the Collapse-Ω
selection `argmin_s [−ln P(s|ψ) + λ D(s, Φ) − γ R(s)]` is well defined (a minimiser exists). -/
theorem collapseOmega_exists {S : Type*} (outcomes : Finset S) (hne : outcomes.Nonempty)
    (P : S → ℝ) (D R : S → ℝ) (lam γ : ℝ) :
    ∃ s ∈ outcomes, ∀ s' ∈ outcomes,
      -log (P s) + lam * D s - γ * R s ≤ -log (P s') + lam * D s' - γ * R s' :=
  outcomes.exists_min_image (fun s => -log (P s) + lam * D s - γ * R s) hne

/-- ME-089: recursive risk `Risk = P(H)·(1 − C)`. -/
def recursiveRisk (pH C : ℝ) : ℝ := pH * (1 - C)

/-- ME-089 law: with `P(H), C ∈ [0, 1]`, risk lies in `[0, P(H)]`, and is
monotonically non-increasing in coherence `C`. -/
theorem recursiveRisk_laws {pH C C' : ℝ} (hp0 : 0 ≤ pH) (hC0 : 0 ≤ C) (hC1 : C ≤ 1)
    (hCC' : C ≤ C') :
    0 ≤ recursiveRisk pH C ∧ recursiveRisk pH C ≤ pH ∧
      recursiveRisk pH C' ≤ recursiveRisk pH C := by
  unfold recursiveRisk
  refine ⟨mul_nonneg hp0 (by linarith), ?_, ?_⟩
  · nlinarith
  · nlinarith

end EFMW

