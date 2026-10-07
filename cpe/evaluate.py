"""Frozen primary comparison and dependence-aware, descriptive uncertainty."""
import math
import random
import statistics
from .core import MODELS

def percentile(values, q):
    values = sorted(values)
    p = (len(values)-1)*q
    low = math.floor(p)
    high = math.ceil(p)
    return values[low]*(high-p) + values[high]*(p-low) if low != high else values[low]

def paired_bootstrap(groups, samples, block_length, seed):
    """Bootstrap baseline absolute error minus candidate absolute error."""
    rng = random.Random(seed)
    groups = list(groups.values())
    draws = []
    method = "cluster_by_series" if len(groups) >= 5 else "circular_block_within_series"
    for _ in range(samples):
        if method == "cluster_by_series":
            selected = [rng.choice(groups) for _ in groups]
            deltas = [v for g in selected for v in g]
        else:
            deltas = []
            for group in groups:
                draw = []
                while len(draw) < len(group):
                    start = rng.randrange(len(group))
                    draw.extend(group[(start+j)%len(group)] for j in range(min(block_length,len(group))))
                deltas.extend(draw[:len(group)])
        draws.append(statistics.mean(deltas))
    return dict(method=method, samples=samples, seed=seed, block_length=block_length,
                mean_gain_95pct_interval=[percentile(draws,0.025),percentile(draws,0.975)],
                interpretation="Descriptive resampling interval; dependence and representativeness assumptions apply.")

def summarize(rows, protocol):
    if not rows:
        raise ValueError("No test predictions")
    metrics = {}
    for name in MODELS:
        errors = [r["y"]-r["predictions"][name] for r in rows]
        metrics[name] = dict(mae=statistics.mean(map(abs,errors)),
                             rmse=math.sqrt(statistics.mean(e*e for e in errors)),
                             bias=statistics.mean(errors),
                             interval_coverage=statistics.mean(abs(e)<=r["radii"][name] for e,r in zip(errors,rows)),
                             mean_interval_width=statistics.mean(2*r["radii"][name] for r in rows))
    differences = {}
    for r in rows:
        differences.setdefault(r["series"],[]).append(
            abs(r["y"]-r["predictions"]["ewma"])-abs(r["y"]-r["predictions"]["cpe"]))
    uncertainty = paired_bootstrap(differences, protocol["bootstrap_samples"], protocol["block_length"], protocol["seed"])
    baseline = metrics["ewma"]["mae"]
    gain = baseline-metrics["cpe"]["mae"]
    relative_gain = gain/baseline if baseline > 0 else None
    normals = [r for r in rows if r["event"] == 0]
    events = [r for r in rows if r["event"] == 1]
    fpr = statistics.mean(r["diagnostic_alert"] for r in normals) if normals else None
    recall = statistics.mean(r["diagnostic_alert"] for r in events) if events else None
    label_coverage = sum(r["event"] is not None for r in rows)/len(rows)
    quality = fpr is None or fpr <= protocol["max_normal_alert_rate"]
    lo, hi = uncertainty["mean_gain_95pct_interval"]
    effect = relative_gain is not None and relative_gain >= protocol["min_relative_gain"]
    if not quality:
        disposition = "rejected_on_alert_rate"
    elif effect and lo > 0:
        disposition = "supported_in_this_benchmark"
    elif hi < 0:
        disposition = "rejected_on_predictive_performance"
    else:
        disposition = "not_supported"
    return dict(n=len(rows),series=len(differences),models=metrics,
                primary=dict(candidate="cpe",comparator="ewma",metric="MAE",absolute_gain=gain,
                             relative_gain=relative_gain,min_required_relative_gain=protocol["min_relative_gain"],
                             alert_constraint="not_evaluated_without_normal_labels" if fpr is None else "passed" if quality else "failed",
                             uncertainty=uncertainty,disposition=disposition),
                diagnostics=dict(normal_alert_rate=fpr,event_detection_rate=recall,label_coverage=label_coverage,
                                 evaluated_normal_rows=len(normals),evaluated_event_rows=len(events),
                                 note="Post-observation residual alerts are diagnostics, not forecasts of future events."),
                nominal_interval_coverage=1-protocol["alpha"],
                evidence_scope=protocol["dataset_kind"],
                physical_validation=False,independent_replication=False)

def revision_proposal(summary, protocol, freeze_hash):
    state = summary["primary"]["disposition"]
    success = state == "supported_in_this_benchmark"
    return dict(parent_freeze=freeze_hash,parent_protocol=protocol["id"],
                disposition=state,action="seek_independent_replication" if success else "reject_advantage_claim_for_this_run",
                next_model="unchanged cpe" if success else "ewma",
                rationale=("Replicate without retuning on new observations." if success else
                           "Retain the matched conventional baseline as the working alternative; do not rewrite this result."),
                automatic_parameter_change=False,new_experiment_required=True,
                next_test="Freeze a new protocol and use newly collected or separately held-out observations.",
                prohibited_reuse="These test outcomes are now development evidence, not a fresh confirmation set.")
