import argparse
import json
import sys
from .io import ROOT,REGISTRY,read_json,write_json
from .engine import freeze,run,verify_run,make_ticket,resolve_ticket
from .atlas import verify_atlas,coverage

def main(argv=None):
    parser=argparse.ArgumentParser(prog="python -m cpe",description="Coherence Prediction Engine v0.1.0")
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("freeze",help="Freeze source, registry, protocol, dataset and splits")
    p.add_argument("--data",required=True);p.add_argument("--protocol",required=True);p.add_argument("--out",required=True)
    p=sub.add_parser("run",help="Run a frozen chronological benchmark")
    p.add_argument("--data",required=True);p.add_argument("--freeze",required=True);p.add_argument("--out",required=True)
    p=sub.add_parser("verify",help="Check all run files and journal linkage")
    p.add_argument("run_directory")
    p=sub.add_parser("atlas",help="Inspect all 165 triples and higher-order coverage gaps")
    p.add_argument("--sectors",nargs="*");p.add_argument("--order",type=int,default=3)
    p=sub.add_parser("catalog",help="Read a source equation and its implementation status")
    p.add_argument("equation_id",nargs="?")
    p=sub.add_parser("forecast",help="Issue a ticket from a checkpoint before receiving the outcome")
    p.add_argument("--checkpoint",required=True);p.add_argument("--series");p.add_argument("--out",required=True)
    p=sub.add_parser("resolve",help="Score an issued ticket and produce the next checkpoint")
    p.add_argument("--ticket",required=True);p.add_argument("--observation",required=True);p.add_argument("--out",required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=="freeze":
            value=freeze(args.data,args.protocol,args.out)
            result={"freeze":args.out,"sha256":value["sha256"]}
        elif args.command=="run":
            value=run(args.data,args.freeze,args.out)
            result={"report":str(args.out)+"/report.html","primary":value["primary"]}
        elif args.command=="verify":
            result=verify_run(args.run_directory)
        elif args.command=="atlas":
            result=coverage(args.sectors,args.order) if args.sectors is not None else verify_atlas()
        elif args.command=="catalog":
            entries=read_json(REGISTRY/"equations.json")
            if args.equation_id:
                selected=[r for r in entries if r["id"]==args.equation_id]
                if not selected: raise ValueError("Unknown equation ID")
                result=selected[0]
            else:
                result={"equations":len(entries),"bindings":{r["id"]:r["engine_binding"] for r in entries if r["engine_binding"]!="reference_only"}}
        elif args.command=="forecast":
            checkpoint=read_json(args.checkpoint)
            if args.series: checkpoint=checkpoint[args.series]
            elif checkpoint.get("format")=="cpe-resolution-v1": checkpoint=checkpoint["checkpoint"]
            value=make_ticket(checkpoint,args.out)
            result={"ticket":args.out,"time":value["time"],"predictions":value["predictions"]}
        else:
            value=resolve_ticket(args.ticket,args.observation,args.out)
            result={"resolution":args.out,"errors":value["absolute_errors"]}
        print(json.dumps(result,indent=2,allow_nan=False))
        return 0
    except (ValueError,KeyError,OSError,TypeError,OverflowError) as exc:
        print(f"CPE error: {exc}",file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
