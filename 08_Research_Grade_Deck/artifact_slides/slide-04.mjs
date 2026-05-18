import { C, base, rect, txt, rule, interp } from './common.mjs';
export async function slide04(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 4, 'Data credibility', '数据可信度来自官方来源、哈希校验和可复现实验流程。', 'Sources: Eurostat SDMX API, manifest.jsonl, manifest_stage2.jsonl; BTOS 403 excluded.');
  const rows = [
    ['Stage 1', 'SME 规模层机制样本', '10 个 Eurostat 文件；544 个建模观测', 'SHA256 全部通过'],
    ['Stage 2', 'GE10 行业/区域外部验证', '17 个压缩 SDMX-CSV；12.77M 行画像', 'SHA256 全部通过'],
    ['Excluded', 'Census BTOS 获取尝试', 'HTTP 403；仅保留日志', '不进入训练']
  ];
  txt(slide, ctx, 'Layer', 92, 188, 120, 24, { size: 12, color: C.gray, bold: true, face: C.sans });
  txt(slide, ctx, 'Research role', 270, 188, 210, 24, { size: 12, color: C.gray, bold: true, face: C.sans });
  txt(slide, ctx, 'Files / rows', 560, 188, 300, 24, { size: 12, color: C.gray, bold: true, face: C.sans });
  txt(slide, ctx, 'Integrity', 936, 188, 220, 24, { size: 12, color: C.gray, bold: true, face: C.sans });
  rule(slide, ctx, 88, 222, 1080, C.line, 1);
  rows.forEach((r, i) => {
    const y = 250 + i * 92;
    txt(slide, ctx, r[0], 92, y, 130, 32, { size: 20, color: C.blue, bold: true, face: C.sans });
    txt(slide, ctx, r[1], 270, y, 220, 42, { size: 15, color: C.ink });
    txt(slide, ctx, r[2], 560, y, 314, 42, { size: 15, color: C.ink });
    txt(slide, ctx, r[3], 936, y, 230, 42, { size: 15, color: C.ink });
    rule(slide, ctx, 88, y + 58, 1080, C.line, 1);
  });
  interp(slide, ctx, 126, 548, 1000, [
    '所有成功进入模型的原始文件均可从 Eurostat 官方接口追溯。',
    '失败或不可访问的数据被记录但排除，避免把网页错误当作训练数据。',
    '这支撑课程案例的科研严谨性：数据、代码、结果三者可复核。'
  ]);
  return slide;
}
