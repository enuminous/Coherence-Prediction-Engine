import Mathlib

/-!
# Independent check of the FieldSpace structural theorems

The upstream Lean files mostly check bare arithmetic identities (`Nat.choose 11 3 = 165`,
`8 = 8`, ...). Here the corresponding claims are stated about the actual objects: the
11 sectors `E M S F W T I R H P A` and the set of all 3-element subsets of them.
-/

namespace FieldSpaceCheck

/-- The 11 sectors, in the source order `E, M, S, F, W, T, I, R, H, P, A`. -/
inductive Sector
  | E | M | S | F | W | T | I | R | H | P | A
  deriving DecidableEq, Fintype, Repr

open Sector

/-- Sector kinds: gravity `E`, gauge `M, S`, and eight scalar sectors. -/
def isGauge (s : Sector) : Bool := s = M || s = S
def isScalar (s : Sector) : Bool := !(s = E) && !isGauge s

/-- The atlas: every 3-element set of sectors. -/
def triplets : Finset (Finset Sector) := Finset.univ.powersetCard 3

/-- FS-T01: there are 165 triplets. -/
theorem triplets_card : triplets.card = 165 := by native_decide

/-- FS-T02: every sector lies in exactly 45 triplets. -/
theorem sector_incidence (s : Sector) : (triplets.filter (s ∈ ·)).card = 45 := by
  revert s; native_decide

/-- FS-T03: every pair of distinct sectors lies in exactly 9 triplets. -/
theorem pair_incidence (s t : Sector) (h : s ≠ t) :
    (triplets.filter (fun x => s ∈ x ∧ t ∈ x)).card = 9 := by
  revert s t; native_decide

/-- Kind profile of a triplet: (has gravity, number of gauge sectors, number of scalars). -/
def profile (x : Finset Sector) : Bool × ℕ × ℕ :=
  (decide (E ∈ x), (x.filter (isGauge ·)).card, (x.filter (isScalar ·)).card)

/-- FS-T04: the six-class decomposition `56 + 56 + 28 + 16 + 8 + 1 = 165`. -/
theorem class_counts :
    (triplets.filter (profile · = (false, 0, 3))).card = 56 ∧
    (triplets.filter (profile · = (false, 1, 2))).card = 56 ∧
    (triplets.filter (profile · = (true, 0, 2))).card = 28 ∧
    (triplets.filter (profile · = (true, 1, 1))).card = 16 ∧
    (triplets.filter (profile · = (false, 2, 1))).card = 8 ∧
    (triplets.filter (profile · = (true, 2, 0))).card = 1 := by
  native_decide

/-- The six classes exhaust the atlas. -/
theorem classes_exhaustive : ∀ x ∈ triplets, profile x ∈
    ({(false, 0, 3), (false, 1, 2), (true, 0, 2), (true, 1, 1), (false, 2, 1), (true, 2, 0)} :
      Finset (Bool × ℕ × ℕ)) := by
  native_decide

/-- Expected statement count of a fully populated block under the source grammar:
one Einstein equation if `E` is present, two statements (dynamics + Bianchi) per gauge
sector, and one scalar equation per scalar sector. -/
def statements (x : Finset Sector) : ℕ :=
  (if E ∈ x then 1 else 0) + 2 * (x.filter (isGauge ·)).card + (x.filter (isScalar ·)).card

/-- FS-T05: the inventory `45 + 90 + 90 + 360 = 585`. -/
theorem statement_inventory :
    (triplets.filter (E ∈ ·)).card = 45 ∧
    (∑ x ∈ triplets, (x.filter (isGauge ·)).card) = 90 ∧
    (∑ x ∈ triplets, (x.filter (isScalar ·)).card) = 360 ∧
    (∑ x ∈ triplets, statements x) = 585 := by
  native_decide

/-- FS-T06: deleting a set `D` of `k` sectors leaves `C(11-k,3)` triplets, all of which
are exactly the triplets of the remaining sectors (closure under vertex deletion). -/
theorem ablation (D : Finset Sector) :
    (triplets.filter (fun x => Disjoint x D)).card = Nat.choose (11 - D.card) 3 := by
  have : triplets.filter (fun x => Disjoint x D) = (Finset.univ \ D).powersetCard 3 := by
    ext x
    simp [triplets, Finset.mem_powersetCard, Finset.subset_sdiff, and_comm]
  rw [this, Finset.card_powersetCard, Finset.card_sdiff_of_subset (Finset.subset_univ _)]
  rfl

/-- FS-T07: overlap spectrum of unordered pairs of distinct triplets
(sharing 2 / 1 / 0 sectors): `1980 + 6930 + 4620 = 13530`. -/
theorem overlap_spectrum :
    let pairs := triplets.offDiag
    (pairs.filter (fun p => (p.1 ∩ p.2).card = 2)).card = 2 * 1980 ∧
    (pairs.filter (fun p => (p.1 ∩ p.2).card = 1)).card = 2 * 6930 ∧
    (pairs.filter (fun p => (p.1 ∩ p.2).card = 0)).card = 2 * 4620 ∧
    pairs.card = 2 * 13530 := by
  native_decide

/-! ## Candidate law FS-C02 (master-action reciprocity), in its simplest form

If the `i`–`j` pair coupling comes from a bilinear potential term `λ φ_i φ_j`, the
coefficient of `φ_j` in the `φ_i` equation equals the coefficient of `φ_i` in the `φ_j`
equation. -/
theorem bilinear_reciprocity (lam a b : ℝ) :
    HasDerivAt (fun x => lam * x * b) (lam * b) a ∧
    HasDerivAt (fun y => lam * a * y) (lam * a) b := by
  constructor
  · simpa using ((hasDerivAt_id a).const_mul lam).mul_const b
  · simpa using (hasDerivAt_id b).const_mul (lam * a)

end FieldSpaceCheck

