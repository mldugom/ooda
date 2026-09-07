from __future__ import annotations
import argparse, datetime as dt, json, sys, uuid
from pathlib import Path

ROLES={"controller","researcher","product-strategist","architect","engineer","validator","portfolio-manager","trader","risk-manager"}
LENSES={"boyd","stanley-lehman","taleb","scientific","statistical","model-risk","value-of-information","causal-mechanism","market-microstructure","portfolio","reliability-systems","product-user","security-abuse"}
CLAIMS={"discovery","evidence","qualification","n-a"}
PROJECT_CLASSES={"quantitative-research","trading-research","data-ml-system","software-product","analytical-product","infrastructure"}

def dump(path:Path,data:dict):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
def load(path:Path)->dict:
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ValueError(f"{path}: expected JSON object")
    return data

def validate_project(d):
    e=[]
    if d.get("schema")!="ooda/project/v1": e.append("schema must be ooda/project/v1")
    if not d.get("project_id"): e.append("project_id is required")
    if d.get("project_class") not in PROJECT_CLASSES: e.append("unknown project_class")
    if not isinstance(d.get("authority"),dict): e.append("authority object is required")
    return e

def validate_work_order(d):
    e=[]
    if d.get("schema")!="ooda/work-order/v1": e.append("schema must be ooda/work-order/v1")
    for k in ("id","project_id","objective","role","profile","claim_level"):
        if not d.get(k): e.append(f"{k} is required")
    if d.get("role") not in ROLES: e.append("unknown role")
    if d.get("claim_level") not in CLAIMS: e.append("unknown claim_level")
    ls=d.get("lenses") or []
    if not isinstance(ls,list): e.append("lenses must be a list")
    else:
        u=[x for x in ls if x not in LENSES]
        if u: e.append("unknown lenses: "+", ".join(u))
        if len(ls)>3: e.append("normally no more than three lenses per bounded action")
    if not isinstance(d.get("authority"),dict): e.append("authority object is required")
    return e

def validate_trace(d):
    e=[]
    if d.get("schema")!="ooda/trace/v1": e.append("schema must be ooda/trace/v1")
    if not d.get("work_order_id"): e.append("work_order_id is required")
    if not d.get("project_id"): e.append("project_id is required")
    if not isinstance(d.get("ooda"),dict): e.append("ooda object is required")
    if not isinstance(d.get("result"),dict): e.append("result object is required")
    return e

def validate_file(path):
    d=load(path); s=d.get("schema")
    if s=="ooda/project/v1": return validate_project(d)
    if s=="ooda/work-order/v1": return validate_work_order(d)
    if s=="ooda/trace/v1": return validate_trace(d)
    return [f"unknown schema: {s!r}"]

def cmd_init(a):
    t=Path(a.path)/".ooda"/"project.json"
    if t.exists() and not a.force: print(f"Refusing to overwrite {t}; use --force",file=sys.stderr); return 2
    d={"schema":"ooda/project/v1","project_id":a.project_id,"project_class":a.project_class,"authority":{"integration_owner":"human","self_merge":False,"live_capital":False},"state_sources":["AGENTS.md","PROJECT_STATE.md","README.md"],"execution":{"current_provider":"grok","existing_lifecycle":"preserve"},"monitor":{"enabled":False}}
    dump(t,d); print(t); return 0

def cmd_doctor(a):
    b=Path(a.path); p=b/".ooda"/"project.json"
    if not p.exists(): print(f"MISSING {p}",file=sys.stderr); return 2
    e=validate_file(p)
    if e:
        [print(f"FAIL {x}") for x in e]; return 1
    print(f"PASS {p}")
    for rel in ("AGENTS.md","PROJECT_STATE.md","README.md"):
        q=b/rel; print(("FOUND " if q.exists() else "INFO  ")+str(q))
    return 0

def cmd_work_order(a):
    ls=[x.strip() for x in a.lenses.split(",") if x.strip()]
    d={"schema":"ooda/work-order/v1","id":a.id or f"ooda-{dt.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}","project_id":a.project_id or Path.cwd().name,"objective":a.objective,"role":a.role,"profile":a.profile,"lenses":ls,"claim_level":a.claim_level,"scope":{"allowed":[],"forbidden":[]},"verification":[],"budget":{"max_turns":a.max_turns,"max_investigation_steps":a.max_investigation_steps},"stop_conditions":["current durable state conflicts with task assumptions","objective materially changes","required authority is not granted","budget is exhausted"],"authority":{"may_merge":False,"may_promote_model":False,"may_modify_live_runtime":False,"may_spend_real_money":False}}
    e=validate_work_order(d)
    if e: [print(f"FAIL {x}",file=sys.stderr) for x in e]; return 2
    t=Path(a.output); dump(t,d); print(t); return 0

def cmd_trace(a):
    wo=load(Path(a.work_order)); e=validate_work_order(wo)
    if e: [print(f"FAIL work order: {x}",file=sys.stderr) for x in e]; return 2
    d={"schema":"ooda/trace/v1","work_order_id":wo["id"],"project_id":wo["project_id"],"provider":a.provider,"role":wo["role"],"profile":wo["profile"],"lenses":wo.get("lenses",[]),"claim_level":wo["claim_level"],"ooda":{"observe":"","orient":"","decide":"","act":""},"result":{"state":a.result_state,"summary":a.summary},"verification":{"status":"not_recorded","tests":[],"artifacts":[]},"economics":{"turns":None,"tool_calls":None,"cost_usd":None},"next_gate":"Human/ChatGPT review"}
    t=Path(a.output); dump(t,d); print(t); return 0

def cmd_validate(a):
    e=validate_file(Path(a.file))
    if e: [print(f"FAIL {x}") for x in e]; return 1
    print("PASS"); return 0

def parser():
    p=argparse.ArgumentParser(prog="ooda"); s=p.add_subparsers(required=True)
    q=s.add_parser("init"); q.add_argument("--project-id",required=True); q.add_argument("--project-class",required=True,choices=sorted(PROJECT_CLASSES)); q.add_argument("--path",default="."); q.add_argument("--force",action="store_true"); q.set_defaults(func=cmd_init)
    q=s.add_parser("doctor"); q.add_argument("--path",default="."); q.set_defaults(func=cmd_doctor)
    q=s.add_parser("work-order"); q.add_argument("--objective",required=True); q.add_argument("--role",required=True,choices=sorted(ROLES)); q.add_argument("--profile",required=True); q.add_argument("--lenses",default=""); q.add_argument("--claim-level",required=True,choices=sorted(CLAIMS)); q.add_argument("--project-id"); q.add_argument("--id"); q.add_argument("--max-turns",type=int,default=6); q.add_argument("--max-investigation-steps",type=int,default=8); q.add_argument("--output",required=True); q.set_defaults(func=cmd_work_order)
    q=s.add_parser("trace"); q.add_argument("--work-order",required=True); q.add_argument("--result-state",required=True,choices=["completed","negative_finding","blocked","budget_exhausted","needs_human_gate"]); q.add_argument("--summary",required=True); q.add_argument("--provider",default="grok"); q.add_argument("--output",required=True); q.set_defaults(func=cmd_trace)
    q=s.add_parser("validate"); q.add_argument("file"); q.set_defaults(func=cmd_validate)
    return p

def main():
    a=parser().parse_args(); raise SystemExit(a.func(a))
if __name__=="__main__": main()
