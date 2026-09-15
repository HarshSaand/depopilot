import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from planner import *
# Objectives fixed before running: three absolute engineering rates, tolerance ±.05 Å/s.
targets=[.5,1.,1.4];seeds=range(20);budget=15;initial=12;results=[]
for target in targets:
 for seed in seeds:
  initial_ids=np.random.default_rng(seed).choice(len(X),initial,replace=False).tolist()
  for strategy in ['bo','random','space_filling','greedy']:
   obs=initial_ids.copy();rng=np.random.default_rng(seed+1000);hit=0 if min(abs(Y[obs]-target))<=.05 else None;covered=[]
   for step in range(1,budget+1):
    r=recommend(obs,Y[obs].tolist(),target,.05,strategy,rng);idx=r['index'];lo,hi=r['predictive_interval_95_A_s'];covered.append(lo<=Y[idx]<=hi);obs.append(idx)
    if hit is None and abs(Y[idx]-target)<=.05:hit=step
   results.append(dict(target=target,seed=seed,strategy=strategy,hit_query=hit,best_error=float(min(abs(Y[obs]-target))),interval_coverage=float(np.mean(covered))))
 summary=[]
 for strategy in ['bo','random','space_filling','greedy']:
  r=[v for v in results if v['strategy']==strategy];summary.append(dict(strategy=strategy,runs=len(r),success_rate=float(np.mean([v['hit_query'] is not None for v in r])),mean_best_error_A_s=float(np.mean([v['best_error'] for v in r])),mean_capped_queries=float(np.mean([v['hit_query'] if v['hit_query'] is not None else budget+1 for v in r])),selected_interval_coverage=float(np.mean([v['interval_coverage'] for v in r]))))
 (ROOT/'artifacts/evaluation.json').write_text(json.dumps(dict(initial=initial,budget=budget,targets=targets,tolerance=.05,seeds=20,summary=summary,runs=results),indent=2));print(summary)
