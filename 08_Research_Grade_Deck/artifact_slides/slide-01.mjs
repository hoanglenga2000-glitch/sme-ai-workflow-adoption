import { C, rect, txt, rule, metric, img } from './common.mjs';
export async function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  txt(slide, ctx, 'RESEARCH DEFENSE', 64, 44, 300, 22, { size: 11, color: C.blue, bold: true, face: C.sans });
  rule(slide, ctx, 64, 76, 64, C.blue, 3);
  txt(slide, ctx, 'AI 流程自动化采纳不是技术选择，而是中小企业的组织决策。', 64, 128, 620, 142, { size: 34, color: C.ink, bold: true, face: C.font });
  txt(slide, ctx, '基于效率需求、安全顾虑与部署偏好的实证分析', 66, 292, 620, 36, { size: 17, color: C.gray, face: C.font });
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\imagegen_research_visuals\\001-out-01-ai-workflow-adoption-mechanism-png-prompt-academic-ve.png", 758, 106, 438, 300, 'contain', 'mechanism');
  metric(slide, ctx, '12.77M', 'Stage 2 官方行数画像', 66, 454, 180);
  metric(slide, ctx, '0.850', 'SME GroupKFold R²', 278, 454, 180);
  metric(slide, ctx, '0.724', 'GE10 外部验证 R²', 490, 454, 190);
  txt(slide, ctx, 'Official Eurostat data · SHA256 validation · GroupKFold by country · NVIDIA A10 MLP baseline', 66, 604, 780, 26, { size: 12, color: C.ink, face: C.sans });
  rule(slide, ctx, 64, 670, 1152, C.line, 1);
  txt(slide, ctx, 'Data: Eurostat SDMX-CSV; Evidence tables: outputs/tables/enhanced_*.csv', 64, 682, 900, 22, { size: 9, color: C.gray, face: C.sans });
  txt(slide, ctx, '01', 1170, 680, 48, 24, { size: 13, color: C.gray, face: C.mono, align: 'right' });
  return slide;
}
