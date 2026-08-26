# 信封：代码身份优先，env 随运行时

## 先齐代码身份（GitNexus 用，无 env）

缺项一次问清即可开 GitNexus，**不要**为检索代码先逼问 env：

- 服务名 / 仓库（`gitlab.yc345.tv/...`）/ 前端或后端
- 接口：HTTP path、gRPC operation、或页面入口
- 现象：超时、5xx、空数据、报错原文
- 关联键若已有：`trace_id` / `request_id`（有则后边运行时精确查）

设备只用 `omvd`。`prod` 不是 K8s namespace。

## 钉死 env（仅当要加载运行时）

打开 metrics / trace / logs / archery **之前** 必须：

1. 用户明示 `env`（`prod` / `stage` / `test` 等），且
2. 落在该域 `*_available_servers` / `archery_available_envs` allowlist。

禁止：默认 `prod`；从 namespace/topic/Jaeger 名反推；一域 `denied` 后改另一 env 凑数。

本信封内 **`env` 不可变**。查错环境：作废运行时部分，用新 env 重开；**禁止**把旧运行时观测拷进新包。GitNexus 代码定位可保留（与 env 无关）。

跨环境是另一次运行时排查，不是对照。禁止 metrics `prod` + logs `stage` 同一包。合法：同一 `env` 故障窗 vs 对照窗。

相对时间只在入口接受，立刻转绝对 `start`/`end`，各运行时域复用。

## 交付模板

```markdown
## 代码证据（主）
### GN-01 <事实标题>
- tool: `<实际调用的 GitNexus tool>`
- invocation: `<实际传入参数；query/task_context/goal 不得省略>`
- observed:
  - repo/index: `<仓库 path、indexed date、last commit；返回什么写什么>`
  - symbol/route/file: `<精确返回字段；未返回的字段明确说明>`
  - source excerpt: `<仅 include_content=true 返回的最小必要源码摘录；敏感字面量替换为 ***REDACTED***>`
- supports: `<本卡直接支持的单一事实>`
- limits: `<静态索引、stale、低 confidence、歧义或字段缺失>`

<按 GN-02、GN-03 继续；不得用一张卡概括全部调用>

## 逻辑对齐
1. [GN-xx] `<入口>` --`<relation>`--> `<下一符号>`（双方文件）
2. [GN-yy] `<符号>` --`<relation>`--> `<下一符号>`（双方文件）

- 关键源码事实：<函数签名/分支/参数映射/外部调用/错误转换> [GN-xx]
- 候选边与缺口：<尚未被 context/route_map 核实的边>
- 静态推断：<条件性解释，并引用 GN-*>。禁止「根因是」。

## 代码侧评估
- 置信度: `high` | `medium` | `low`（取最低档的原因：…）
- 初步结论: 代码结构显示 … [GN-xx]。若请求走到该路径，与症状相符的点是 …。
- 未证实: 该 env 现网是否发生、流量/错误量、某条请求的实际耗时或返回。
- 收束: `stop` | `need_runtime` | `need_more_code`

## 运行时（未加载则写「未取运行时」）
- env: <仅已钉死>
- 时间窗: <绝对 start/end>
- 层次表: 层 / tool / status / 进/出 / 缺口

## 单一假设与下一步
假设与初步结论一致（一句，引用 GN-*）。下一步：<GitNexus 或一个运行时 tool 或问用户一项>

## 能力缺口
<GitNexus 未索引 / 某运行时域该 env 不可查>
```
