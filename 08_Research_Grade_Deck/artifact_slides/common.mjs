
export const C = {
  W: 1280,
  H: 720,
  blue: '#0B1F3A',
  ink: '#111827',
  gray: '#6B7280',
  soft: '#9CA3AF',
  line: '#E5E7EB',
  light: '#F6F7F9',
  white: '#FFFFFF',
  pale: '#EEF3F8',
  font: 'Microsoft YaHei',
  sans: 'Aptos',
  mono: 'Cascadia Mono'
};

export function rect(slide, ctx, x, y, w, h, fill = C.white, line = 'rgba(0,0,0,0)', name = undefined) {
  return ctx.addShape(slide, { left: x, top: y, width: w, height: h, fill, line: ctx.line(line, line === 'rgba(0,0,0,0)' ? 0 : 1), name });
}

export function txt(slide, ctx, text, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: String(text ?? ''),
    left: x,
    top: y,
    width: w,
    height: h,
    fontSize: opts.size ?? 18,
    color: opts.color ?? C.ink,
    bold: Boolean(opts.bold),
    typeface: opts.face ?? C.font,
    align: opts.align ?? 'left',
    valign: opts.valign ?? 'top',
    fill: opts.fill ?? 'rgba(0,0,0,0)',
    line: opts.line ?? ctx.line(),
    insets: opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 },
    name: opts.name
  });
}

export function rule(slide, ctx, x, y, w, color = C.line, h = 1) {
  rect(slide, ctx, x, y, w, h, color, 'rgba(0,0,0,0)');
}

export function base(slide, ctx, no, kicker, claim, source = 'Eurostat official SDMX-CSV; reproducible Python pipeline; A10 GPU baseline.') {
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  txt(slide, ctx, String(kicker).toUpperCase(), 64, 36, 360, 24, { size: 10, color: C.blue, bold: true, face: C.sans });
  rule(slide, ctx, 64, 66, 64, C.blue, 3);
  txt(slide, ctx, claim, 64, 84, 1040, 74, { size: 28, color: C.ink, bold: true, face: C.font });
  rule(slide, ctx, 64, 670, 1152, C.line, 1);
  txt(slide, ctx, source, 64, 682, 900, 22, { size: 9, color: C.gray, face: C.sans });
  txt(slide, ctx, String(no).padStart(2, '0'), 1170, 680, 48, 24, { size: 13, color: C.gray, face: C.mono, align: 'right' });
}

export async function img(slide, ctx, path, x, y, w, h, fit = 'contain', name = undefined) {
  return await ctx.addImage(slide, { path, left: x, top: y, width: w, height: h, fit, alt: name ?? 'visual asset', name });
}

export function metric(slide, ctx, value, label, x, y, w = 170) {
  txt(slide, ctx, value, x, y, w, 46, { size: 29, color: C.blue, bold: true, face: C.mono });
  txt(slide, ctx, label, x, y + 48, w + 12, 38, { size: 11, color: C.gray, face: C.font });
}

export function interp(slide, ctx, x, y, w, rows) {
  const labels = ['What the chart shows', 'Why it matters', 'Decision it supports'];
  if (w >= 700) {
    const gap = 30;
    const col = (w - gap * 2) / 3;
    rows.forEach((body, i) => {
      const xx = x + i * (col + gap);
      txt(slide, ctx, labels[i], xx, y, col, 20, { size: 9.5, color: C.blue, bold: true, face: C.sans });
      txt(slide, ctx, body, xx, y + 28, col, 54, { size: 12.2, color: C.ink, face: C.font });
      if (i < 2) rect(slide, ctx, xx + col + gap / 2, y + 4, 1, 72, C.line);
    });
    return;
  }
  rows.forEach((body, i) => {
    const yy = y + i * 72;
    txt(slide, ctx, labels[i], x, yy, w, 18, { size: 9.2, color: C.blue, bold: true, face: C.sans });
    txt(slide, ctx, body, x, yy + 24, w, 40, { size: 11.5, color: C.ink, face: C.font });
    if (i < 2) rule(slide, ctx, x, yy + 64, w, C.line, 1);
  });
}

export function bullets(slide, ctx, items, x, y, w, rowH = 62) {
  items.slice(0, 3).forEach((item, i) => {
    const yy = y + i * rowH;
    rect(slide, ctx, x, yy + 7, 6, 28, C.blue);
    txt(slide, ctx, item, x + 20, yy, w - 20, rowH - 8, { size: 14, color: C.ink, face: C.font });
  });
}
