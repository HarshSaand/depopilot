"""Extract numeric literal buffers with pickletools; never execute pickle opcodes."""
import base64,csv,hashlib,json,pickletools,sys
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'data'
NAMES=['Al 120 W','Al 200 W','Al 250 W','Ti 120 W','Ti 200 W','Ti 250 W']
def extract(path):
 x=json.loads(Path(path).read_text());x=json.loads(x) if isinstance(x,str) else x
 ops=list(pickletools.genops(base64.b64decode(x['_measurements_exp'])))
 buffers=[v for o,v,p in ops if o.name in ('BINBYTES','SHORT_BINBYTES') and len(v)>100]
 # Fixed audited schema: first float64 block has five recipe columns plus y1.
 names=[p['name'] for p in x['searchspace']['continuous']['parameters']]
 n=x['n_batches_done']; assert len(names)==5 and len(buffers[0])==n*6*8
 arr=np.frombuffer(buffers[0],dtype='<f8').reshape(6,n).T.copy()
 return x,names,arr
if __name__=='__main__':
 path=Path(sys.argv[1])/'hipims_campaign_0.json'
 x,names,a=extract(path)
 a[:,-1]*=1000*1.1684
 valid=np.isfinite(a).all(axis=1)
 bounds=np.array([[p['bounds']['lower'],p['bounds']['upper']] for p in x['searchspace']['continuous']['parameters']])
 valid &= ((a[:,:5]>=bounds[:,0]) & (a[:,:5]<=bounds[:,1])).all(axis=1)
 valid &= (a[:,1]+a[:,2]+a[:,3])<1e6/a[:,0]
 groups={}
 for row in a[valid]: groups.setdefault(tuple(row[:5].round(8)),[]).append(row[-1])
 with (OUT/'recipes.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['recipe_id',*names,'rate_A_s','repeat_count'])
  for i,(key,rates) in enumerate(groups.items()):w.writerow([f'AL120-{i:04d}',*key,float(np.mean(rates)),len(rates)])
 audit={'campaign':'Al 120 W','raw_rows':len(a),'valid_rows':int(valid.sum()),'excluded_rows':int((~valid).sum()),'unique_recipes':len(groups),'repeat_groups':sum(len(v)>1 for v in groups.values()),'controls':names,'bounds':bounds.tolist(),'rate_unit':'Å/s','conversion':'raw y1 × 1000 × 1.1684','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dataset_doi':'10.5281/zenodo.18495402','calibration_source':'Clean Datasets Used for Publication/Al - 120 W  - short PW/calibration.txt','scope':'Finite observed-recipe pool; timing checked, not hardware safety qualification'}
 (OUT/'audit.json').write_text(json.dumps(audit,indent=2));print(audit)
