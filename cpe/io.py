"""Explicit schemas, canonical hashes, immutable run records."""
import csv
import hashlib
import json
from pathlib import Path
from .core import finite

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path(__file__).resolve().parent/"registry"

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_manifest():
    paths = sorted((ROOT/"cpe").glob("*.py")) + sorted(REGISTRY.glob("*.json"))
    return {str(p.relative_to(ROOT)):file_hash(p) for p in paths}

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+"\n")

def sealed(obj):
    result = dict(obj)
    result["sha256"] = digest(obj)
    return result

def verify_seal(obj):
    payload = {k:v for k,v in obj.items() if k != "sha256"}
    if obj.get("sha256") != digest(payload):
        raise ValueError("Artifact digest mismatch")
    return payload

def load_data(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if set(reader.fieldnames or []) != {"series", "time", "y", "split", "event"}:
            raise ValueError("CSV headers must be series,time,y,split,event")
        groups = {}
        for row in reader:
            if not row["series"].strip():
                raise ValueError("series cannot be empty")
            if row["split"] not in ("train", "calibration", "test"):
                raise ValueError("split must be train, calibration or test")
            if row["event"] not in ("", "0", "1"):
                raise ValueError("event must be empty (unknown), 0, or 1")
            item = dict(series=row["series"],time=finite(row["time"]),y=finite(row["y"]),
                        split=row["split"],event=None if row["event"]=="" else int(row["event"]))
            groups.setdefault(item["series"], []).append(item)
    if not groups:
        raise ValueError("Dataset is empty")
    for series, rows in groups.items():
        counts = {s:sum(r["split"]==s for r in rows) for s in ("train", "calibration", "test")}
        if counts["train"] < 20 or counts["calibration"] < 20 or counts["test"] < 20:
            raise ValueError(f"{series}: each split needs at least 20 observations")
        split_order = {"train":0, "calibration":1, "test":2}
        dt = rows[1]["time"]-rows[0]["time"]
        if dt <= 0:
            raise ValueError("Times must increase within each series; input is never silently sorted")
        for a,b in zip(rows, rows[1:]):
            if b["time"] <= a["time"] or not abs((b["time"]-a["time"])-dt) <= 1e-8*max(1,abs(dt)):
                raise ValueError("Require strictly increasing, equally spaced times within each series")
            if split_order[b["split"]] < split_order[a["split"]]:
                raise ValueError("Split leakage: require contiguous train -> calibration -> test")
        if any(r["event"] == 1 for r in rows if r["split"] != "test"):
            raise ValueError("Known events in training/calibration require a different explicit protocol")
    return groups

def validate_protocol(p):
    required = {"id","claim","dataset_kind","value_unit","time_unit","decay","epsilon_scale",
                "alpha","min_relative_gain","bootstrap_samples","block_length","seed",
                "max_normal_alert_rate","primary_comparator","equation_ids","sectors","interaction_order"}
    if set(p) != required:
        raise ValueError(f"Protocol keys differ: {sorted(set(p)^required)}")
    if p["dataset_kind"] not in ("synthetic", "external_retrospective"):
        raise ValueError("CSV replay must be synthetic or external_retrospective; use forecast/resolve for future observations")
    if p["primary_comparator"] != "ewma":
        raise ValueError("v0.1 fixes the matched EWMA comparator")
    if not 0 <= finite(p["decay"]) < 1 or finite(p["epsilon_scale"]) <= 0:
        raise ValueError("Invalid recurrence parameters")
    if not 0 < finite(p["alpha"]) < 1 or not 0 <= finite(p["min_relative_gain"]) < 1:
        raise ValueError("Invalid alpha or effect threshold")
    if not 0 <= finite(p["max_normal_alert_rate"]) <= 1:
        raise ValueError("Invalid alert rate")
    for k in ("bootstrap_samples", "block_length", "seed", "interaction_order"):
        if type(p[k]) is not int:
            raise ValueError(f"{k} must be an integer")
    if not 200 <= p["bootstrap_samples"] <= 20000 or p["block_length"] < 1:
        raise ValueError("Require 200..20000 bootstrap samples and positive block length")
    if not p["id"] or not p["claim"] or not p["value_unit"] or not p["time_unit"]:
        raise ValueError("Need experiment identity, claim and units")
    registry = read_json(REGISTRY/"equations.json")
    by_id = {r["id"]:r for r in registry}
    if not isinstance(p["equation_ids"],list) or not p["equation_ids"]:
        raise ValueError("Need an explicit equation binding")
    for eid in p["equation_ids"]:
        if eid not in by_id or by_id[eid]["engine_binding"] != "scalar_coherence_metric":
            raise ValueError(f"{eid} has no executable v0.1 binding")
    if not isinstance(p["sectors"],list) or p["sectors"] or p["interaction_order"] != 0:
        raise ValueError("The v0.1 predictor has no physical-sector dynamics; use the atlas coverage command")
    return p

class Journal:
    def __init__(self, path):
        self.file = Path(path).open("x", encoding="utf-8")
        self.previous = "0"*64
        self.count = 0

    def add(self, kind, data):
        record = {"seq":self.count, "previous":self.previous, "kind":kind, "data":data}
        record = sealed(record)
        self.file.write(canonical(record)+"\n")
        self.file.flush()
        self.previous = record["sha256"]
        self.count += 1
        return record["sha256"]

    def close(self):
        self.file.close()

def verify_journal(path):
    previous = "0"*64
    n = 0
    pending = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        verify_seal(row)
        if row["seq"] != n or row["previous"] != previous:
            raise ValueError("Journal chain is broken")
        if row["kind"] == "forecast":
            if pending is not None or "y" in row["data"]:
                raise ValueError("Invalid prediction/observation ordering")
            pending = (row["data"]["series"], row["data"]["time"])
        elif row["kind"] == "observation":
            if pending != (row["data"]["series"], row["data"]["time"]):
                raise ValueError("Observation has no preceding forecast")
            pending = None
        previous = row["sha256"]
        n += 1
    if pending is not None:
        raise ValueError("Unresolved forecast in completed retrospective run")
    return {"records":n, "head":previous}
