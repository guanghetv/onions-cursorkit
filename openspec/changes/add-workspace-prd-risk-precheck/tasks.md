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

## 4. 验收（初版，已按当时口径完成）

- [x] 4.1 用使用说明中的 10 天会员模拟需求跑 `/prd-risk` 口径（可对 fixtures/`prd.md` 做静态走查或最小夹具）
      验证点: 报告需调整且提及 R-免费活动-04；不宣称已移交法务
- [x] 4.2 走查 `/pm-spec-5` 确认顺序：预检失败不得写 v5 confirmed
      验证点: 对照 skill 文本与 OpenSpec Scenario（初版为 HIT/待补双硬阻断；已被第 5 节修订）
- [x] 4.3 写 `e2e-report.md`（等价验收；无真实业务工作台不记生产门禁通过）
      验证点: 列出已验证与未验证项

## 5. 产品修订（2026-09-16）

- [x] 5.1 将自动预检从 Step 6 前移到 Step 4 后 / Step 5 前
      验证点: `pm-spec-5` skill/command 写明 Step 4.5；Step 6 不再作为首次触发点
- [x] 5.2 报告：待补必写；复检覆盖更新同一 `prd-risk-precheck.md` 并追加时间+结论历史；通过不写命中明细
      验证点: `prd-risk` 模板含运行历史表；待补/需调整完整口径；通过仅结论+历史
- [x] 5.3 Step 6 方案 C：需调整硬阻断；待补软提醒可确认；通过可确认
      验证点: skill 返回表与 OpenSpec Scenario 一致
- [x] 5.4 AI Review 只展示预检结论 + 报告路径，不内嵌规则明细
      验证点: `ai-review-rubric-v5.md` / Step 5 模板
- [x] 5.5 需调整/待补时 Agent 显著告警；通过仅轻提示
      验证点: `prd-risk` 与 `pm-spec-5` 提示分级写明
- [x] 5.6 更新 e2e-report 与插件文档（README、workspace-awareness、req-status）
      验证点: 文档与修订后触发/门禁一致；版本 `0.3.4`

## 6. Review 修复（2026-09-16）

- [x] 6.1 无报告 / 结论不可读 / `prd.md` 已改 → 确认前必须先 `prd-risk`
      验证点: `pm-spec-5` 与 `pm-spec` Step 6 写明 MISSING 不得当通过
- [x] 6.2 `/pm-spec` Step 4.5 自动预检 + 方案 C 拦 9稿 confirmed
      验证点: skill / command / 9稿 rubric
- [x] 6.3 预检报告正文对齐预检包产品正文；门禁与非预检字段不进报告；历史保留；metadata 索引
      验证点: `prd-risk` 模板与禁止清单；`req-new` metadata 模板含 `risk_precheck`
- [x] 6.4 升版本并 pack check / 同步 local
      验证点: `0.3.5`

## 7. 文档对称修复（2026-09-16）

- [x] 7.1 `workspace-awareness` 9稿顺序：瘦身写 `v9_pending` → 再 `/prd-risk`
- [x] 7.2 `/pm-spec-5` Step 4.5 显式回写 `prd.risk_precheck`（与 9稿对称）
- [x] 7.3 `/pm-spec` Step 6 缺失条件与 5稿同款三条列举
- [x] 7.4 版本 `0.3.6` + pack / local 同步
