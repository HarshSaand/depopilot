"""Original finite-pool Bayesian target-matching planner. Outcomes passed explicitly."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern,ConstantKernel,WhiteKernel
ROOT=Path(__file__).parent
AUDIT=json.loads((ROOT/'data/audit.json').read_text())
ROWS=list(csv.DictReader((ROOT/'data/recipes.csv').open()))
IDS=[r['recipe_id'] for r in ROWS]
X=np.array([[float(r[k]) for k in AUDIT['controls']] for r in ROWS])
Y=np.array([float(r['rate_A_s']) for r in ROWS])
BOUNDS=np.array(AUDIT['bounds']);XN=(X-BOUNDS[:,0])/(BOUNDS[:,1]-BOUNDS[:,0])
def fit_predict(observed,values,candidates):
 # Bounds are experiment-design constants. No hidden outcome normalization.
 model=GaussianProcessRegressor(kernel=ConstantKernel(1.0)*Matern(length_scale=.35,nu=2.5)+WhiteKernel(.01),normalize_y=True,optimizer=None,alpha=1e-8)
 model.fit(XN[observed],np.asarray(values));return model.predict(XN[candidates],return_std=True)
def expected_target_improvement(mu,sigma,target,best_error):
 """E[max(best_error - |Y-target|, 0)] under a normal predictive distribution."""
 s=np.maximum(sigma,1e-12);lo=target-best_error;hi=target+best_error
 zl=(lo-mu)/s;zt=(target-mu)/s;zh=(hi-mu)/s
 left=(mu-lo)*(norm.cdf(zt)-norm.cdf(zl))+s*(norm.pdf(zl)-norm.pdf(zt))
 right=(hi-mu)*(norm.cdf(zh)-norm.cdf(zt))-s*(norm.pdf(zt)-norm.pdf(zh))
 return np.maximum(left+right,0)
def recommend(observed,values,target,tolerance,strategy='bo',rng=None):
 if not np.isfinite([target,tolerance]).all() or target<=0 or tolerance<=0:raise ValueError('Target and tolerance must be finite and positive.')
 if len(observed)<3 or len(set(observed))!=len(observed) or len(values)!=len(observed):raise ValueError('Provide at least three distinct measured recipe IDs and matching rates.')
 if any(i<0 or i>=len(X) for i in observed) or not np.isfinite(values).all() or np.any(np.asarray(values)<0):raise ValueError('Invalid recipe ID or measurement.')
 candidates=np.setdiff1d(np.arange(len(X)),observed)
 if not len(candidates):raise ValueError('All recipes have been measured.')
 mu,std=fit_predict(observed,values,candidates)
 if strategy=='random':k=(rng or np.random.default_rng(0)).integers(len(candidates))
 elif strategy=='space_filling':k=np.argmax(np.min(np.sum((XN[candidates,None]-XN[observed])**2,axis=2),axis=1))
 elif strategy=='greedy':k=np.argmin(abs(mu-target))
 elif strategy=='bo':k=np.argmax(expected_target_improvement(mu,std,target,min(abs(np.asarray(values)-target))))
 else:raise ValueError('Unknown strategy')
 idx=int(candidates[k]);return {'recipe_id':IDS[idx],'index':idx,'campaign':AUDIT['campaign'],'settings':{k:float(v) for k,v in zip(AUDIT['controls'],X[idx])},'target_A_s':target,'tolerance_A_s':tolerance,'predicted_rate_A_s':float(mu[k]),'predictive_interval_95_A_s':[float(mu[k]-1.96*std[k]),float(mu[k]+1.96*std[k])],'probability_in_tolerance':float(norm.cdf((target+tolerance-mu[k])/std[k])-norm.cdf((target-tolerance-mu[k])/std[k])),'expected_error_improvement_A_s':float(expected_target_improvement(mu[k],std[k],target,min(abs(np.asarray(values)-target)))),'observations':len(observed),'strategy':strategy,'model':'fixed Matérn 5/2 GP v1','scope':'Historical finite-pool recommendation; not hardware qualified','source_doi':AUDIT['dataset_doi']}
