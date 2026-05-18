import { C, base, rect, txt, rule, interp } from './common.mjs';
export async function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 3, 'Research question', '本研究回答：什么条件下，中小企业会采纳 AI 流程自动化？');
  const cards = [
    ['效率需求', '人工成本 · 重复流程 · 自动化压力', 88],
    ['安全顾虑', '数据边界 · 权限控制 · 治理责任', 474],
    ['部署准备度', '云能力 · API 集成 · 本地化能力', 860]
  ];
  cards.forEach(([a,b,x], i) => {
    rect(slide, ctx, x, 206, 260, 120, C.light, C.line);
    txt(slide, ctx, a, x + 24, 228, 212, 34, { size: 22, color: C.blue, bold: true, align: 'center' });
    txt(slide, ctx, b, x + 24, 272, 212, 38, { size: 13, color: C.gray, align: 'center' });
    if (i < 2) txt(slide, ctx, '×', x + 298, 238, 42, 42, { size: 30, color: C.ink, bold: true, face: C.sans, align: 'center' });
  });
  rule(slide, ctx, 244, 396, 792, C.blue, 3);
  txt(slide, ctx, 'AI workflow automation adoption', 376, 424, 528, 44, { size: 29, color: C.ink, bold: true, face: C.sans, align: 'center' });
  txt(slide, ctx, '目标变量来自 Eurostat：企业使用 AI 自动化流程或辅助决策的比例。', 302, 506, 676, 34, { size: 16, color: C.gray, align: 'center' });
  interp(slide, ctx, 172, 560, 940, [
    '因变量直接对应“流程自动化/辅助决策”，不是泛泛的 AI 热度。',
    '机制框架把效率、安全和部署准备度拆开，保证模型结果可解释。',
    '后续客户画像和部署建议都从这个机制框架推出。'
  ]);
  return slide;
}
