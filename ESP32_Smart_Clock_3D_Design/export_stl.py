import subprocess,concurrent.futures,pathlib,json,time,sys,os,shutil
root=pathlib.Path(__file__).resolve().parent
import trimesh
executable=os.environ.get('OPENSCAD') or shutil.which('openscad')
if not executable and os.name=='nt': executable=str(pathlib.Path(os.environ.get('ProgramFiles','C:/Program Files'))/'OpenSCAD/openscad.com')
if not executable or not pathlib.Path(executable).is_file(): raise SystemExit('Install OpenSCAD on PATH or set OPENSCAD to its executable.')
parts=['body','lid','sensor_cage']
if len(sys.argv)>1: parts=sys.argv[1:]
assert set(parts)<=set(['body','lid','sensor_cage','esp_gauge','power_gauge'])
for folder in ['stl','test-pieces','previews']:(root/folder).mkdir(exist_ok=True)
def export(p):
 t=time.time();dest=root/('stl' if p in ['body','lid','sensor_cage'] else 'test-pieces')/f'{p}.stl';r=subprocess.run([executable,'-o',str(dest),'-D',f'part="{p}"',str(root/'clock.scad')],capture_output=True,text=True)
 (root/'previews'/f'{p}.log').write_text(r.stdout+r.stderr,encoding='utf8')
 if r.returncode: raise RuntimeError(r.stdout+r.stderr)
 mesh=trimesh.load_mesh(dest)
 clean=trimesh.boolean.union([mesh],engine='manifold')
 assert clean.is_volume and abs(clean.volume-mesh.volume)<0.1, p
 clean.export(dest)
 return {'part':p,'returncode':r.returncode,'seconds':round(time.time()-t,1),'bytes':dest.stat().st_size if dest.exists() else 0,'warnings':[l for l in (r.stdout+r.stderr).splitlines() if 'WARNING' in l or 'ERROR' in l]}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=[]
 for r in pool.map(export,parts):results.append(r);print(json.dumps(r),flush=True)
(root/'previews'/'export_report.json').write_text(json.dumps(results,indent=2),encoding='utf8')




