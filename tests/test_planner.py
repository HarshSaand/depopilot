import numpy as np
import pytest
from planner import *
from app import app

def test_acquisition_matches_numerical_integral():
 from scipy.integrate import quad
 for mu,s in [(1.,.2),(.5,.5),(1.8,.1)]:
  expected=quad(lambda y:max(.3-abs(y-1),0)*norm.pdf(y,mu,s),.7,1.3)[0]
  assert expected_target_improvement(mu,s,1,.3)==pytest.approx(expected,abs=1e-8)
def test_hidden_outcomes_not_used():
 obs=list(range(12));values=Y[obs].copy();a=recommend(obs,values,1,.05)
 original=Y.copy()
 try:
  Y[12:]=99999;b=recommend(obs,values,1,.05)
  assert a==b
 finally:Y[:]=original
 assert a['index'] not in obs
def test_input_validation():
 for obs,values in [([0,0,1],[1,1,1]),([0,1,2],[1,np.nan,1]),([0,1,9999],[1,1,1])]:
  with pytest.raises(ValueError):recommend(obs,values,1,.05)
 with pytest.raises(ValueError):recommend([0,1,2],[1,1,1],1,-1)
def test_api_import_and_reveal():
 c=app.test_client();start=c.get('/api/start').get_json();r=c.post('/api/recommend',json={'observations':start['observations'],'target':1,'tolerance':.05});assert r.status_code==200
 result=c.post('/api/reveal',json={'recipe_id':r.get_json()['recipe_id']});assert result.get_json()['rate_A_s']>=0
 assert c.post('/api/import',data='recipe_id,rate_A_s\nBAD,2').status_code==400
 assert c.post('/api/recommend',json={'observations':[],'target':1,'tolerance':.05}).status_code==400
