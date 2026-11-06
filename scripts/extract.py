"""Direction-only geometry correction and paired Original-feature extraction."""
import argparse,csv,json,math,itertools
from pathlib import Path
import numpy as np

def geometry_metrics(mask_xyz, mask_affine, image_affine, image_size, image_spacing):
    xyz=np.asarray(mask_xyz)
    if not len(xyz): raise ValueError('Empty foreground')
    transform=np.linalg.inv(image_affine) @ mask_affine
    def into_image(points): return points @ transform[:3,:3].T + transform[:3,3]
    idx=into_image(xyz)
    corners=np.array(list(itertools.product(*zip(xyz.min(0)-.5,xyz.max(0)+.5))))
    ci=into_image(corners); size=np.asarray(image_size); spacing=np.asarray(image_spacing)
    excursion=max(0.,float(np.max((-.5-ci.min(0))*spacing)),float(np.max((ci.max(0)-(size-.5))*spacing)))
    if excursion<1e-8: excursion=0.
    inside=np.all((idx>=-.5-1e-5)&(idx<=size-.5+1e-5),axis=1)
    return {'max_bbox_excursion_mm':excursion,'foreground_inside_pct':float(100*inside.mean())}

def affine(im):
    a=np.eye(4);a[:3,:3]=np.asarray(im.GetDirection()).reshape(3,3)@np.diag(im.GetSpacing());a[:3,3]=im.GetOrigin();return a

def main():
    import SimpleITK as sitk
    import radiomics
    from radiomics import featureextractor
    p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    with args.manifest.open() as f: rows=list(csv.DictReader(f))
    if not rows: raise ValueError('Manifest has no cases')
    ids=[r['audit_id'] for r in rows]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate audit IDs')
    if not all(r['verified_correspondence'].lower()=='true' for r in rows): raise ValueError('Expert voxel correspondence confirmation is required for every case')
    args.out.mkdir(parents=True,exist_ok=True)
    e=featureextractor.RadiomicsFeatureExtractor(label=1,binWidth=25,geometryTolerance=.01,correctMask=True,normalize=False)
    def extract(im,m):
        try:
            f={k:float(v) for k,v in e.execute(im,m).items() if k.startswith('original_')}
            return {'features':f,'count':len(f),'finite_count':sum(math.isfinite(v) for v in f.values())}
        except Exception as ex: return {'features':{},'count':0,'finite_count':0,'error':str(ex)}
    records=[]; geometry=[]
    for row in rows:
        image=sitk.ReadImage(row['image_path']);mask=sitk.ReadImage(row['mask_path'])
        for name in ['GetSize','GetSpacing','GetOrigin']:
            if getattr(image,name)()!=getattr(mask,name)(): raise ValueError(f"{row['audit_id']}: unequal {name}")
        fixed=sitk.Image(mask);fixed.SetDirection(image.GetDirection())
        xyz=np.argwhere(sitk.GetArrayFromImage(mask)>0)[:,::-1]
        g={'audit_id':row['audit_id']}
        for prefix,m in [('before',mask),('after',fixed)]:
            g.update({prefix+'_'+k:v for k,v in geometry_metrics(xyz,affine(m),affine(image),image.GetSize(),image.GetSpacing()).items()})
        geometry.append(g)
        records.append({'audit_id':row['audit_id'],'before':extract(image,mask),'after':extract(image,fixed)})
    (args.out/'features.json').write_text(json.dumps({'versions':{'pyradiomics':radiomics.__version__,'simpleitk':sitk.Version_VersionString()},'cases':records},indent=2,allow_nan=True))
    with (args.out/'geometry_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(geometry[0]));w.writeheader();w.writerows(geometry)
    print(json.dumps({'cases':len(records),'before_107_finite':sum(r['before']['count']==r['before']['finite_count']==107 for r in records),'after_107_finite':sum(r['after']['count']==r['after']['finite_count']==107 for r in records)}))
if __name__=='__main__':main()
