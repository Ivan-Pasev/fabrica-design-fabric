#!/usr/bin/env python3
"""FDF() unified read-only initialization, plan, gated apply, status, rollback."""
import argparse
import json
import sys
from pathlib import Path
import fdf_adopt as a
from fdf_kernel import select

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=("FDF","status","evolve","apply","verify","rollback"))
    p.add_argument("--project",required=True)
    p.add_argument("--platforms",default=",".join(a.PLATFORMS))
    p.add_argument("--root-hooks",choices=("none","append"),default="none")
    p.add_argument("--approve-plan",default=None)
    args=p.parse_args(argv)
    try:
        root=a.require_root(args.project)
        platforms=tuple(x.strip() for x in args.platforms.split(",") if x.strip())
        if not platforms or len(platforms)!=len(set(platforms)) or set(platforms)-set(a.PLATFORMS):
            raise ValueError("unsupported or duplicate platform")
        if args.command=="FDF":
            plan,_=a.generate_plan(root,platforms,args.root_hooks)
            result={"command":"FDF()","phase":"SOURCE_DISCOVERY_AND_APPROVAL_PLAN",
                "projectdna":plan["projectdna"],"skill_lattice":select(plan["projectdna"]),
                "actions":plan["actions"],"collisions":plan["collisions"],
                "plan_sha256":plan["plan_sha256"],"files_written":False,
                "next":"Review source/host policies and authorize exact plan separately or HOLD",
                "release":"HOLD"}
        elif args.command=="apply":
            if not args.approve_plan: raise ValueError("apply requires --approve-plan")
            result=a.apply(root,args.approve_plan,platforms,args.root_hooks)
        elif args.command=="verify":result=a.verify(root)
        elif args.command=="rollback":
            if not args.approve_plan:raise ValueError("rollback requires --approve-plan")
            result=a.rollback(root,args.approve_plan)
        elif args.command=="status":
            result={"status":"NOT_INSTALLED","release":"HOLD"}
            if (root/a.MANIFEST).exists():result=a.verify(root)
            result["caller_policy_semantics_verified"]=False
        else:
            data=a.detect(root)
            result={"phase":"GUIDED_EVOLUTION_PROPOSAL_ONLY", "projectdna":data,
                "skill_lattice":select(data),"next":"Choose one observed problem, produce ProposalDNA, collect real test evidence; owner decides",
                "human_decision":"PENDING_NOT_GIVEN","writes_performed":False,"release":"HOLD"}
        print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    except (ValueError,OSError,json.JSONDecodeError,UnicodeError) as e:
        print("HOLD: "+str(e),file=sys.stderr);return 2
    return 0

if __name__=="__main__":sys.exit(main())
