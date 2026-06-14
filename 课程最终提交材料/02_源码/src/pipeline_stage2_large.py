#!/usr/bin/env python3
"""Stage-2 large-data feature extraction and modeling.

Uses 12.7M+ official Eurostat rows to build NACE/region/business-structure
features, then predicts AI workflow automation adoption without target leakage.
"""
from __future__ import annotations
import csv, gzip, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import MiniBatchKMeans

ROOT = Path(__file__).resolve().parents[1]
RAW1 = ROOT / 'data' / 'raw' / 'eurostat'
RAW2 = ROOT / 'data' / 'raw' / 'eurostat_stage2'
PRO = ROOT / 'data' / 'processed'
TAB = ROOT / 'outputs' / 'tables'
REP = ROOT / 'outputs' / 'reports'
FIG = ROOT / 'outputs' / 'figures'
for p in [PRO,TAB,REP,FIG,ROOT/'data'/'samples']:
    p.mkdir(parents=True, exist_ok=True)

COUNTRY = {'EU27_2020':'EU-27','EA':'Euro area','BE':'Belgium','BG':'Bulgaria','CZ':'Czechia','DK':'Denmark','DE':'Germany','EE':'Estonia','IE':'Ireland','EL':'Greece','ES':'Spain','FR':'France','HR':'Croatia','IT':'Italy','CY':'Cyprus','LV':'Latvia','LT':'Lithuania','LU':'Luxembourg','HU':'Hungary','MT':'Malta','NL':'Netherlands','AT':'Austria','PL':'Poland','PT':'Portugal','RO':'Romania','SI':'Slovenia','SK':'Slovakia','FI':'Finland','SE':'Sweden','NO':'Norway','BA':'Bosnia and Herzegovina','ME':'Montenegro','MK':'North Macedonia','AL':'Albania','RS':'Serbia','TR':'T?rkiye'}
SIZE_ORDER = {'10-49':1, '50-249':2, '10-249':3, 'GE250':4, 'GE10':5}

TARGET_KEEP = {'E_AI_TPA','E_AI_TML','E_AI_TNLG','E_AI_PBAM','E_AI_PITS','E_AI_BCDP','E_AI_BLEG','E_AI_BEC','E_AI_BDDT','E_AI_BLE','E_AI_BCST','E_AI_BINC','E_AI_BNU','E_AI_BIAS','E_AI_CC','E_AI_DA','E_AI_CC1SI_DA'}
FEATURE_KEEP = {
 'isoc_cicce_usen2': {'E_CC','E_CC1_SI','E_CC1_S','E_CC_PSEC','E_CC_PDEV','E_CC_DA','E_CC_PCPU','E_CC_PCRM','E_CC_PERP'},
 'isoc_e_diin2': {'E_DI3_GELO','E_DI3_HI','E_DI3_VHI','E_DI4_GELO','E_DI4_HI','E_DI4_VHI'},
 'isoc_eb_dan2': {'E_DA','E_DASANY','E_DASGE3','E_DASCRM','E_DASERP','E_DASSDS','E_DASWEB'},
 'isoc_eb_bdn2': {'E_BDA','E_BDAML','E_BDANL','E_BDAINT','E_BDAEXT'},
 'isoc_ec_eseln2': {'E_AESELL','E_ESELL','E_AWSELL','E_AWS_COWN','E_AWS_CMP','E_AWSDS','E_AWSFOR'},
 'isoc_ske_itspen2': {'E_ITSP'},
 'isoc_ske_ittn2': {'E_ITT2','E_ITSPT2','E_ITUST2'},
 'isoc_ske_itrcrn2': {'E_ITSPRCR2','E_ITSPVAC2','E_ITSPDLA','E_ITSPDLET','E_ITSPDLWE','E_ITSPDSAL'},
 'isoc_r_cicce_usen2': {'E_CC'},
 'isoc_r_eb_dan2': {'E_DA','E_DASANY','E_DASGE3'},
}
SBS_KEEP = {'V11110','V12110','V12150','V16110','V16130','V13310','V13320','V13330'}
BD_KEEP = {'V97010','V97020','V97030','V97040','V97110','V97120'}

def read_sdmx(path: Path, dataset: str, keep: set[str] | None = None, max_rows: int | None = None):
    opener = gzip.open if path.suffix == '.gz' else open
    mode = 'rt' if path.suffix == '.gz' else 'r'
    rows=[]; seen=0
    with opener(path, mode, encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        for r in reader:
            seen += 1
            indic = r.get('indic_is') or r.get('indic_sbs') or r.get('indic_sb') or ''
            if keep and indic not in keep:
                continue
            val = r.get('OBS_VALUE')
            if val in ('', None):
                continue
            try: value=float(val)
            except Exception: continue
            year = r.get('TIME_PERIOD')
            try: year=int(float(year))
            except Exception: continue
            rows.append({
                'dataset': dataset, 'geo': r.get('geo',''), 'year': year, 'size_emp': r.get('size_emp',''),
                'nace_r2': r.get('nace_r2',''), 'indicator': indic, 'unit': r.get('unit',''), 'value': value
            })
            if max_rows and len(rows) >= max_rows: break
    return pd.DataFrame(rows), seen

def pivot_features(df: pd.DataFrame, prefix: str, index_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=index_cols)
    df=df.copy(); df['feature']=prefix+'__'+df['indicator']
    return df.pivot_table(index=index_cols, columns='feature', values='value', aggfunc='mean').reset_index()

def main():
    stats={'source_rows_scanned':0, 'feature_rows_kept':0}
    # Target by country-year-industry/size from AI NACE table.
    ai_df, scanned = read_sdmx(RAW2/'isoc_eb_ain2_sdmx.csv.gz','isoc_eb_ain2', TARGET_KEEP)
    stats['source_rows_scanned'] += scanned; stats['feature_rows_kept'] += len(ai_df)
    ai_df = ai_df[ai_df['size_emp'].isin(['GE10','10-49','50-249','10-249','GE250'])]
    target_panel = pivot_features(ai_df, 'ai_industry', ['geo','year','size_emp','nace_r2'])
    target_panel['target_workflow_automation'] = target_panel.get('ai_industry__E_AI_TPA')
    target_panel = target_panel.dropna(subset=['target_workflow_automation'])

    # Industry digital features by country-year-industry/size.
    panel = target_panel.copy()
    for code, keep in FEATURE_KEEP.items():
        path = RAW2 / f'{code}_sdmx.csv.gz'
        if not path.exists(): continue
        df, scanned = read_sdmx(path, code, keep)
        stats['source_rows_scanned'] += scanned; stats['feature_rows_kept'] += len(df)
        if 'size_emp' in df.columns:
            df = df[df['size_emp'].isin(['GE10','10-49','50-249','10-249','GE250'])]
        pv = pivot_features(df, code, ['geo','year','size_emp','nace_r2'])
        panel = panel.merge(pv, on=['geo','year','size_emp','nace_r2'], how='left')

    # Regional features aggregated to country-year-industry.
    for code, keep in {'isoc_r_eb_ain2': {'E_AI_TML','E_AI_TNLG','E_AI_PITS','E_AI_BCDP'}, 'isoc_r_cicce_usen2': {'E_CC'}, 'isoc_r_eb_dan2': {'E_DA','E_DASANY'}}.items():
        path = RAW2 / f'{code}_sdmx.csv.gz'
        df, scanned = read_sdmx(path, code, keep)
        stats['source_rows_scanned'] += scanned; stats['feature_rows_kept'] += len(df)
        if df.empty: continue
        df['geo_country'] = df['geo'].str[:2]
        agg = df.groupby(['geo_country','year','nace_r2','indicator'], as_index=False)['value'].mean()
        agg = agg.rename(columns={'geo_country':'geo'})
        agg['size_emp'] = 'REGION_AGG'
        pv = pivot_features(agg, code+'_regionmean', ['geo','year','nace_r2'])
        panel = panel.merge(pv, on=['geo','year','nace_r2'], how='left')

    # Business structure and high growth indicators by country-year-industry.
    for code, keep in {'sbs_sc_ovw': SBS_KEEP, 'sbs_ovw_act': SBS_KEEP, 'bd_9pm_r2': BD_KEEP, 'bd_hg': BD_KEEP}.items():
        path = RAW2 / f'{code}_sdmx.csv.gz'
        df, scanned = read_sdmx(path, code, keep)
        stats['source_rows_scanned'] += scanned; stats['feature_rows_kept'] += len(df)
        if df.empty: continue
        if code == 'sbs_sc_ovw':
            if 'size_emp' in df.columns:
                df = df[df['size_emp'].isin(['GE10','10-49','50-249','10-249','GE250'])]
            pv = pivot_features(df, code, ['geo','year','size_emp','nace_r2'])
            panel = panel.merge(pv, on=['geo','year','size_emp','nace_r2'], how='left')
        else:
            pv = pivot_features(df, code, ['geo','year','nace_r2'])
            panel = panel.merge(pv, on=['geo','year','nace_r2'], how='left')

    # Engineered indices.
    def mean_cols(cols):
        cols=[c for c in cols if c in panel.columns]
        return panel[cols].mean(axis=1) if cols else np.nan
    panel['security_concern_index'] = mean_cols(['ai_industry__E_AI_BCDP','ai_industry__E_AI_BLEG','ai_industry__E_AI_BEC','ai_industry__E_AI_BDDT','ai_industry__E_AI_BLE','ai_industry__E_AI_BCST','ai_industry__E_AI_BINC'])
    panel['deployment_readiness_index'] = mean_cols(['isoc_cicce_usen2__E_CC','isoc_cicce_usen2__E_CC1_SI','isoc_cicce_usen2__E_CC1_S','isoc_cicce_usen2__E_CC_PDEV','isoc_cicce_usen2__E_CC_PSEC'])
    panel['data_maturity_index'] = mean_cols(['isoc_eb_dan2__E_DA','isoc_eb_dan2__E_DASANY','isoc_eb_dan2__E_DASGE3','isoc_eb_bdn2__E_BDA','isoc_eb_bdn2__E_BDAML'])
    panel['digital_foundation_index'] = mean_cols(['isoc_e_diin2__E_DI3_GELO','isoc_e_diin2__E_DI3_HI','isoc_e_diin2__E_DI3_VHI','isoc_e_diin2__E_DI4_GELO','isoc_e_diin2__E_DI4_HI','isoc_e_diin2__E_DI4_VHI'])
    panel['market_digitization_index'] = mean_cols(['isoc_ec_eseln2__E_AESELL','isoc_ec_eseln2__E_ESELL','isoc_ec_eseln2__E_AWSELL','isoc_ec_eseln2__E_AWS_COWN','isoc_ec_eseln2__E_AWS_CMP'])
    panel['ict_constraint_index'] = mean_cols(['isoc_ske_itrcrn2__E_ITSPVAC2','isoc_ske_itrcrn2__E_ITSPDLA','isoc_ske_itrcrn2__E_ITSPDLET','isoc_ske_itrcrn2__E_ITSPDLWE','isoc_ske_itrcrn2__E_ITSPDSAL'])
    panel['governance_maturity_proxy'] = mean_cols(['ai_industry__E_AI_BIAS','ai_industry__E_AI_PITS','isoc_cicce_usen2__E_CC_PSEC'])
    panel['country'] = panel['geo'].map(COUNTRY).fillna(panel['geo'])
    panel['size_rank'] = panel['size_emp'].map(SIZE_ORDER).fillna(0)

    PRO.mkdir(exist_ok=True, parents=True)
    panel.to_csv(PRO/'stage2_industry_panel.csv', index=False)
    panel.head(3000).to_csv(ROOT/'data'/'samples'/'stage2_industry_panel_sample.csv', index=False)

    target='target_workflow_automation'
    leakage = {target, 'ai_industry__E_AI_TPA'}
    features = ['year','geo','size_emp','nace_r2','size_rank'] + [c for c in panel.columns if ('__' in c or c.endswith('_index') or c.endswith('_proxy')) and c not in leakage]
    data = panel[features+[target]].dropna(subset=[target]).copy()
    keep=['year','geo','size_emp','nace_r2','size_rank']
    for c in features:
        if c in keep: continue
        if data[c].notna().mean() >= 0.15:
            keep.append(c)
    features=keep
    X=data[features]; y=data[target]
    # Random split and country-group split for robustness.
    tx, vx, ty, vy = train_test_split(X,y,test_size=0.25,random_state=42)
    numeric=[c for c in features if c not in ['geo','size_emp','nace_r2']]
    categorical=[c for c in ['geo','size_emp','nace_r2'] if c in features]
    prep=ColumnTransformer([
        ('num', Pipeline([('imp', SimpleImputer(strategy='median')),('sc',StandardScaler())]), numeric),
        ('cat', Pipeline([('imp', SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore'))]), categorical),
    ])
    models={
        'ridge': Ridge(alpha=1.0),
        'random_forest': RandomForestRegressor(n_estimators=800, random_state=42, min_samples_leaf=3, n_jobs=-1),
        'extra_trees': ExtraTreesRegressor(n_estimators=800, random_state=42, min_samples_leaf=3, n_jobs=-1),
        'hist_gradient_boosting': HistGradientBoostingRegressor(max_iter=500, learning_rate=0.04, random_state=42, l2_regularization=0.05),
    }
    results={}; fitted={}
    for name,m in models.items():
        pipe=Pipeline([('prep',prep),('model',m)])
        pipe.fit(tx,ty); pred=pipe.predict(vx)
        results[name]={'r2':float(r2_score(vy,pred)), 'mae':float(mean_absolute_error(vy,pred)), 'n_test':int(len(vy))}
        fitted[name]=pipe
    best_name=max(results, key=lambda k: results[k]['r2'])
    best=fitted[best_name]
    # Use single-process permutation importance so the pipeline also reruns from
    # Windows folders with non-ASCII names; joblib's memmap tracker can fail
    # there before model evaluation finishes.
    perm=permutation_importance(best, vx, vy, scoring='r2', n_repeats=12, random_state=42, n_jobs=1)
    imp=pd.DataFrame({'feature':features,'importance_mean':perm.importances_mean,'importance_std':perm.importances_std}).sort_values('importance_mean', ascending=False)
    imp.to_csv(TAB/'stage2_feature_importance.csv', index=False)

    # Persona clustering on SME rows.
    persona_cols=[c for c in ['target_workflow_automation','security_concern_index','deployment_readiness_index','data_maturity_index','digital_foundation_index','market_digitization_index','ict_constraint_index','governance_maturity_proxy'] if c in panel]
    pdata=panel[panel['size_emp'].isin(['GE10','10-49','50-249','10-249'])][['geo','country','year','size_emp','nace_r2']+persona_cols].dropna(subset=['target_workflow_automation']).copy()
    mat=pdata[persona_cols].fillna(pdata[persona_cols].median(numeric_only=True))
    pdata['persona_cluster']=MiniBatchKMeans(n_clusters=6, random_state=42, n_init=20, batch_size=1024).fit_predict(StandardScaler().fit_transform(mat))
    pdata.to_csv(PRO/'stage2_persona_assignments.csv', index=False)
    personas=pdata.groupby('persona_cluster')[persona_cols].mean().round(2)
    personas['n']=pdata.groupby('persona_cluster').size()
    personas=personas.sort_values('target_workflow_automation', ascending=False)
    personas.to_csv(TAB/'stage2_persona_clusters.csv')

    # Reports.
    profile=json.loads((REP/'stage2_source_profile.json').read_text(encoding='utf-8'))
    source_rows=sum(x['rows'] for x in profile)
    nonnull=sum(x['nonnull_obs'] for x in profile)
    report=[]
    report.append('# Stage 2 Large-Scale Data Mining Results\n\n')
    report.append(f'Official stage-2 source rows profiled: {source_rows:,}; non-null observations: {nonnull:,}; source files: {len(profile)}.\n\n')
    report.append(f'Rows scanned in feature extraction: {stats["source_rows_scanned"]:,}; rows kept after indicator filtering: {stats["feature_rows_kept"]:,}.\n\n')
    report.append(f'Integrated GE10 industry panel rows: {len(panel):,}; modeling rows: {len(data):,}; features after coverage/leakage control: {len(features)}.\n\n')
    report.append('## Model Metrics\n\n')
    report.append(f'Best model: `{best_name}`.\n\n')
    for name,m in results.items(): report.append(f'- {name}: R2={m["r2"]:.3f}, MAE={m["mae"]:.3f}, n_test={m["n_test"]}\n')
    report.append('\n## Top Features\n\n')
    report.append(imp.head(20).round(4).to_markdown(index=False)+'\n\n')
    report.append('## SME Persona Clusters\n\n')
    report.append(personas.to_markdown()+'\n')
    (REP/'stage2_large_model_results.md').write_text(''.join(report), encoding='utf-8')
    (REP/'stage2_large_model_metrics.json').write_text(json.dumps({'stats':stats,'model_rows':len(data),'panel_rows':len(panel),'feature_count':len(features),'metrics':results,'best_model':best_name}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'stage2_source_rows':source_rows,'stage2_nonnull_obs':nonnull,'panel_rows':len(panel),'model_rows':len(data),'feature_count':len(features),'best_model':best_name,'metrics':results}, indent=2))

if __name__ == '__main__':
    main()


