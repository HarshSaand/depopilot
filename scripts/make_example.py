import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from planner import *
ids=np.random.default_rng(7).choice(len(IDS),12,replace=False).tolist()
r=recommend(ids,Y[ids].tolist(),1.,.05)
(ROOT/'artifacts/recommendation.json').write_text(json.dumps(r,indent=2))
with (ROOT/'artifacts/recommendation.csv').open('w') as f:
 row={'recipe_id':r['recipe_id'],**r['settings'],'target_A_s':r['target_A_s'],'predicted_rate_A_s':r['predicted_rate_A_s']};w=csv.DictWriter(f,fieldnames=row);w.writeheader();w.writerow(row)
with (ROOT/'artifacts/initial_observations.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['recipe_id','rate_A_s']);w.writerows((IDS[i],Y[i]) for i in ids)
(ROOT/'artifacts/revealed_result.json').write_text(json.dumps({'recipe_id':r['recipe_id'],'recorded_rate_A_s':float(Y[r['index']]),'target_error_A_s':float(abs(Y[r['index']]-1)),'provenance':'historical measured outcome; revealed after recommendation'},indent=2))
# Region extrapolation check: upper PRR quintile determined from recipe controls only.
cut=np.quantile(X[:,0],.8);train=np.flatnonzero(X[:,0]<cut);test=np.flatnonzero(X[:,0]>=cut)
mu,s=fit_predict(train,Y[train],test)
(ROOT/'artifacts/heldout_region.json').write_text(json.dumps({'split':'highest PRR 20% held out; no outcome-based split','train_recipes':len(train),'test_recipes':len(test),'cutoff_Hz':cut,'mae_A_s':float(np.mean(abs(mu-Y[test]))),'rmse_A_s':float(np.sqrt(np.mean((mu-Y[test])**2))),'interval_coverage_95':float(np.mean(abs(mu-Y[test])<=1.96*s))},indent=2))
print(r)

trace=[];obs=ids.copy()
for step in range(1,16):
 result=recommend(obs,Y[obs].tolist(),1.,.05);result['recorded_rate_A_s']=float(Y[result['index']]);result['query']=step;trace.append(result);obs.append(result['index'])
 if abs(result['recorded_rate_A_s']-1.)<=.05:break
(ROOT/'artifacts/replay_trace.json').write_text(json.dumps(trace,indent=2))
