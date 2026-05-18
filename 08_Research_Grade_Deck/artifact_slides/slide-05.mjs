import { C, base, img, interp } from './common.mjs';
export async function slide05(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 5, 'Data lifecycle', '数字生命周期把海量官方数据收敛为可审计的建模面板。', 'Source: outputs/tables/cleaning_retention_summary.csv; outputs/reports/stage2_source_profile.md');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\charts_rebuilt\\chart05_data_lifecycle_funnel.png", 70, 184, 650, 374, 'contain', 'lifecycle-funnel');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\imagegen_research_visuals\\02_data_lifecycle_pipeline.png", 780, 184, 360, 180, 'contain', 'lifecycle-visual');
  interp(slide, ctx, 780, 402, 380, [
    '12.77M 行官方数据先经过画像，再进入机制指标筛选。',
    '保留率低不是缺陷，而是排除无关指标后的质量控制。',
    '最终面板可审计、可复跑，并能支撑机器学习建模。'
  ]);
  return slide;
}
