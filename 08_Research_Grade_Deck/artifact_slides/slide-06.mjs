import { C, base, img, interp } from './common.mjs';
export async function slide06(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 6, 'Mechanism framework', '采纳机制不是“AI 热情”，而是效率需求被安全与部署能力约束。');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\imagegen_research_visuals\\001-out-01-ai-workflow-adoption-mechanism-png-prompt-academic-ve.png", 78, 184, 660, 398, 'contain', 'mechanism-framework');
  interp(slide, ctx, 800, 220, 360, [
    '效率需求、安全顾虑和部署准备度共同指向采纳结果。',
    '所以模型需要同时纳入 AI 能力、数字基础、治理和云/数据能力。',
    '部署建议必须判断企业受哪一类机制力量主导。'
  ]);
  return slide;
}
