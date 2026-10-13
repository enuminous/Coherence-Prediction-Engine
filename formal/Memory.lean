import Mathlib

namespace CPE
open Finset Filter
open scoped Topology

/-- `r n` is the next residual, consumed in the update from n to n+1. -/
noncomputable def memory (λ : ℝ) (r : ℕ → ℝ) (m₀ : ℝ) : ℕ → ℝ
  | 0 => m₀
  | n + 1 => λ * memory λ r m₀ n + (1 - λ) * r n

theorem memory_closed (λ : ℝ) (r : ℕ → ℝ) (m₀ : ℝ) (n : ℕ) :
    memory λ r m₀ n = λ ^ n * m₀ +
      (1 - λ) * ∑ j ∈ range n, λ ^ (n - 1 - j) * r j := by
  induction n with
  | zero => simp [memory]
  | succ n ih =>
    rw [memory, ih, sum_range_succ]
    simp only [Nat.add_sub_cancel_right, Nat.sub_self, pow_zero, one_mul]
    have hs : (∑ j ∈ range n, λ ^ (n - j) * r j) =
        λ * ∑ j ∈ range n, λ ^ (n - 1 - j) * r j := by
      rw [mul_sum]
      apply sum_congr rfl
      intro j hj
      have he : n - j = (n - 1 - j) + 1 := by have := mem_range.mp hj; omega
      rw [he, pow_succ]
      ring
    rw [hs, pow_succ]
    ring

theorem memory_bound (λ R m₀ : ℝ) (r : ℕ → ℝ)
    (hλ : 0 ≤ λ) (hλ1 : λ ≤ 1) (hr : ∀ j, |r j| ≤ R) (n : ℕ) :
    |memory λ r m₀ n| ≤ λ ^ n * |m₀| + (1 - λ ^ n) * R := by
  induction n with
  | zero => simp [memory]
  | succ n ih =>
    calc
      |memory λ r m₀ (n + 1)| ≤ |λ * memory λ r m₀ n| + |(1 - λ) * r n| := abs_add _ _
      _ = λ * |memory λ r m₀ n| + (1 - λ) * |r n| := by
        rw [abs_mul, abs_mul, abs_of_nonneg hλ, abs_of_nonneg (sub_nonneg.mpr hλ1)]
      _ ≤ λ * (λ ^ n * |m₀| + (1 - λ ^ n) * R) + (1 - λ) * R :=
        add_le_add (mul_le_mul_of_nonneg_left ih hλ)
          (mul_le_mul_of_nonneg_left (hr n) (sub_nonneg.mpr hλ1))
      _ = λ ^ (n + 1) * |m₀| + (1 - λ ^ (n + 1)) * R := by rw [pow_succ]; ring

theorem same_inputs_difference (λ a b : ℝ) (r : ℕ → ℝ) (n : ℕ) :
    memory λ r a n - memory λ r b n = λ ^ n * (a - b) := by
  induction n with
  | zero => simp [memory]
  | succ n ih =>
    simp only [memory]
    calc
      _ = λ * (memory λ r a n - memory λ r b n) := by ring
      _ = _ := by rw [ih, pow_succ]; ring

theorem forgets_initial_state (λ a b : ℝ) (r : ℕ → ℝ)
    (hλ : 0 ≤ λ) (hλ1 : λ < 1) :
    Tendsto (fun n => memory λ r a n - memory λ r b n) atTop (𝓝 0) := by
  simp only [same_inputs_difference]
  simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one hλ hλ1).mul_const (a - b)

theorem causal (λ m₀ : ℝ) (r s : ℕ → ℝ) (n : ℕ)
    (h : ∀ j < n, r j = s j) : memory λ r m₀ n = memory λ s m₀ n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [memory, memory, h n (by omega), ih (fun j hj => h j (by omega))]

theorem gated_bound (C m : ℝ) (hC : |C| ≤ 1) : |C * m| ≤ |m| := by
  rw [abs_mul]
  simpa using mul_le_mul_of_nonneg_right hC (abs_nonneg m)

end CPE
