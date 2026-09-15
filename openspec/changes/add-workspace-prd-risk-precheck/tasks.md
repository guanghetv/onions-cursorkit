# Tasks: add-workspace-prd-risk-precheck

> 执行约束
> - 每个任务必须有验证点。
> - 可自动化时遵守 TDD；无法自动化时记录人工步骤。
> - 不接工作台 DB / 双周调度 / 法务发送接口。
> - 预检正文口径以飞书使用说明与 vendored `SKILL.md` 为准。

## 1. 整包迁入

- [x] 1.1 将 `/Users/lige/Downloads/product-requirement-risk-gate/` 复制到 `plugins/workspace-specflow/skills/product-requirement-risk-gate/`，保留相对路径与全部文件
      验证点: `SKILL.md`、`references/rules.json`、`references/input-output.md`、`references/biweekly.md`、`references/acceptance.md`、`references/source-framework.xml`、`agents/openai.yaml`、`产品接入说明.md`、`交付核验结果.md` 均存在且规则 JSON SHA256 与交付核验说明一致

## 2. 工作区适配与命令

- [x] 2.1 新增 `prd-risk` skill + `commands/prd-risk.md`：定位需求、抽取 `prd.md` 业务事实、Read 预检包、写 `prototypes/prd-risk-precheck.md`
      验证点: skill 明确禁止向研发索取技术补件；报告三类结论措辞与使用说明一致
- [x] 2.2 更新 `pm-spec-5` Step 6：快照前调用同一预检；HIT/待补则停止确认
      验证点: SKILL.md / command / rubric 均写明硬门禁顺序
- [x] 2.3 更新 README、`workspace-awareness.mdc`、`req-status`（如展示预检报告路径）
      验证点: `/prd-risk` 出现在产品命令表；流程说明含 5 稿确认前预检

## 3. Codex 同步

- [x] 3.1 按现有 `pack.py` 把新 skill 纳入源同步（必要时 `sync` 更新 `source-lock.json`）
      验证点: `python3 codex-plugins/workspace-specflow/scripts/pack.py check` 通过

## 4. 验收

- [x] 4.1 用使用说明中的 10 天会员模拟需求跑 `/prd-risk` 口径（可对 fixtures/`prd.md` 做静态走查或最小夹具）
      验证点: 报告需调整且提及 R-免费活动-04；不宣称已移交法务
- [x] 4.2 走查 `/pm-spec-5` 确认顺序：预检失败不得写 v5 confirmed
      验证点: 对照 skill 文本与 OpenSpec Scenario
- [x] 4.3 写 `e2e-report.md`（等价验收；无真实业务工作台不记生产门禁通过）
      验证点: 列出已验证与未验证项
