import { C, base, img, interp, metric } from './common.mjs';
export async function slide08(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 8, 'Mechanism evidence', 'OLS 先确认机制方向，再由非线性模型提升预测解释力。', 'Source: outputs/tables/course_ols_coefficients.csv; course_vif_diagnostics.csv');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\charts_rebuilt\\chart02_ols_mechanism_coefficients.png", 64, 184, 680, 390, 'contain', 'ols-chart');
  metric(slide, ctx, '7.59', 'SME 机器学习能力标准化系数', 800, 184, 280);
  metric(slide, ctx, '4.19', 'GE10 行业机器学习能力系数', 800, 296, 280);
  interp(slide, ctx, 800, 438, 360, [
    '机器学习能力是最强正向机制变量。',
    '云和数据能力方向有意义；最大 VIF=14.4，不能过度因果化。',
    '因此 OLS 用于机制解释，树模型用于最终预测。'
  ]);
  return slide;
}
