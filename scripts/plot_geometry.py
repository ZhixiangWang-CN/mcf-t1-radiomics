"""Rebuild Figure 2 from the case-level geometry summary (no images required)."""
from pathlib import Path
import argparse,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data/geometry_comparison.csv');p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'figures');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 with a.data.open() as f:rows=list(csv.DictReader(f))
 n=len(rows);before=np.array([float(r['before_max_bbox_excursion_mm']) for r in rows]);after=np.array([float(r['after_max_bbox_excursion_mm']) for r in rows]);bc=np.array([float(r['before_foreground_inside_pct']) for r in rows]);ac=np.array([float(r['after_foreground_inside_pct']) for r in rows])
 assert n==130 and (after==0).all() and (ac==100).all()
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'legend.frameon':False})
 fig,(ax,bx)=plt.subplots(1,2,figsize=(7.09,3.05),gridspec_kw={'width_ratios':[1.35,1]});fig.subplots_adjust(left=.09,right=.98,bottom=.2,top=.83,wspace=.38)
 gray='#747C86';blue='#007D91'
 for vals,color,label in [(before,gray,'Before'),(after,blue,'After')]:
  x=np.sort(vals);ax.step(np.r_[-5,x,310],np.r_[0,np.arange(1,n+1)/n,1],where='post',color=color,lw=1.8,label=label)
 ax.set(xlim=(-6,310),ylim=(-.02,1.07),xlabel='Maximum ROI bounding-box excursion (mm)',ylabel='Cumulative fraction of cases',xticks=[0,100,200,300],yticks=[0,.25,.5,.75,1])
 ax.legend(loc='lower right');ax.text(10,.96,'After: 130/130 at 0 mm',color=blue,va='top',fontsize=7.5);ax.text(10,.28,'Before: 20/130 at 0 mm',color=gray,fontsize=7.5)
 ax.set_title('Physical-space boundary excursion',loc='left',pad=12)
 # Exact masses, rather than a smoothed density for binary observations.
 transitions={}
 for x,y in zip(bc,ac):transitions[(x,y)]=transitions.get((x,y),0)+1
 for (x,y),count in transitions.items():bx.plot([0,1],[x,y],color='#C4CDD1',lw=count/n*4,zorder=1)
 for j,(values,color) in enumerate([(bc,gray),(ac,blue)]):
  for val in sorted(set(values)):
   count=int(sum(values==val));bx.scatter(j,val,s=count*5.5,color=color,edgecolors='white',linewidth=.7,zorder=3)
   bx.annotate(f'{count}/{n}',(j,val),xytext=(0,18 if val==100 else 18),textcoords='offset points',ha='center',color=color,fontweight='bold',fontsize=8)
 bx.set(xlim=(-.35,1.35),ylim=(-18,122),xticks=[0,1],xticklabels=['Before','After'],yticks=[0,50,100],ylabel='Mask foreground within image (%)')
 bx.set_title('Foreground containment',loc='left',pad=12)
 bx.text(.50,39,'110 cases',ha='center',rotation=46,color='#59646B',fontsize=7.5)
 for label,axis in [('a',ax),('b',bx)]:axis.text(-.17,1.12,label,transform=axis.transAxes,fontweight='bold',fontsize=11)
 for ext in ['pdf','svg','png','tiff']:fig.savefig(a.out/f'Figure_2_geometry.{ext}',dpi=600,facecolor='white')
 plt.close(fig)
if __name__=='__main__':main()
