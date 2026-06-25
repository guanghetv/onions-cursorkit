# 实施计划

## 清单

- [x] 创建 `plugins/onion-sdd/` 目录结构。
- [x] 添加 `.cursor-plugin/plugin.json`（`name: onion-sdd`，声明 commands、skills、rules）。
- [x] 添加中文 README：Phase 0 目标、onion 独立流程定位、Tier 路由、剔除的重约束、后续演进。
- [x] README 写明试点隔离：不注册 marketplace，手动指定 `plugins/onion-sdd/` 路径试用。
- [x] 添加 `DESIGN-SUPPLEMENT.md`，记录 Phase 0 补充设计与后续预留。
- [x] 添加命令（均需 YAML frontmatter：`name`、`description`）：
  - [x] `onion-hotfix.md` → `tier-triage` + `mini-change`
  - [x] `onion-tweak.md` → `tier-triage` + `light-change`
  - [x] `onion-plan.md` → triage + Tier 路由；Tier 2+ 进入 onion 自有完整 SDD 路径
  - [x] `onion-continue.md` → OpenSpec 产物弱恢复
  - [x] `onion-finish.md` → 验收证据 + 归档提示（非 Trellis journal）
- [x] 添加技能（frontmatter：`name`、`description`）：
  - [x] `tier-triage/SKILL.md`
  - [x] `mini-change/SKILL.md`
  - [x] `light-change/SKILL.md`
- [x] 添加 `rules/onion-sdd.mdc`：slash command 配套说明、Tier 分级 OpenSpec 门禁、Phase 0 不做范围；glob 以 `openspec/**` 为主，不承诺自然语言弱触发。
- [x] 添加 `templates/current.example.json`，作为 `.onion-sdd/current.json` 轻量状态模板。
- [x] 落地 Phase 0 补充项 S1-S6：Tier 决策树、Tier 0++、轻量状态、质量门禁、冲突检测、带债归档。
- [x] 全文中文；**禁止**出现「必须全量扫描」「扫描当前仓库」等硬约束。
- [x] 运行验证；偏离记录在任务 notes。

## 编写参照

- 实施过程可阅读既有流程材料和插件规范，但这些参考来源不写入 `onion-sdd` 产物。
- `onion-sdd` 的 README、commands、skills、rules 只记录 onion 自有流程。
- `docs/add-a-plugin.md` 用于 frontmatter 与目录规范自检。

## 验证命令

```bash
# 1. 文件清单
find plugins/onion-sdd -type f | sort

# 2. plugin.json
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json

# 3. command → skill 路由（每个 command 至少命中一行）
for f in plugins/onion-sdd/commands/*.md; do
  echo "=== $f ==="
  rg -n "tier-triage|mini-change|light-change|onion 完整 SDD|完整 SDD 路径|验收规则" "$f" || echo "MISSING onion route reference"
done

# 4. 纪律关键词
rg -n "按需|Phase 0|Tier 0\\+|/onion-|独立|完整 SDD 路径|Trellis|后续" plugins/onion-sdd
rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd && echo "FAIL: heavy scan constraint found" || echo "OK: no hard full-scan constraint"
rg -n "fe-specflow|fe-sdd|dev-workflow|design-to-opsx|pull-spec|e2e-verify" plugins/onion-sdd && echo "FAIL: coupled legacy flow found" || echo "OK: no legacy flow references"

# 5. frontmatter 抽检（需 node）
node -e "
const fs=require('fs');const path=require('path');
function fm(p){const c=fs.readFileSync(p,'utf8');if(!c.startsWith('---\\n'))return null;
  const i=c.indexOf('\\n---\\n',4);if(i<0)return null;
  const o={};for(const l of c.slice(4,i).split('\\n')){const j=l.indexOf(':');if(j>0)o[l.slice(0,j).trim()]=l.slice(j+1).trim();}
  return o;}
for(const p of fs.readdirSync('plugins/onion-sdd/commands').filter(f=>f.endsWith('.md')))
  {const f=fm('plugins/onion-sdd/commands/'+p);if(!f?.name||!f?.description)console.error('BAD command frontmatter:',p);}
for(const s of ['tier-triage','mini-change','light-change']){
  const p='plugins/onion-sdd/skills/'+s+'/SKILL.md';const f=fm(p);
  if(!f?.name||!f?.description)console.error('BAD skill frontmatter:',p);}
"

# 6. 隔离
git diff -- plugins ':!plugins/onion-sdd'
git status --short
```

## 回滚点

- 结构错误：删除 `plugins/onion-sdd/` 即可；试点目录外既有插件未动。
- 范围变更：先回写 `prd.md` / `design.md` / 本文件，再重新实施。

## 启动前检查

- [x] 用户确认：设计全新的 onion-sdd 流程；本期不接 Trellis；Tier 2+ 不依赖其他插件；Phase 0 先使用 slash command 触发。
- [x] 用户确认：试点隔离，手动指定 `plugins/onion-sdd/` 路径执行，不先放入插件市场。
- [x] 用户 review 本版规划 artifacts 后，执行：

```bash
python3 ./.trellis/scripts/task.py start .trellis/tasks/06-24-fe-specflow-trellis-phase-0
```
