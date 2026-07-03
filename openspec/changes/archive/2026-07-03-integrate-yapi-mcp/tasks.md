# Tasks: integrate-yapi-mcp

> **执行约束**
> - 本变更为 **fe-specflow 插件文档/技能**，无业务页面代码；每个 task 以「对照 `specs/yapi-mcp-integration/spec.md` Scenario 自检」为验证，不要求前端 L1/L2 单测
> - 完成一组相关 task 后 commit（**须用户确认**）；确认后 `git add .` → 提交前审查（aicr-local `/cr` 或 Agent 自审暂存区）→ commit
>
> **验证分层**
> - **V1 结构**：文件存在、章节/触发语/命名约定与 proposal 一致
> - **V2 场景**：逐条对照 spec.md 的 WHEN/THEN 做文档走查（可用真实 YApi 链接做一次 MCP 冒烟，非必须写入本仓库）
> - **V3 编排**：在 Cursor 中触发 `/fe-sdd` 或「YApi 接口到了」话术，确认 Agent 读到的技能描述无矛盾

## 1. 新建 pull-yapi 技能

- [x] 1.1 创建 `plugins/fe-specflow/skills/pull-yapi/SKILL.md` 骨架（frontmatter `name`/`description`、两种使用时机表）
      测试要点: 文件存在；description 含「YApi」「interfaceID」「backend-yapi」；明确与 pull-spec 分工（YApi 结构化契约 vs GitLab 叙事 spec）

- [x] 1.2 编写 MCP 调用流程：`get_interface_detail`（`interfaceURL` / `interfaceID`）、环境变量 `YAPI_BASE_URL` / `YAPI_GLOBAL_TOKEN`、失败提示与粘贴降级
      测试要点: 覆盖 spec「YApi MCP 不可用时的降级」；未配置时 MUST NOT 静默跳过

- [x] 1.3 编写 `search_interface` 受限流程：仅用户显式要求搜索 → 展示候选 → 确认 `interfaceID` 后再 `get_interface_detail`
      测试要点: 覆盖 spec「用户要求搜索接口」；禁止未经确认落盘

- [x] 1.4 编写变更目录定位（复用 pull-spec：`find proposal.md`、多目录让用户选、无目录拒绝）
      测试要点: 覆盖 spec「无变更目录时拒绝写入」

- [x] 1.5 定义落盘：`backend-yapi-<slug>.md` 头部 metadata 模板 + 正文 Markdown 结构（Method/Path/Query/Body/Response/错误码）
      测试要点: 符合决策 **1a**；metadata 含 `source`、`interface_id`、`interface_url`、`pulled_at`、外部副本 WARNING

- [x] 1.6 编写差异分析步骤（读 `proposal.md` API 契约段，输出一致/差异/增量；字段纠偏以 YApi 为准）
      测试要点: 覆盖 spec「联调前发现契约差异」；对齐决策 **3a**

## 2. 更新 dev-workflow 主编排

- [x] 2.1 步骤 1b「来源一览」增加 **YApi 接口** 行（feishu/GitLab 同级；只读、可组合）
      测试要点: 阶段 1 不写入 `openspec/changes/**`；仅用户给链接/ID 时拉取（**2a**）

- [x] 2.2 步骤 1b 增加 YApi 失败处理小节（MCP 未启用、鉴权、接口不存在 → 明确提示）
      测试要点: 与 pull-yapi / feishu 失败处理语气一致

- [x] 2.3 步骤 1d brainstorming 约束：有 YApi 时 API 契约以 MCP 详情为主依据；无 YApi 可标注 `inferred`
      测试要点: 禁止 brainstorming 结束前默认 `search_interface`

- [x] 2.4 事件 A 增加 YApi 分支：`REQUIRED SUB-SKILL: pull-yapi`、触发语（「YApi 接口到了」「从 YApi 拉 interface」等）、与 pull-spec 并列说明
      测试要点: T1 后写入 `backend-yapi-*.md` 并 diff；不替换 GitLab pull-spec 路径

- [x] 2.5 阶段 4 e2e-verify 引用段补充：存在 `backend-yapi-*` 时字段对照以 YApi 为准，与 qa 冲突须标注
      测试要点: 决策 **3a** 在主编排中可见

- [x] 2.6 更新 `dev-workflow` skill `description` 与文首能力列表，提及 YApi MCP
      测试要点: Agent 通过 skill 元数据可发现 YApi 能力

## 3. 门禁、命令与 README

- [x] 3.1 更新 `plugins/fe-specflow/commands/fe-sdd.md`：阶段 1 多源采集含 YApi MCP（只读、用户给链接/ID）
      测试要点: 覆盖 spec「fe-sdd 阶段 1 声明 YApi 来源」；门禁禁止项不变

- [x] 3.2 更新 `plugins/fe-specflow/rules/dev-workflow.mdc` 流程摘要（设计探索多源 + 事件 A pull-yapi）
      测试要点: 与 dev-workflow SKILL 无矛盾；Rule 顶部门禁块不被破坏

- [x] 3.3 更新 `plugins/fe-specflow/README.md`：核心能力表、流程图、前置条件（`user-yapi-common-mcp`、`YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`）
      测试要点: 安装检查项可执行（`echo ${YAPI_BASE_URL:+ok}` 等）；插件结构树含 `pull-yapi/`

## 4. 关联技能交叉引用

- [x] 4.1 更新 `plugins/fe-specflow/skills/design-to-opsx/SKILL.md`：`References` 模板增加「YApi 接口: <链接列表>」
      测试要点: 阶段 1 只读拉取的链接可记入 proposal

- [x] 4.2 更新 `plugins/fe-specflow/skills/pull-spec/SKILL.md`：说明结构化接口契约走 `pull-yapi`，GitLab 叙事 spec 仍走 pull-spec
      测试要点: 两技能职责清晰，无重复三级策略描述

- [x] 4.3 更新 `plugins/fe-specflow/skills/e2e-verify/SKILL.md`：静态对照优先级中补充 `backend-yapi-*` 字段权威与 qa 冲突标注
      测试要点: 覆盖 spec「YApi 与 qa spec 字段冲突」

## 5. 整体验收

- [x] 5.1 对照 `openspec/changes/integrate-yapi-mcp/specs/yapi-mcp-integration/spec.md` 全量 Scenario 走查，在 PR/对话中列出 PASS/FAIL 清单
      测试要点: 所有 ADDED Requirements 至少有一条 Scenario 被文档满足

- [ ] 5.2 可选冒烟：在已启用 YApi MCP 的环境用一条真实 `interfaceURL` 走读阶段 1 只读（不写 change 目录），再在测试用 change 目录走 `pull-yapi` 落盘一条 `backend-yapi-*.md`
      测试要点: 落盘文件名、metadata、diff 输出符合 1.5/1.6；失败则记录环境原因，不阻塞文档合入

- [x] 5.3 将本 `tasks.md` 全部勾选后，提示用户是否 commit；归档前由用户执行 `openspec archive integrate-yapi-mcp`（或团队约定命令）
      测试要点: 变更目录含 proposal、spec、tasks 三件套完整

## 6. re-check 实现层对齐（本迭代）

- [x] 6.1 创建 `plugins/fe-specflow/skills/re-check/SKILL.md`（触发、scope、破坏性确认、批量 N=5、扫描优先级、REQUIRED pull-yapi）
      测试要点: 覆盖 spec「re-check 技能」「破坏性变更」「scope 皆空」「无标记仍可对齐」

- [x] 6.2 收窄 `pull-yapi`：文档层、不改业务代码；触发语区分「只落盘」与 re-check 默认路径
      测试要点: 覆盖 spec「pull-yapi 为文档层」

- [x] 6.3 更新 `dev-workflow` 事件 A：默认 re-check；无感路由；步骤 2 意图表；T1 推荐 mock 标记
      测试要点: 覆盖 spec「事件 A 默认」「无感触发」「编排文档同步」

- [x] 6.4 更新 `dev-workflow.mdc`、`README.md`、`plugin.json` v0.0.3：双技能对照表；Commands 仅 fe-sdd
      测试要点: 用户可区分 pull-yapi vs re-check；无 fe-re-check command

- [x] 6.5 更新本变更 `proposal.md` 与 `specs/yapi-mcp-integration/spec.md` 增补 re-check Requirements
      测试要点: 6.x 与 spec 新增 Scenario 一一对应

- [ ] 6.6 可选冒烟：在测试 change 目录触发「re-check」话术，确认 Agent 先 pull-yapi 落盘再列出对齐表（可不真改代码）
      测试要点: 链路无矛盾；scope/确认门禁在技能中可读
