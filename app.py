import csv,io,json
import numpy as np
from flask import Flask,request,jsonify,send_from_directory
from planner import ROOT,IDS,X,Y,AUDIT,recommend
app=Flask(__name__,static_folder='static');app.config['MAX_CONTENT_LENGTH']=1024*1024
@app.get('/')
def home():return send_from_directory('static','index.html')
@app.get('/api/start')
def start():
 ids=np.random.default_rng(7).choice(len(IDS),12,replace=False)
 return jsonify(audit=AUDIT,observations=[{'recipe_id':IDS[i],'rate_A_s':float(Y[i])} for i in ids])
@app.post('/api/recommend')
def plan():
 try:
  d=request.get_json();obs=d['observations'];r=recommend([IDS.index(o['recipe_id']) for o in obs],[float(o['rate_A_s']) for o in obs],float(d['target']),float(d['tolerance']));return jsonify(r)
 except (ValueError,KeyError,TypeError) as e:return jsonify(error=str(e)),400
@app.post('/api/reveal')
def reveal():
 try:
  i=IDS.index(request.get_json()['recipe_id']);return jsonify(recipe_id=IDS[i],rate_A_s=float(Y[i]),source='Recorded historical measurement, not a new physical experiment')
 except (ValueError,KeyError,TypeError) as e:return jsonify(error=str(e)),400
@app.post('/api/import')
def import_csv():
 try:
  text=request.get_data(as_text=True);rows=list(csv.DictReader(io.StringIO(text)))
  observations=[{'recipe_id':r['recipe_id'],'rate_A_s':float(r['rate_A_s'])} for r in rows]
  recommend([IDS.index(r['recipe_id']) for r in observations],[r['rate_A_s'] for r in observations],1,.05)
  return jsonify(observations=observations)
 except (ValueError,KeyError,TypeError) as e:return jsonify(error=str(e)),400
@app.get('/artifacts/<path:name>')
def artifacts(name):return send_from_directory(ROOT/'artifacts',name)
if __name__=='__main__':app.run(host='127.0.0.1',port=8051)
