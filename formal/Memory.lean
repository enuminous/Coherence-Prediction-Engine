import Mathlib

namespace CPE
open Finset Filter
open scoped Topology

/-- `r n` is the next residual, consumed in the update from n to n+1. -/
noncomputable def memory (lam : ℝ) (r : ℕ → ℝ) (m₀ : ℝ) : ℕ → ℝ
  | 0 => m₀
  | n + 1 => lam * memory lam r m₀ n + (1 - lam) * r n

theorem memory_closed (lam : ℝ) (r : ℕ → ℝ) (m₀ : ℝ) (n : ℕ) :
    memory lam r m₀ n = lam ^ n * m₀ +
      (1 - lam) * ∑ j ∈ range n, lam ^ (n - 1 - j) * r j := by
  induction n with
  | zero => simp [memory]
  | succ n ih =>
    rw [memory, ih, sum_range_succ]
    simp only [Nat.add_sub_cancel_right, Nat.sub_self, pow_zero, one_mul]
    have hs : (∑ j ∈ range n, lam ^ (n - j) * r j) =
        lam * ∑ j ∈ range n, lam ^ (n - 1 - j) * r j := by
      rw [mul_sum]
      apply sum_congr rfl
      intro j hj
      have he : n - j = (n - 1 - j) + 1 := by have := mem_range.mp hj; omega
      rw [he, pow_succ]
      ring
    rw [hs, pow_succ]
    ring

theorem memory_bound (lam R m₀ : ℝ) (r : ℕ → ℝ)
    (hlam : 0 ≤ lam) (hlam1 : lam ≤ 1) (hr : ∀ j, |r j| ≤ R) (n : ℕ) :
    |memory lam r m₀ n| ≤ lam ^ n * |m₀| + (1 - lam ^ n) * R := by
  induction n with
  | zero => simp [memory]
  | succ n ih =>
    calc
      |memory lam r m₀ (n + 1)| ≤ |lam * memory lam r m₀ n| + |(1 - lam) * r n| := abs_add _ _
      _ = lam * |memory lam r m₀ n| + (1 - lam) * |r n| := by
        rw [abs_mul, abs_mul, abs_of_nonneg hlam, abs_of_nonneg (sub_nonneg.mpr hlam1)]
      _ ≤ lam * (lam ^ n * |m₀| + (1 - lam ^ n) * R) + (1 - lam) * R :=
        add_le_add (mul_le_mul_of_nonneg_left ih hlam)
          (mul_le_mul_of_nonneg_left (hr n) (sub_nonneg.mpr hlam1))
      _ = lam ^ (n + 1) * |m₀| + (1 - lam ^ (n + 1)) * R := by rw [pow_succ]; ring

theorem same_inputs_difference (lam a b : ℝ) (r : ℕ → ℝ) (n : ℕ) :
    memory lam r a n - memory lam r b n = lam ^ n * (a - b) := by
  induction n with
  | zero => simp [memory]
  | succ n ih =>
    simp only [memory]
    calc
      _ = lam * (memory lam r a n - memory lam r b n) := by ring
      _ = _ := by rw [ih, pow_succ]; ring

theorem forgets_initial_state (lam a b : ℝ) (r : ℕ → ℝ)
    (hlam : 0 ≤ lam) (hlam1 : lam < 1) :
    Tendsto (fun n => memory lam r a n - memory lam r b n) atTop (𝓝 0) := by
  simp only [same_inputs_difference]
  simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one hlam hlam1).mul_const (a - b)

theorem causal (lam m₀ : ℝ) (r s : ℕ → ℝ) (n : ℕ)
    (h : ∀ j < n, r j = s j) : memory lam r m₀ n = memory lam s m₀ n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [memory, memory, h n (by omega), ih (fun j hj => h j (by omega))]

theorem gated_bound (C m : ℝ) (hC : |C| ≤ 1) : |C * m| ≤ |m| := by
  rw [abs_mul]
  simpa using mul_le_mul_of_nonneg_right hC (abs_nonneg m)

end CPE
