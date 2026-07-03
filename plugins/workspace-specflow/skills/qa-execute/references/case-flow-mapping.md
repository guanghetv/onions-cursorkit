# test-spec.md ↔ Case Flow 嵌套列表映射

## 双格式识别

| 格式 | 特征 | 处理 |
|------|------|------|
| Case Flow 原生 | 首行以 `- ` 开头；正文含 `前置条件` / `操作步骤` / `预期结果` 嵌套链 | 原样 POST |
| `/qa-spec` 原生 | `# 测试用例：`、`## MODULE`、`### 场景:` | 转换为 6 级嵌套列表后 POST |

## test-spec → Case Flow（6 级）

```
- <用例集标题>                    ← # 测试用例：<标题>，去掉前缀
  - <MODULE-ID>                   ← ## MODULE-1: ... 取 MODULE-1（不含冒号）
    - <场景描述>                  ← ### 场景: <描述>（同 MODULE 多场景并列于此下）
      - 前置条件：<a>；<b>        ← **前置条件**: 下 - 列表，；连接
        - 步骤：<a>；<b>          ← **操作步骤**: 下 1. 列表，去序号后；连接
          - 预期结果：<a>；<b>    ← **预期结果**: 下 - 列表，；连接
```

同 MODULE 下多个场景合并为同一 MODULE 节点，场景为第 3 级并列子项。

仅解析 `### 场景:` 块；Brainstorming、覆盖率表、十大类说明等跳过。

## API

```http
POST {CASE_FLOW_BASE_URL}/api/v1/quick/sessions/import
Content-Type: application/json

{
  "filename": "<basename>",
  "content": "<markdown>",
  "functionFiles": []
}
```

## 环境变量

| 变量 | 默认 |
|------|------|
| `CASE_FLOW_BASE_URL` | `https://ai-case-flow.yc345.tv` |
| `CASE_FLOW_OPEN_BROWSER` | `1` |

上传通过系统 `curl` 发起（兼容内网自签证书）。

## Session 接力

上传成功后需在 `/quick` 底部「Session 接力」粘贴 `session_id` 后点「进入」。
