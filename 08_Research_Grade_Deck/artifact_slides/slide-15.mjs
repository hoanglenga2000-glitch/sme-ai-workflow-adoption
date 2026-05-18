import { C, base, txt, rule, interp } from './common.mjs';
export async function slide15(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 15, 'Final contribution', '本项目贡献了一条从官方数据到可部署 AI 流程策略的复现路径。');
  const rows = [
    ['01', '数据可信', 'Eurostat 官方数据、manifest、SHA256 和清洗日志共同支撑真实性。'],
    ['02', '机器学习严谨', 'OLS、RandomForest、ExtraTrees、GroupKFold 和 A10 MLP 基线形成完整算法链。'],
    ['03', '机制解释', '效率需求 × 安全顾虑 × 部署准备度解释 AI 流程自动化采纳。'],
    ['04', '产品价值', 'SaaS / API / 本地 / 混合部署策略服务真实 AI 办公场景。']
  ];
  rows.forEach((r, i) => {
    const y = 182 + i * 82;
    txt(slide, ctx, r[0], 94, y, 56, 34, { size: 21, color: C.blue, bold: true, face: C.mono });
    rule(slide, ctx, 160, y + 18, 76, C.blue, 2);
    txt(slide, ctx, r[1], 270, y - 2, 180, 34, { size: 22, color: C.ink, bold: true });
    txt(slide, ctx, r[2], 506, y, 560, 42, { size: 16, color: C.gray });
  });
  interp(slide, ctx, 152, 540, 980, [
    '结论不止是一个模型分数，而是一套可解释采纳机制。',
    '课程中的数据生命周期、监督学习、回归、集成学习、聚类和深度学习基线均已体现。',
    '下一步可以接入国内问卷与真实工作流日志，形成更强的中小企业本土化研究。'
  ]);
  return slide;
}
