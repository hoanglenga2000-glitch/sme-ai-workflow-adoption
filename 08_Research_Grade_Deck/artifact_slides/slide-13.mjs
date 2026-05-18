import { C, base, img, interp, metric } from './common.mjs';
export async function slide13(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 13, 'Segmentation', '客户画像把模型结果转化为可落地的企业部署策略。', 'Source: outputs/tables/sme_persona_clusters_multisource.csv.');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\charts_rebuilt\\chart06_persona_deployment_map.png", 76, 170, 590, 386, 'contain', 'persona-chart');
  metric(slide, ctx, 'C3', '最高流程自动化采纳画像', 742, 176, 160);
  metric(slide, ctx, '13.36%', 'workflow automation mean', 990, 176, 190);
  interp(slide, ctx, 760, 314, 380, [
    '不同画像在部署准备度和安全顾虑上存在结构性差异。',
    '同一套 AI 功能不能用单一部署方案覆盖所有中小企业。',
    '画像结果可直接服务于销售、交付和部署方案推荐。'
  ]);
  return slide;
}
