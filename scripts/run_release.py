"""Freeze and evaluate every registered demo exactly once into a NEW output root."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cpe.engine import freeze,run,verify_run
from cpe.io import write_json

def main():
    destination=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"runs"
    destination.mkdir(parents=True,exist_ok=False)
    summaries={}
    for name in ("control_drift","control_null","sunspots"):
        receipt_path=destination/f"{name}.freeze.json"
        freeze(ROOT/f"data/{name}.csv",ROOT/f"protocols/{name}.json",receipt_path)
        summary=run(ROOT/f"data/{name}.csv",receipt_path,destination/name)
        verify_run(destination/name)
        summaries[name]=summary
        print(name,summary["primary"]["disposition"],summary["primary"]["relative_gain"])
    write_json(destination/"all_results.json",summaries)

if __name__=="__main__": main()
