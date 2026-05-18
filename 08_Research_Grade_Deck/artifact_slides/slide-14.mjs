import { C, base, img, interp } from './common.mjs';
export async function slide14(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 14, 'Product landing', 'ai.zhjjq.tech 是把研究机制落到真实 AI 办公流程的操作层。', 'Product visual: ai.zhjjq.tech workstation screenshot and research operating model.');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\imagegen_research_visuals\\06_ai_workstation_operating_model.png", 66, 184, 470, 286, 'contain', 'workstation-model');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\ppt_assets\\browser\\ai_zhjjq_dashboard.png", 598, 188, 560, 290, 'contain', 'ai-workstation-screenshot');
  interp(slide, ctx, 146, 520, 940, [
    '研究模型判断企业效率需求、安全顾虑和部署准备度。',
    'AI 工作站承接智能体、组织知识、流程任务和治理反馈。',
    '产品落地让课程模型从预测结果走向可执行的 AI 办公部署方案。'
  ]);
  return slide;
}
