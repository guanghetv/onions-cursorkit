---
name: qa-execute
description: 将 test/ 下的测试用例 Markdown 上传至 Case Flow 快速模式（ai-case-flow.yc345.tv/quick）；支持 test-spec 格式自动转换与 Case Flow 嵌套列表直传。
---

# /qa-execute

将当前需求的测试用例 Markdown 上传到 [Case Flow 快速模式](https://ai-case-flow.yc345.tv/quick)。自动识别格式（`/qa-spec` 的 `test-spec.md` 会转换为嵌套列表；已是 Case Flow 嵌套列表则直传）、调用 API 导入，并打开浏览器输出 Session 接力 ID。
