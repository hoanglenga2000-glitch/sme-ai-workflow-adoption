import { C, base, img, interp } from './common.mjs';
export async function slide11(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 11, 'Interpretability', '特征重要性支持效率-安全-部署机制，而不是泛泛的 AI 热度。', 'Source: outputs/tables/enhanced_permutation_importance.csv.');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\charts_rebuilt\\chart04_feature_importance_mechanism.png", 54, 184, 710, 404, 'contain', 'importance-chart');
  interp(slide, ctx, 805, 212, 360, [
    'SME 层最强变量是 ML capability，Stage 2 也由 ML 能力和 NLG 支撑。',
    '数字基础、部署准备度和国家/行业异质性共同解释采纳差异。',
    '特征重要性把预测结果转化为可执行的企业分层依据。'
  ]);
  return slide;
}
