from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(r"D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption")
OUT=ROOT/"08_Research_Grade_Deck"/"assets"/"charts_rebuilt"
OUT.mkdir(parents=True, exist_ok=True)
T=ROOT/"outputs"/"tables"
BLUE="#0B1F3A"; MUTED="#6B7280"; LIGHT="#E5E7EB"; BLACK="#111827"; GRAY="#9CA3AF"
plt.rcParams.update({
    "font.family": ["Microsoft YaHei", "DejaVu Sans", "Arial"],
    "axes.edgecolor": "#D1D5DB", "axes.linewidth": 0.8,
    "axes.labelcolor": BLACK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": "white", "axes.facecolor":"white", "savefig.facecolor":"white",
    "font.size": 10,
})

def save(fig,name):
    fig.savefig(OUT/f"{name}.png", dpi=240, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(OUT/f"{name}.svg", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

# 1 model comparison
cv=pd.read_csv(T/'enhanced_cv_results.csv')
fig,ax=plt.subplots(figsize=(8,4.6))
models=['ridge','random_forest','extra_trees','hist_gradient_boosting']
labels=['Ridge','Random Forest','ExtraTrees','HistGB']
x=np.arange(len(models)); width=.34
for i,(ds,label,color) in enumerate([('stage1_sme_size_class','SME size-class',BLUE),('stage2_industry_region_GE10','Industry/region GE10',GRAY)]):
    vals=[cv[(cv.dataset==ds)&(cv.model==m)].iloc[0].r2_mean for m in models]
    err=[cv[(cv.dataset==ds)&(cv.model==m)].iloc[0].r2_std for m in models]
    ax.bar(x+(i-.5)*width, vals, width, yerr=err, label=label, color=color, alpha=1 if i==0 else .55, capsize=3)
ax.set_ylim(0.55,0.93); ax.set_ylabel('GroupKFold R² by country')
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.grid(axis='y', color=LIGHT, linewidth=.7)
ax.spines[['top','right']].set_visible(False)
ax.legend(frameon=False, loc='upper right')
ax.set_title('Country-group validation preserves strong predictive signal', loc='left', fontsize=13, fontweight='bold', color=BLACK)
save(fig,'chart01_groupkfold_model_comparison')

# 2 OLS coefficients top
ols=pd.read_csv(T/'course_ols_coefficients.csv')
sel=pd.concat([ols[ols.dataset=='Stage 1 SME规模层'].sort_values('p_value').head(4), ols[ols.dataset=='Stage 2 行业验证层'].sort_values('p_value').head(4)])
sel['label']=sel['dataset'].str.replace('Stage 1 SME规模层','SME').str.replace('Stage 2 行业验证层','GE10')+' · '+sel['feature_label']
sel=sel.sort_values('coef_std')
fig,ax=plt.subplots(figsize=(8,4.8))
colors=[BLUE if v>0 else "#6B7280" for v in sel.coef_std]
ax.barh(sel['label'], sel['coef_std'], color=colors)
ax.axvline(0,color='#111827',lw=.8)
ax.grid(axis='x', color=LIGHT, linewidth=.7)
ax.spines[['top','right','left']].set_visible(False)
ax.set_xlabel('Standardized OLS coefficient')
ax.set_title('Mechanism direction is dominated by AI capability and digital foundation', loc='left', fontsize=12.5, fontweight='bold')
save(fig,'chart02_ols_mechanism_coefficients')

# 3 GPU baseline vs trees
best=pd.DataFrame([
    {'dataset':'SME size-class','Tree model':'Random Forest','Tree R2':cv[(cv.dataset=='stage1_sme_size_class')&(cv.model=='random_forest')].iloc[0].r2_mean,'MLP R2':pd.read_csv(T/'enhanced_gpu_baseline.csv').query("dataset=='stage1_sme_size_class'").iloc[0].r2},
    {'dataset':'Industry/region GE10','Tree model':'ExtraTrees','Tree R2':cv[(cv.dataset=='stage2_industry_region_GE10')&(cv.model=='extra_trees')].iloc[0].r2_mean,'MLP R2':pd.read_csv(T/'enhanced_gpu_baseline.csv').query("dataset=='stage2_industry_region_GE10'").iloc[0].r2},
])
fig,ax=plt.subplots(figsize=(7.4,4.3))
x=np.arange(len(best)); width=.32
ax.bar(x-width/2,best['Tree R2'],width,color=BLUE,label='Best tree model')
ax.bar(x+width/2,best['MLP R2'],width,color=GRAY,label='A10 GPU MLP')
for i,row in best.iterrows():
    ax.text(i-width/2,row['Tree R2']+.015,f"{row['Tree R2']:.3f}",ha='center',fontsize=9,color=BLACK)
    ax.text(i+width/2,row['MLP R2']+.015,f"{row['MLP R2']:.3f}",ha='center',fontsize=9,color=BLACK)
ax.set_xticks(x); ax.set_xticklabels(best['dataset'])
ax.set_ylim(0.55,0.9); ax.set_ylabel('Holdout / CV R²')
ax.grid(axis='y',color=LIGHT,lw=.7); ax.spines[['top','right']].set_visible(False)
ax.legend(frameon=False)
ax.set_title('More computation did not beat tabular inductive bias', loc='left', fontsize=13, fontweight='bold')
save(fig,'chart03_tree_vs_gpu_mlp')

# 4 feature importance
imp=pd.read_csv(T/'enhanced_permutation_importance.csv')
fig,axes=plt.subplots(1,2,figsize=(10,4.6))
for ax,ds,title in zip(axes,['stage1_sme_size_class','stage2_industry_region_GE10'],['SME size-class','Industry/region GE10']):
    d=imp[imp.dataset==ds].sort_values('importance_mean',ascending=False).head(8).iloc[::-1]
    labels=d['feature_label'].str.replace(' index','',regex=False).str.replace('ecommerce sales  ','',regex=False).str[:28]
    ax.barh(labels,d['importance_mean'],color=BLUE)
    ax.grid(axis='x',color=LIGHT,lw=.7); ax.spines[['top','right','left']].set_visible(False)
    ax.set_title(title, loc='left', fontweight='bold', fontsize=11)
    ax.tick_params(axis='y', labelsize=8)
axes[0].set_xlabel('Permutation importance'); axes[1].set_xlabel('Permutation importance')
fig.suptitle('Feature importance supports a mechanism story, not generic AI enthusiasm', x=.02, ha='left', fontsize=13, fontweight='bold')
save(fig,'chart04_feature_importance_mechanism')

# 5 data quality/lifecycle funnel
ret=pd.read_csv(T/'cleaning_retention_summary.csv')
stages=[('Official rows profiled',12770332),('Non-null observations',10453354),('Mechanism-relevant rows',856880),('Stage 2 panel rows',5814),('Stage 1 model rows',544)]
fig,ax=plt.subplots(figsize=(8,4.5))
y=np.arange(len(stages))[::-1]
vals=[v for _,v in stages]
labels=[k for k,_ in stages]
ax.barh(y,vals,color=[BLUE,'#263B59','#4B5F7A','#7A879A','#A8B1C0'])
ax.set_xscale('log')
ax.set_yticks(y); ax.set_yticklabels(labels)
for yy,v in zip(y,vals): ax.text(v*1.08,yy,f"{v:,}",va='center',fontsize=9,color=BLACK)
ax.grid(axis='x',color=LIGHT,lw=.7); ax.spines[['top','right','left']].set_visible(False)
ax.set_xlabel('Rows / observations, log scale')
ax.set_title('The pipeline narrows large official data into auditable model panels', loc='left', fontsize=13, fontweight='bold')
save(fig,'chart05_data_lifecycle_funnel')

# 6 personas scatter
pers=pd.read_csv(T/'sme_persona_clusters_multisource.csv')
fig,ax=plt.subplots(figsize=(7.2,4.6))
sizes=pers['n']/pers['n'].max()*650+80
ax.scatter(pers['deployment_readiness_index'], pers['security_concern_index'], s=sizes, c=pers['target_workflow_automation'], cmap='Blues', edgecolor=BLUE, linewidth=.8)
for _,r in pers.iterrows(): ax.text(r['deployment_readiness_index']+0.8, r['security_concern_index']+0.1, f"C{int(r['persona_cluster'])}\n{int(r['n'])}", fontsize=8, color=BLACK)
ax.set_xlabel('Deployment readiness'); ax.set_ylabel('Security concern')
ax.grid(color=LIGHT,lw=.7); ax.spines[['top','right']].set_visible(False)
ax.set_title('Personas translate model output into deployment choices', loc='left', fontsize=13, fontweight='bold')
save(fig,'chart06_persona_deployment_map')

print(OUT)
