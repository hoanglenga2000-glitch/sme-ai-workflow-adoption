import { C, base, img, interp, metric } from './common.mjs';
export async function slide09(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 9, 'Generalization', '按国家分组的 GroupKFold 说明模型学到的是跨地区采纳机制。', 'Source: outputs/tables/enhanced_cv_results.csv; validation = GroupKFold(geo).');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\charts_rebuilt\\chart01_groupkfold_model_comparison.png", 66, 184, 672, 384, 'contain', 'groupkfold-chart');
  metric(slide, ctx, '0.850', 'RandomForest · Stage 1 SME', 800, 184, 250);
  metric(slide, ctx, '0.724', 'ExtraTrees · Stage 2 GE10', 800, 282, 250);
  interp(slide, ctx, 800, 406, 360, [
    '每个国家只会在某一折中作为测试组出现。',
    '在更严格验证下仍保持较高 R²，比随机切分更有说服力。',
    'Stage 1 支撑 SME 结论，Stage 2 支撑行业/区域外部验证。'
  ]);
  return slide;
}
