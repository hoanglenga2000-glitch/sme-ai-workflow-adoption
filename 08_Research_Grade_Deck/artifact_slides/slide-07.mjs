import { C, base, txt, rule, interp } from './common.mjs';
export async function slide07(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 7, 'Model strategy', '模型设计把解释、预测、泛化和深度学习基线分开处理。', 'Source: src/course_ml_diagnostics.py; src/enhanced_training_gpu.py');
  const rows = [
    ['01', 'OLS / 多元线性回归', '用于识别机制方向、显著性和 VIF 共线性风险。'],
    ['02', 'Random Forest / ExtraTrees', '用于捕捉非线性关系，并通过特征重要性解释机制。'],
    ['03', 'GroupKFold by country', '按国家分组验证，降低同一国家观测泄漏带来的虚高分数。'],
    ['04', 'A10 GPU MLP baseline', '作为深度学习对照，不把 GPU 算力强行包装成最优模型。']
  ];
  rows.forEach((r, i) => {
    const y = 180 + i * 86;
    txt(slide, ctx, r[0], 94, y, 52, 32, { size: 20, color: C.blue, bold: true, face: C.mono });
    txt(slide, ctx, r[1], 180, y - 2, 300, 34, { size: 21, color: C.ink, bold: true, face: C.sans });
    txt(slide, ctx, r[2], 518, y, 560, 40, { size: 16, color: C.gray });
    rule(slide, ctx, 94, y + 56, 1000, C.line, 1);
  });
  interp(slide, ctx, 160, 550, 900, [
    '不是只追求最高 R²，而是把模型功能和研究问题对应起来。',
    'GroupKFold 让结果更接近跨国家、跨组织环境的泛化能力。',
    '课程目标中的监督学习、回归、模型评估和深度学习基线都得到体现。'
  ]);
  return slide;
}
