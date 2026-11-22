"""Draw report Figures 7 and 8 from the recorded per-split measurements."""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=root / "figures")
out = parser.parse_args().output_dir
out.mkdir(parents=True, exist_ok=True)
data = [
    ("Taiwan credit cards", root/"experiments/near-tie/fresh/rule_metrics.csv", "#007a73", "o"),
    ("South German Credit", root/"experiments/external/south_german_results.csv", "#a34c20", "s"),
    ("Polish companies", root/"experiments/external/polish_results.csv", "#485587", "^"),
]
data = [(n,pd.read_csv(path).sort_values("split_seed"),c,m) for n,path,c,m in data]
for name,df,c,m in data:
    assert len(df) == 5 and (df.n_excluded_undefined == 0).all()
    assert ((df.single_reason_repeat - df.baseline_repeat - df.single_minus_baseline).abs() < 1e-9).all()
    assert ((df.coverage >= .5) & (df.single_minus_baseline >= .05)).sum() == (5 if name.startswith("Taiwan") else 0)
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10, "axes.spines.right":False,
                     "axes.spines.top":False, "axes.edgecolor":"#a6afb3", "axes.labelcolor":"#192c35",
                     "xtick.color":"#384e57","ytick.color":"#384e57","axes.axisbelow":True,
                     "pdf.fonttype":42})
fig,ax=plt.subplots(figsize=(7.2,4.15))
fig.subplots_adjust(left=.12,right=.965,top=.84,bottom=.16)
ax.set(xlim=(20,81), ylim=(0,22), xlabel="One-reason coverage (%)",ylabel="Repeat-agreement gain (percentage points)")
ax.fill_between([50,81],5,22,color="#e8f3ee",zorder=0)
ax.grid(axis="both",color="#dce4e4",linewidth=.55)
for n,df,c,m in data:
    ax.scatter(df.coverage*100, df.single_minus_baseline*100, marker=m, color=c, s=38, edgecolors="white",linewidths=.55,label=n,zorder=4)
for fun,val in [(ax.axhline,5),(ax.axvline,50)]:
    fun(val,color="#596c65",linewidth=1,ls=(0,(4,3)))
ax.text(80,20.5,"Both targets met",ha="right",va="center",color="#345447",size=9)
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_major_locator(MultipleLocator(5))
fig.legend(*ax.get_legend_handles_labels(),loc="upper center",bbox_to_anchor=(.53,.99),ncol=3,frameon=False,columnspacing=1.3,handletextpad=.4)
fig.savefig(out/"figure-7-transfer-targets.png",dpi=320,facecolor="white")
fig.savefig(out/"figure-7-transfer-targets.pdf")
plt.close(fig)

fig,axs=plt.subplots(1,3,figsize=(7.35,3.25),sharey=True)
fig.subplots_adjust(left=.095,right=.977,top=.69,bottom=.24,wspace=.24)
for ax,(n,df,c,m) in zip(axs,data):
    for j,(_,r) in enumerate(df.iterrows()):
        b,s=100*r.baseline_repeat,100*r.single_reason_repeat
        ax.hlines(j,b,s,color=c,linewidth=2)
        ax.scatter(b,j,s=39,facecolor="white",edgecolor=c,linewidth=1.5,zorder=3)
        ax.scatter(s,j,s=39,facecolor=c,edgecolor=c,linewidth=1,zorder=3)
    ax.set(ylim=(4.55,-.55),xlim=(-3,103),title=n,yticks=range(5),xticks=[0,25,50,75,100])
    ax.set_title(n,fontsize=10,fontweight="bold",pad=9)
    ax.grid(axis="x",color="#d7dfe0",linewidth=.65)
    ax.tick_params(axis="both",labelsize=8)
    ax.spines["left"].set_visible(False)
axs[0].set_yticks(range(5),[str(int(x))[-2:] for x in data[0][1].split_seed])
axs[0].set_ylabel("Split seed suffix",fontsize=9)
fig.supxlabel("First-reason repeat rate (%)",y=.04,fontsize=10)
handles=[Line2D([],[],ls="",marker="o",markersize=6,markeredgecolor="#304654",markerfacecolor=k,label=l) for k,l in [("white","All cases"),("#304654","Cases shown one reason")]]
fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.5,1.0),ncol=2,frameon=False,handletextpad=.45)
fig.savefig(out/"figure-8-repeat-agreement.png",dpi=320,facecolor="white")
fig.savefig(out/"figure-8-repeat-agreement.pdf")
