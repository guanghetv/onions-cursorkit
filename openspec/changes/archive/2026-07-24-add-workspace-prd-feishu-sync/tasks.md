# Tasks: add-workspace-prd-feishu-sync

> 执行约束
> - 每个任务必须有验证点
> - 同步与校验技能必须可独立调用；publish 仅编排
> - 依赖 `lark-cli` 的路径须有失败断言（不得伪造 pass）

## 1. Metadata 与模板

- [x] 1.1 扩展 `req-new/references/templates.md` 中 `metadata.yaml`：`feishu.*` 与 `consistency.*` 字段
- [x] 1.2 更新 9 稿 `prd-template.md`：标明 9 稿确认后按语义无背景/价值；契约章节与原型锚点必留
- [x] 1.3 固化 chapter-map（unit key + 标题关键词优先，序号仅兼容；sync/check 共用）

## 2. `/prd-feishu-sync` 独立技能

- [x] 2.0 将同步/排版/增量规程内化进 `prd-feishu-sync/SKILL.md`（自包含，无外挂技能引用）
- [x] 2.1 新增 `skills/prd-feishu-sync/SKILL.md` + `commands/prd-feishu-sync.md`
- [x] 2.2 实现 `create` 规程（req-new 强制调用）— **真机 create 待试点**
- [x] 2.3 实现 `push` 规程（增量/manifest 写在 SKILL）— **真机增量待试点**
- [x] 2.4 实现 5/9 门控与 `--force`
- [x] 2.5 实现 `pull`/`reconcile`/`status`/`rebind` 规程
- [x] 2.6 9 稿瘦身（语义删讲解层）与不重排序号写入模板与 chapter-map

## 3. `/prd-consistency-check` 技能

- [x] 3.1 新增 `skills/prd-consistency-check/SKILL.md` + command
- [x] 3.2 实现 critical/warning 规则（写在 SKILL）
- [x] 3.3 报告字段 + metadata.consistency 更新规程
- [x] 3.4 飞书底部机器 callout 回写规程
- [x] 3.5 与 sync 协作：超前/未推送漂移定级


## 4. `/prd-publish` 编排

- [x] 4.1 新增 `skills/prd-publish/SKILL.md` + command：sync → check

## 5. 生命周期挂接

- [x] 5.1 `/req-new` 末尾必调 `sync create`
- [x] 5.2 `/pm-spec-5` 按 `v9_synced` 门控调用 push v5
- [x] 5.3 `/pm-spec`：瘦身 → push v9 → check → 再 confirmed
- [x] 5.4 `/qa-spec` 启动前读 consistency（fail 阻断）
- [x] 5.5 提交前 T4 规程（pm-spec Step 7 / prd-publish）
- [x] 5.6 移除 `/dev-start`

## 6. 文档与规则

- [x] 6.1 更新 `rules/workspace-awareness.mdc`
- [x] 6.2 更新 `plugins/workspace-specflow/README.md`

## 7. 试点验收

- [ ] 7.1 用真实需求跑通：create → v5 push → v9 publish → 改飞书契约 reconcile → 再 check
      验证点: 对齐全提案验收条；飞书项目 #7016921222 可关联说明
