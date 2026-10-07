"""Freeze -> causal prediction -> score -> ablate -> revision proposal."""
import csv
import datetime
import platform
from pathlib import Path
from .core import MODELS, Tracker, initialize, calibration_radius
from .io import (canonical,digest,file_hash,read_json,write_json,sealed,verify_seal,
                 source_manifest,load_data,validate_protocol,Journal,verify_journal,ROOT)
from .evaluate import summarize,revision_proposal
from .atlas import verify_atlas

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def freeze(data_path, protocol_path, output):
    groups = load_data(data_path)
    protocol = validate_protocol(read_json(protocol_path))
    # Freeze stores bytes identities and split boundaries, never fitted test statistics.
    receipt = sealed(dict(format="cpe-freeze-v1",created_utc=utcnow(),
                          protocol=protocol,data_sha256=file_hash(data_path),
                          source_files=source_manifest(),
                          splits={s:{split:[r["time"] for r in rows if r["split"]==split]
                                     for split in ("train","calibration","test")} for s,rows in groups.items()},
                          runtime=dict(python=platform.python_version(),platform=platform.platform()),
                          chronology="Local receipt only; no external timestamp or blinded holdout attestation.",
                          interpretation="Retrospective files may already be known; a hash does not create independent evidence."))
    write_json(output,receipt)
    return receipt

def check_freeze(data_path, receipt):
    verify_seal(receipt)
    if receipt["format"] != "cpe-freeze-v1":
        raise ValueError("Unsupported freeze format")
    validate_protocol(receipt["protocol"])
    if source_manifest() != receipt["source_files"]:
        raise ValueError("Source or registry changed after freeze; create a NEW experiment")
    if file_hash(data_path) != receipt["data_sha256"]:
        raise ValueError("Dataset changed after freeze")

def calibrate(rows, protocol):
    training = [r["y"] for r in rows if r["split"] == "train"]
    tracker = initialize(training,protocol["decay"],protocol["epsilon_scale"])
    errors = {name:[] for name in MODELS}
    diagnostics = []
    for row in rows:
        if row["split"] != "calibration":
            continue
        predictions = tracker.predict()
        for name in MODELS:
            errors[name].append(abs(row["y"]-predictions[name]))
        diagnostics.append(abs(tracker.observe(row["y"])["memory"]))
    radii = {name:calibration_radius(errors[name],protocol["alpha"]) for name in MODELS}
    threshold = calibration_radius(diagnostics,protocol["alpha"])
    return tracker,radii,threshold

def run(data_path, freeze_path, output):
    receipt = read_json(freeze_path)
    check_freeze(data_path,receipt)
    protocol = receipt["protocol"]
    groups = load_data(data_path)
    output = Path(output)
    output.mkdir(parents=True,exist_ok=False)
    write_json(output/"freeze.json",receipt)
    journal = Journal(output/"events.jsonl")
    rows_out = []
    checkpoints = {}
    initial_checkpoints = {}
    try:
        journal.add("freeze",{"freeze_hash":receipt["sha256"]})
        for series, rows in groups.items():
            tracker,radii,threshold = calibrate(rows,protocol)
            before_test = [r for r in rows if r["split"] != "test"][-1]
            dt = rows[1]["time"]-rows[0]["time"]
            checkpoint = sealed(dict(format="cpe-checkpoint-v1",series=series,tracker=tracker.to_dict(),
                                     last_time=before_test["time"],time_step=dt,radii=radii,
                                     diagnostic_threshold=threshold,protocol=protocol,freeze_hash=receipt["sha256"],
                                     source_files=receipt["source_files"],previous_resolution=None))
            initial_checkpoints[series] = checkpoint
            last_time = before_test["time"]
            for row in rows:
                if row["split"] != "test":
                    continue
                predictions = tracker.predict()
                # This append is flushed before observe() accepts y_t.
                journal.add("forecast",dict(series=series,time=row["time"],origin_time=last_time,
                                             predictions=predictions,radii=radii,
                                             lagged_coherence=tracker.last_coherence))
                observed = tracker.observe(row["y"])
                alert = abs(observed["memory"]) > threshold
                journal.add("observation",dict(series=series,time=row["time"],y=row["y"],event=row["event"],
                                                diagnostics=observed,diagnostic_alert=alert))
                rows_out.append(dict(series=series,time=row["time"],y=row["y"],event=row["event"],
                                     predictions=predictions,radii=radii,diagnostic_alert=alert,
                                     coherence=observed["coherence"],memory=observed["memory"]))
                last_time = row["time"]
            final_checkpoint = {k:v for k,v in checkpoint.items() if k != "sha256"}
            final_checkpoint.update(tracker=tracker.to_dict(),last_time=last_time)
            checkpoints[series] = sealed(final_checkpoint)
        summary = summarize(rows_out,protocol)
        summary["freeze_hash"] = receipt["sha256"]
        summary["protocol_id"] = protocol["id"]
        journal.add("evaluation",summary)
        revision = revision_proposal(summary,protocol,receipt["sha256"])
        journal.add("revision",revision)
    except Exception as exc:
        journal.add("run_failed",{"type":type(exc).__name__,"message":str(exc)})
        journal.close()
        write_json(output/"FAILED.json",dict(error=str(exc),status="incomplete_invalid"))
        raise
    journal.close()
    audit = dict(journal=verify_journal(output/"events.jsonl"),atlas=verify_atlas(),
                 source_and_data_freeze="verified",forecast_before_observation=True,
                 zoo_scope="TORTOISE-derived regression adapter; other Zoo animals not asserted as run",
                 empirical_independence="external retrospective data" if protocol["dataset_kind"]=="external_retrospective" else protocol["dataset_kind"],
                 novelty="AR(1), EWMA and empirical intervals are established methods; the gate is an experimental combination.")
    write_json(output/"summary.json",summary)
    write_json(output/"audit.json",audit)
    write_json(output/"revision.json",revision)
    write_json(output/"checkpoints.json",checkpoints)
    write_json(output/"checkpoints_before_test.json",initial_checkpoints)
    with (output/"predictions.csv").open("x",newline="",encoding="utf-8") as f:
        fields = ["series","time","y","event","diagnostic_alert","coherence","memory"] + list(MODELS)
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for row in rows_out:
            writer.writerow({**{k:row[k] for k in fields if k not in MODELS},**row["predictions"]})
    from .report import render_report
    (output/"report.html").write_text(render_report(summary,protocol,rows_out,revision),encoding="utf-8")
    files = {p.name:file_hash(p) for p in sorted(output.iterdir()) if p.is_file()}
    write_json(output/"manifest.json",sealed(dict(format="cpe-run-manifest-v1",files=files)))
    return summary

def verify_run(output):
    output = Path(output)
    manifest = read_json(output/"manifest.json")
    verify_seal(manifest)
    for filename,expected in manifest["files"].items():
        if Path(filename).name != filename or file_hash(output/filename) != expected:
            raise ValueError(f"Run artifact changed: {filename}")
    journal = verify_journal(output/"events.jsonl")
    expected_head = read_json(output/"audit.json")["journal"]["head"]
    if journal["head"] != expected_head:
        raise ValueError("Journal head mismatch")
    return dict(verified=True,files=len(manifest["files"]),journal=journal)

def make_ticket(checkpoint, output):
    verify_seal(checkpoint)
    if checkpoint["format"] != "cpe-checkpoint-v1":
        raise ValueError("Expected a checkpoint")
    if checkpoint["source_files"] != source_manifest():
        raise ValueError("Checkpoint was made with different code/registry")
    tracker = Tracker(**checkpoint["tracker"])
    ticket = sealed(dict(format="cpe-prediction-v1",created_utc=utcnow(),checkpoint=checkpoint,
                         series=checkpoint["series"],time=checkpoint["last_time"]+checkpoint["time_step"],
                         predictions=tracker.predict(),radii=checkpoint["radii"],
                         warning="Local timestamp; publish this ticket before the outcome for externally attestable chronology."))
    write_json(output,ticket)
    return ticket

def resolve_ticket(ticket_path, observation_path, output):
    ticket = read_json(ticket_path)
    verify_seal(ticket)
    checkpoint = ticket["checkpoint"]
    verify_seal(checkpoint)
    if checkpoint["source_files"] != source_manifest():
        raise ValueError("Source changed since forecast")
    observation = read_json(observation_path)
    if set(observation) != {"series","time","y","source"} or not observation["source"]:
        raise ValueError("Observation requires series,time,y,source")
    if observation["series"] != ticket["series"] or observation["time"] != ticket["time"]:
        raise ValueError("Observation does not resolve this forecast")
    from .core import finite
    y = finite(observation["y"])
    tracker = Tracker(**checkpoint["tracker"])
    if tracker.predict() != ticket["predictions"]:
        raise ValueError("Ticket predictions do not match frozen state")
    diagnostics = tracker.observe(y)
    after = {k:v for k,v in checkpoint.items() if k != "sha256"}
    after.update(tracker=tracker.to_dict(),last_time=ticket["time"],previous_resolution=digest(observation))
    after = sealed(after)
    result = sealed(dict(format="cpe-resolution-v1",ticket_sha256=ticket["sha256"],observation=observation,
                         absolute_errors={k:abs(y-v) for k,v in ticket["predictions"].items()},
                         diagnostics=diagnostics,checkpoint=after,
                         evidence_status="Source assertion supplied by operator; independent collection is not automatically verified."))
    write_json(output,result)
    return result
