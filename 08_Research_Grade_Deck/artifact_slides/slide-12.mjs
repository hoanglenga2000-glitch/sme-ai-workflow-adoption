import { C, base, img, interp } from './common.mjs';
export async function slide12(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 12, 'Deployment implication', 'SaaS、API、本地和混合部署，本质上是风险-效率权衡的结果。', 'Framework: model/persona outputs + NIST AI RMF governance logic.');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\imagegen_research_visuals\\04_deployment_matrix.png", 72, 184, 650, 400, 'contain', 'deployment-matrix');
  interp(slide, ctx, 790, 210, 370, [
    '效率需求越强，企业越倾向快速上线自动化能力。',
    '安全顾虑越强，企业越需要 API、私有化或混合部署边界。',
    '部署矩阵把模型结论转化为产品方案选择。'
  ]);
  return slide;
}
