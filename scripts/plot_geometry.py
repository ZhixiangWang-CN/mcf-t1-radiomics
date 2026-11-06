"""Rebuild Figure 2 from the case-level geometry summary (no images required)."""
from pathlib import Path
import argparse,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data/geometry_comparison.csv')
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'figures')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with a.data.open() as f: rows=list(csv.DictReader(f))
    n=len(rows)
    before=np.array([float(r['before_max_bbox_excursion_mm']) for r in rows])
    after=np.array([float(r['after_max_bbox_excursion_mm']) for r in rows])
    bc=np.array([float(r['before_foreground_inside_pct']) for r in rows])
    ac=np.array([float(r['after_foreground_inside_pct']) for r in rows])
    assert n==130 and (after==0).all() and (ac==100).all()
    gray='#8C837A';teal='#007F86';ink='#26343B';muted='#6F7C83'
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'text.color':ink,'axes.labelcolor':ink,'xtick.color':muted,'ytick.color':muted,'axes.edgecolor':'#A7AFB3','axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.65,'svg.fonttype':'none','pdf.fonttype':42,'legend.frameon':False})
    fig=plt.figure(figsize=(7.2,3.35),facecolor='white')
    ax=fig.add_axes([.09,.20,.43,.61]);bx=fig.add_axes([.68,.20,.29,.61])
    for x,label,title in [(.035,'a','Distance beyond image boundary'),(.605,'b','Mask containment')]:
        fig.text(x,.935,label,fontsize=12,fontweight='bold',va='top')
        fig.text(x+.055,.932,title,fontsize=10,fontweight='bold',va='top')
    fig.text(.09,.86,'All 130 cases · empirical cumulative distribution',fontsize=7,color=muted)
    fig.text(.68,.86,'Paired change across 130 cases',fontsize=7,color=muted)
    ax.set_axisbelow(True);ax.grid(axis='y',color='#E8ECEE',lw=.55)
    for vals,color,ls in [(before,gray,'-'),(after,teal,'-')]:
        x=np.sort(vals)
        ax.step(np.r_[-5,x,310],np.r_[0,np.arange(1,n+1)/n,1],where='post',color=color,lw=1.9,ls=ls,zorder=3)
    ax.set(xlim=(-7,310),ylim=(-.025,1.035),xticks=[0,100,200,300],yticks=[0,.25,.5,.75,1],xlabel='Maximum ROI excursion (mm)',ylabel='Cumulative proportion of cases')
    ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.tick_params(length=3,width=.6,labelsize=7)
    ax.text(12,.92,'After correction',color=teal,fontweight='bold',fontsize=8)
    ax.text(12,.84,'130/130 at 0 mm',color=teal,fontsize=7.5)
    ax.text(179,.43,'Before correction',color=gray,fontweight='bold',fontsize=8)
    ax.annotate('20/130 at 0 mm',xy=(0,20/130),xytext=(29,.29),fontsize=7.5,color=gray,arrowprops={'arrowstyle':'-','color':gray,'lw':.7,'connectionstyle':'angle,angleA=0,angleB=90,rad=4'})
    # Bubble areas and connector widths encode the observed case counts.
    transitions={}
    for x,y in zip(bc,ac):transitions[(x,y)]=transitions.get((x,y),0)+1
    for (x,y),count in transitions.items():bx.plot([0,1],[x,y],color='#CFD9D9',lw=count/n*4,zorder=1)
    for j,(vals,color) in enumerate([(bc,gray),(ac,teal)]):
        for val in sorted(set(vals)):
            count=int(sum(vals==val))
            bx.scatter(j,val,s=count*2.7,facecolor=color,edgecolor='white',lw=1,zorder=3)
            bx.annotate(f'{count}/130',(j,val),xytext=(0,17),textcoords='offset points',ha='center',fontsize=8,fontweight='bold',color=color)
    bx.set(xlim=(-.3,1.3),ylim=(-14,126),xticks=[0,1],xticklabels=['Before','After'],yticks=[0,50,100],ylabel='Foreground voxels within image (%)')
    bx.tick_params(length=0,labelsize=8,pad=6);bx.spines['left'].set_visible(False);bx.spines['bottom'].set_visible(False)
    for y in [0,50,100]:bx.axhline(y,color='#E8ECEE',lw=.55,zorder=0)
    bx.text(.52,43,'110 cases',ha='center',fontsize=7.5,color=muted,bbox={'facecolor':'white','edgecolor':'none','pad':2})
    fig.text(.09,.035,'Direction metadata correction',color=muted,fontsize=7)
    for ext in ['pdf','svg','png','tiff']:fig.savefig(a.out/f'Figure_2_geometry.{ext}',dpi=600,facecolor='white')
    fig.savefig(a.out/'Figure_2_preview.png',dpi=180,facecolor='white')
    plt.close(fig)
if __name__=='__main__':main()
