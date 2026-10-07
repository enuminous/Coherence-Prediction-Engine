"""Recreate experiment inputs and integration registries; does not evaluate models."""
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cpe.atlas import atlas

def save(path,obj):
    path=ROOT/path
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")

def csvwrite(path,rows):
    with (ROOT/path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["series","time","y","split","event"])
        writer.writerows(rows)

def main():
    records=json.loads((ROOT/"references/equation-map.json").read_text(encoding="utf-8"))
    for row in records:
        row.update(engine_binding="reference_only",empirical_status="not_validated_by_CPE",
                   source_commit="58f743bd44929049928d0b1d8beee9403c549a0d")
        if row["id"]=="ME-047":
            row.update(engine_binding="scalar_coherence_metric",binding="cpe.core.coherence",
                       assumptions=["finite real observations and forecasts in matching units","epsilon > 0 in those units"],
                       formal_status="Upstream scalar/general-normed-space theorem reference; Lean was not rebuilt for this release.")
        if row["id"]=="ME-102":
            row.update(engine_binding="gate_reference_only",binding=None,
                       missing=["prespecified future failure event and warning lead time", "matched false-alarm comparison",
                                "hardware compute budget", "independent replication"],
                       disposition="NOT_SATISFIED_BY_THIS_RELEASE")
    save("cpe/registry/equations.json",records)
    save("cpe/registry/atlas_165.json",atlas())
    save("cpe/registry/claims.json",[
        dict(id="CPE-C01",claim="All eleven-sector triples are catalogued",status="demonstrated_by_enumeration",
             evidence="python -m cpe atlas",scope="combinatorial coverage only"),
        dict(id="CPE-C02",claim="Forecast at t uses observations only through t-1",status="testable_software_contract",
             evidence="tests/test_engine.py; forecast/observation journals"),
        dict(id="CPE-C03",claim="Coherence gating reduces MAE by at least 5% against matched EWMA",status="hypothesis",
             evidence="Frozen per-dataset protocols and generated results; failures retained"),
        dict(id="CPE-C04",claim="CPE establishes EFMW physical validity",status="unresolved_not_claimed",
             evidence="No physical field equation solver or independent physical test included")])
    save("cpe/registry/zoo_operations.json",[
        dict(operation="TORTOISE",source="https://github.com/enuminous/Tortoise/tree/6658128fd2df96ff6c32fce219bfc9ee3e8876da",
             canonical_purpose="Freeze, predict, score, ablate, replicate without assuming EFMW wins",
             adapter="CPE continuous-target regression adapter v1; not the complete canonical binary classifier",
             inputs=["frozen protocol", "chronological series", "matched comparator", "candidate and ablations"],
             transformation=["train-only AR fit", "calibration-only bands", "causal forecast-before-observation", "held-out scoring"],
             outputs=["predictions", "metrics", "evidence status", "revision proposal", "failure records"],
             pass_criteria="Protocol minimum relative MAE gain (shipped: 5%), bootstrap lower bound > 0, and applicable alert-rate constraint",
             result="Per-run result only; replication remains unresolved",anti_circularity="No outcome-based model selection within a frozen run"),
        dict(operation="OTHER_ZOO_ANIMALS",status="not_run",reason="No invented animal contracts or claim of a complete 46/50-animal pass")])
    save("cpe/registry/source_lock.json",dict(
        monolithic=dict(repository="https://github.com/enuminous/Monlithic_EFMW_102_Lean4",commit="58f743bd44929049928d0b1d8beee9403c549a0d"),
        formalization_102=dict(repository="https://github.com/enuminous/Aristotle-102-Monolithic-Lean",commit="1d89827ccb914d26055feac13229134651d57700"),
        fieldspace=dict(repository="https://github.com/enuminous/Aristotle-165-Einsteinian-Tensors",commit="3053b513ec9ff2f42bba86f1d81694cde98a3d86"),
        tortoise=dict(repository="https://github.com/enuminous/Tortoise",commit="6658128fd2df96ff6c32fce219bfc9ee3e8876da"),
        dataset=dict(url="https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/sunspots/sunspots.csv",
                     git_blob_sha="bf1aec0ce46612fb472d08b66a43115538f405d5",local_sha256=hashlib.sha256((ROOT/"data/sunspots_original.csv").read_bytes()).hexdigest(),
                     documentation="https://www.statsmodels.org/stable/datasets/generated/sunspots.html",license="Public domain",
                     evidence_type="external retrospective observations; not blind or independent replication")))
    for variant in ("control_drift","control_null"):
        rows=[]
        for s in range(12):
            rng=random.Random(530+s)
            y=0.0
            for t in range(600):
                forcing=(1 if s%2==0 else -1)*0.006*max(0,t-375) if variant=="control_drift" else 0.0
                y=0.82*y+0.3+forcing+rng.gauss(0,0.3)
                split="train" if t<200 else "calibration" if t<350 else "test"
                event=int(variant=="control_drift" and t>=375)
                rows.append([f"s{s:02d}",t,format(y,".17g"),split,event])
        csvwrite(f"data/{variant}.csv",rows)
    rows=[]
    with (ROOT/"data/sunspots_original.csv").open(newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            year=int(row["YEAR"])
            split="train" if year<1880 else "calibration" if year<1950 else "test"
            rows.append(["sunspots",year,row["SUNACTIVITY"],split,""])
    csvwrite("data/sunspots.csv",rows)
    for name in ("control_drift","control_null","sunspots"):
        save(f"protocols/{name}.json",dict(
            id=f"CPE-{name}-v1",claim="Lagged ME-047 coherence gating lowers one-step MAE by at least 5% against matched EWMA residual correction.",
            dataset_kind="external_retrospective" if name=="sunspots" else "synthetic",
            value_unit="annual sunspot index (legacy series)" if name=="sunspots" else "arbitrary sensor unit",
            time_unit="year" if name=="sunspots" else "sample",decay=0.97,epsilon_scale=0.01,alpha=0.1,
            min_relative_gain=0.05,bootstrap_samples=1000,block_length=11 if name=="sunspots" else 20,
            seed=20261007,max_normal_alert_rate=0.1,primary_comparator="ewma",equation_ids=["ME-047"],sectors=[],interaction_order=0))
    print("Created 102 equation bindings, 165 atlas entries, three datasets and frozen-design protocols.")

if __name__=="__main__": main()
