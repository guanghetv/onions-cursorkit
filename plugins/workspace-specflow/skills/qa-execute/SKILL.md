---
name: qa-execute
description: >-
  Use when user mentions /qa-execute、Case Flow、快速模式、上传测试用例、ai-case-flow。
  Uploads test/*.md to Case Flow quick mode; converts /qa-spec test-spec.md or passthrough nested list MD.
disable-model-invocation: true
---

# /qa-execute — 上传测试用例到 Case Flow 快速模式

## 前置条件

- 目标文件为 `test/` 目录下的 `.md`（常见：`test-spec.md` 或 Case Flow 嵌套列表用例）
- 网络可访问 `https://ai-case-flow.yc345.tv`
- 系统已安装 `curl`、Python 3.9+

## 定位文件（优先级）

1. 用户当前编辑器打开的 `test/*.md`
2. 从工作目录向上查找 `test/test-spec.md`
3. 当前目录为 `test/` 且仅有一个 `.md` → 用该文件
4. 扫描 `requirements/*/test/test-spec.md`，多个则 **AskQuestion**
5. 失败则提示先 `/qa-spec` 或让用户给出路径

## 执行

定位本 Skill 目录下的脚本（glob `**/qa-execute/scripts/convert_and_upload.py`），执行：

```bash
python3 <脚本绝对路径> \
  --file "<待上传 .md 绝对路径>" \
  --base-url "https://ai-case-flow.yc345.tv"
```

脚本行为：
- **嵌套列表**（首行 `- ` 且含前置条件/操作步骤/预期结果）→ 直传
- **test-spec 格式** → 转换为 6 级嵌套列表后上传

映射细则见 [references/case-flow-mapping.md](references/case-flow-mapping.md)。

## 收尾汇报

解析脚本 stdout 中的 JSON 与「Session 接力 ID」：

| 项 | 说明 |
|----|------|
| 模式 | `passthrough` 或 `converted` |
| 用例数 | `case_count` |
| Session 接力 ID | 用户粘贴到 `/quick` 底部「Session 接力」→「进入」 |
| 快速模式 URL | `https://ai-case-flow.yc345.tv/quick` |

脚本默认 `open` 浏览器；禁用：`CASE_FLOW_OPEN_BROWSER=0`。

## 错误处理

- HTTP 422：打印服务端 `detail`，说明格式或层级问题
- 无 `### 场景:`：提示检查 test-spec 或改用已转换的嵌套列表 MD

## 典型顺序

`/qa-spec` → （可选 `/qa-sync-xmind`）→ **`/qa-execute`**
