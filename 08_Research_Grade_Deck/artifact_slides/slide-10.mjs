import { C, base, img, interp } from './common.mjs';
export async function slide10(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 10, 'Model finding', 'A10 GPU MLP 没有超过树模型，说明结构化官方统计更适合表格学习器。', 'Source: outputs/tables/enhanced_gpu_baseline.csv; enhanced_cv_results.csv.');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\charts_rebuilt\\chart03_tree_vs_gpu_mlp.png", 78, 170, 600, 386, 'contain', 'gpu-vs-tree');
  interp(slide, ctx, 760, 206, 392, [
    'MLP 在 NVIDIA A10 上成功训练，但 R² 低于随机森林和 ExtraTrees。',
    '这不是失败，而是模型选择结论：更多算力不自动带来更好泛化。',
    '本研究最终选择树模型作为主预测器，同时保留 GPU 基线作为课程证据。'
  ]);
  return slide;
}
