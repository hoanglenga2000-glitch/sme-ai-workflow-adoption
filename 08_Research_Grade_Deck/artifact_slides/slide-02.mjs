import { C, base, img, bullets, interp } from './common.mjs';
export async function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 2, 'The real problem', '中小企业想要自动化，但真正约束采纳的是风险承受能力。');
  await img(slide, ctx, "D:\\桌面\\codex\\机械挖掘学习汇报\\github_upload\\sme-ai-workflow-adoption\\08_Research_Grade_Deck\\assets\\imagegen_research_visuals\\03_efficiency_security_deployment_causal_diagram.png", 72, 178, 620, 360, 'contain', 'causal');
  bullets(slide, ctx, [
    '人工成本和重复性流程推动企业寻找自动化工具。',
    '数据安全、权限边界和治理责任会减缓采纳。',
    '部署准备度决定需求能否转化成实际使用。'
  ], 770, 190, 380, 74);
  interp(slide, ctx, 770, 420, 382, [
    '采纳不是单变量决策，而是效率、风险和部署能力的共同结果。',
    '同一种 AI 功能，在不同安全约束下会导向不同部署架构。',
    '先识别企业风险-效率位置，再推荐 SaaS、API、本地或混合部署。'
  ]);
  return slide;
}
