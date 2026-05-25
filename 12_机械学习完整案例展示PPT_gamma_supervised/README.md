# Gamma 逐页监督生成工作区

本目录用于把 GPT image 2 / 数据驱动图交给 Gamma 做版式生成。流程是一页一页生成：

1. Codex 提供已通过检查的图片 URL 和证据约束。
2. Gamma 只负责单页 PPT 排版。
3. 每页导出 PPTX 和 PNG 预览。
4. Codex 检查页面是否通过，确认后再生成下一页。

`payloads/` 保存每页发送给 Gamma 的脱敏请求体，不包含 API key。
`single_page_pptx/` 保存每页 Gamma 生成结果。
`preview_png/` 保存每页预览图。
`qa/` 保存每页质量门禁。

运行时必须临时设置 `GAMMA_API_KEY` 环境变量；不要把密钥写入仓库、脚本、JSON 或 Markdown。
