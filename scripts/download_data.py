"""Download official source archive and extract the one campaign as inert JSON."""
import urllib.request,json,zipfile,tempfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
meta=json.load(urllib.request.urlopen('https://zenodo.org/api/records/18495402'))
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);dest=p/'source.zip';print('Downloading official 396 MB archive…')
 urllib.request.urlretrieve(meta['files'][0]['links']['self'],dest)
 with zipfile.ZipFile(dest) as z:
  names=[n for n in z.namelist() if '/Al - 120 W  - short PW/' in n and n.endswith('/Campaign.json')]
  assert len(names)==1,names
  (p/'hipims_campaign_0.json').write_bytes(z.read(names[0]))
 subprocess.run([sys.executable,str(ROOT/'scripts/prepare_data.py'),str(p)],check=True)
