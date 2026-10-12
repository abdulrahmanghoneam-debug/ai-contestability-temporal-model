"""Audit a synthetic configuration and enumerate inclusion-minimal option repairs.

This is a model audit, not legal advice or an automated compliance certificate.
Repairs add optional mechanisms only; they do not change budgets or times.
"""
import argparse
import itertools
import json
from dataclasses import asdict,replace
from pathlib import Path
from model import Scenario,characterize,model_check,verify_witness

OPTIONS=('informative_notice','preservation_available','protective_filing','deadline_from_notice')

def audit_case(c):
    observed=model_check(c,witness=True)
    if observed['reachable']:verify_witness(c,observed)
    candidates=[]
    available=[key for key in OPTIONS if not getattr(c,key)]
    for size in range(len(available)+1):
        for subset in itertools.combinations(available,size):
            if any(set(x['add_options']).issubset(subset) for x in candidates):continue
            modified=replace(c,**dict.fromkeys(subset,True))
            result=model_check(modified,witness=True)
            if result['reachable']:
                verify_witness(modified,result)
                candidates.append({'add_options':list(subset),'earliest_completion':result['earliest_correction'],'certificate':result['witness']})
    return {'scope':'Synthetic timed model only; legal availability and actual durations require separate verification.',
            'scenario':asdict(c),'analytical_diagnosis':characterize(c),
            'graph_check':observed,'inclusion_minimal_repairs':candidates}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path);p.add_argument('--output',type=Path)
    args=p.parse_args()
    c=Scenario(**json.loads(args.input.read_text(encoding='utf-8'))) if args.input else Scenario(notice=2,access_delay=3,evidence_delay=2,retention=3,budget=4)
    result=audit_case(c)
    s=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.write_text(s,encoding='utf-8')
    else:print(s)
