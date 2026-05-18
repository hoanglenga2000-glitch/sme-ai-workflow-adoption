#!/usr/bin/env python3
"""Render lightweight SVG charts from pipeline outputs without extra plotting libs."""
from __future__ import annotations

from pathlib import Path
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

PALETTE = ["#1f6f8b", "#46a08d", "#d48b32", "#7a4c9f", "#b94343", "#334155"]

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg_wrap(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#ffffff"/>{body}</svg>'

def text(x, y, s, size=12, fill="#111827", anchor="start", weight="400"):
    return f'<text x="{x}" y="{y}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'

def line_chart():
    df = pd.read_csv(OUT / "01_eu_ai_adoption_trends.csv")
    df = df[(df["size_emp"].isin(["10-249", "GE250"])) & (df["indic_is"].isin(["E_AI_TANY", "E_AI_TPA", "E_AI_TNLG", "E_AI_TML"]))]
    series = list(df.groupby(["size_emp", "indicator_label"]))
    w, h = 1100, 650
    ml, mr, mt, mb = 95, 260, 70, 80
    xs = sorted(df["year"].unique())
    ymin, ymax = 0, math.ceil(df["value"].max() / 10) * 10
    def sx(year): return ml + (year - min(xs)) / (max(xs)-min(xs)) * (w-ml-mr)
    def sy(v): return h-mb - (v-ymin)/(ymax-ymin) * (h-mt-mb)
    body = text(w/2, 36, "EU AI adoption trends by enterprise size", 24, anchor="middle", weight="700")
    for i in range(6):
        y = h-mb - i/5*(h-mt-mb); val = ymin + i/5*(ymax-ymin)
        body += f'<line x1="{ml}" y1="{y:.1f}" x2="{w-mr}" y2="{y:.1f}" stroke="#e5e7eb"/>' + text(50, y+4, f"{val:.0f}", 12, "#64748b")
    for x in xs:
        body += text(sx(x), h-35, str(int(x)), 12, "#64748b", anchor="middle")
    body += text(20, h/2, "Percent of enterprises", 13, "#475569")
    for idx, ((size, label), g) in enumerate(series):
        g = g.sort_values("year")
        pts = " ".join(f"{sx(r.year):.1f},{sy(r.value):.1f}" for r in g.itertuples())
        color = PALETTE[idx % len(PALETTE)]
        dash = "6 5" if size == "GE250" else ""
        body += f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}"/>'
        for r in g.itertuples():
            body += f'<circle cx="{sx(r.year):.1f}" cy="{sy(r.value):.1f}" r="4" fill="{color}"/>'
        body += f'<rect x="{w-mr+25}" y="{95+idx*44}" width="18" height="4" fill="{color}"/>' + text(w-mr+52, 101+idx*44, f"{size} | {label[:38]}", 12)
    (OUT / "01_eu_ai_adoption_trends.svg").write_text(svg_wrap(w,h,body), encoding="utf-8")

def bar_chart():
    df = pd.read_csv(OUT / "02_sme_workflow_automation_country_rank.csv").head(18)
    w, h = 1050, 720
    ml, mt, mb, mr = 250, 70, 50, 80
    maxv = df["target_workflow_automation"].max()
    step = (h-mt-mb)/len(df)
    body = text(w/2, 36, "Top SME AI workflow automation adoption countries, 2025", 23, anchor="middle", weight="700")
    for i,r in enumerate(df.itertuples()):
        y = mt + i*step + 4
        bw = (r.target_workflow_automation / maxv) * (w-ml-mr)
        body += text(ml-12, y+18, r.country, 13, "#334155", anchor="end")
        body += f'<rect x="{ml}" y="{y}" width="{bw:.1f}" height="{step*0.68:.1f}" rx="3" fill="#1f6f8b"/>'
        body += text(ml+bw+8, y+18, f"{r.target_workflow_automation:.1f}%", 12, "#0f172a")
    (OUT / "02_sme_workflow_automation_country_rank.svg").write_text(svg_wrap(w,h,body), encoding="utf-8")

def heatmap():
    df = pd.read_csv(OUT / "03_size_lifecycle_heatmap_data.csv")
    df = df[(df["geo"]=="EU27_2020") & (df["year"]==df["year"].max())]
    metrics = ["target_workflow_automation","target_any_ai","security_concern_index","deployment_readiness_index","governance_maturity_proxy"]
    labels = ["Workflow automation","Any AI","Security concern","Deployment readiness","Governance maturity"]
    sizes = ["10-49","50-249","GE250"]
    w,h=1050,430; ml,mt=180,90; cw,ch=155,78
    vals = df[metrics].to_numpy().flatten(); mn, mx = float(pd.Series(vals).min()), float(pd.Series(vals).max())
    body = text(w/2, 36, "AI adoption lifecycle indicators by size, EU 2025", 23, anchor="middle", weight="700")
    for j,l in enumerate(labels): body += text(ml+j*cw+cw/2, 70, l, 12, "#334155", anchor="middle")
    for i,s in enumerate(sizes):
        row = df[df["size_emp"]==s]
        body += text(ml-14, mt+i*ch+ch/2+5, s, 14, "#334155", anchor="end", weight="700")
        for j,m in enumerate(metrics):
            v = float(row[m].iloc[0]) if not row.empty and pd.notna(row[m].iloc[0]) else 0
            t=(v-mn)/(mx-mn) if mx>mn else 0
            r=int(239-(239-31)*t); g=int(246-(246-111)*t); b=int(255-(255-139)*t)
            fill=f"#{r:02x}{g:02x}{b:02x}"
            body += f'<rect x="{ml+j*cw}" y="{mt+i*ch}" width="{cw-6}" height="{ch-6}" rx="4" fill="{fill}"/>'
            body += text(ml+j*cw+cw/2, mt+i*ch+ch/2+5, f"{v:.1f}", 18, "#0f172a", anchor="middle", weight="700")
    (OUT / "03_size_lifecycle_heatmap.svg").write_text(svg_wrap(w,h,body), encoding="utf-8")

def importance_chart():
    df = pd.read_csv(OUT / "04_model_feature_importance_data.csv").head(14)
    w,h=1050,620; ml,mt,mb,mr=280,70,50,80
    mx=max(df["importance_mean"].max(), 0.001); step=(h-mt-mb)/len(df)
    body=text(w/2,36,"Model drivers of AI workflow automation adoption",23,anchor="middle",weight="700")
    for i,r in enumerate(df.itertuples()):
        y=mt+i*step+4; bw=(max(r.importance_mean,0)/mx)*(w-ml-mr)
        body += text(ml-12,y+18,r.feature,13,"#334155",anchor="end")
        body += f'<rect x="{ml}" y="{y}" width="{bw:.1f}" height="{step*0.65:.1f}" rx="3" fill="#7a4c9f"/>'
        body += text(ml+bw+8,y+18,f"{r.importance_mean:.3f}",12)
    (OUT / "04_model_feature_importance.svg").write_text(svg_wrap(w,h,body), encoding="utf-8")

def persona_chart():
    df = pd.read_csv(OUT / "05_sme_persona_clusters_data.csv")
    metrics=["target_workflow_automation","target_any_ai","security_concern_index","deployment_readiness_index","governance_maturity_proxy"]
    labels=["Workflow","Any AI","Security","Deploy","Governance"]
    w,h=1050,600; ml,mt=95,80; chartw, charth=820,380
    maxv = df[metrics].max().max()
    body=text(w/2,36,"SME personas from clustering",23,anchor="middle",weight="700")
    groupw=chartw/len(df); barw=groupw/(len(metrics)+1)
    for i,r in enumerate(df.itertuples()):
        x0=ml+i*groupw
        body += text(x0+groupw/2, mt+charth+35, f"Cluster {int(r.persona_cluster)}\nn={int(r.n)}", 12, "#334155", anchor="middle")
        for j,m in enumerate(metrics):
            v=float(getattr(r,m)); bh=v/maxv*charth
            x=x0+j*barw+8; y=mt+charth-bh
            body += f'<rect x="{x:.1f}" y="{y:.1f}" width="{barw-10:.1f}" height="{bh:.1f}" fill="{PALETTE[j]}"/>'
    for j,l in enumerate(labels):
        body += f'<rect x="930" y="{95+j*32}" width="14" height="14" fill="{PALETTE[j]}"/>' + text(952,108+j*32,l,12)
    (OUT / "05_sme_persona_clusters.svg").write_text(svg_wrap(w,h,body), encoding="utf-8")

if __name__ == "__main__":
    line_chart(); bar_chart(); heatmap(); importance_chart(); persona_chart()
    print("rendered", len(list(OUT.glob("*.svg"))), "svg charts")
