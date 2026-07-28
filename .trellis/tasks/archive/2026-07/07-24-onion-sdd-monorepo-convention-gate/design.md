# Design

## 方案概览

两个独立交付物，同一任务、同一发版（0.1.2）：

| 交付物 | 改动文件 | 性质 |
|--------|----------|------|
| D1: repo-root 自动解析 | `scripts/onion_state.py`、`rules/onion-sdd.mdc`（小注） | 运行态行为，向后兼容 |
| D2: 规范类交付物门禁 | `scripts/finish_check.py`、`skills/openspec-change/SKILL.md` | 规划期硬规则 + 归档期 WARN |
| 发版 | `CHANGELOG.md`、`.cursor-plugin/plugin.json` | 版本号 |

## D1: repo-root 自动解析

### 解析算法（resolve_repo_root）

新增 `resolve_repo_root(start: Path) -> Path`：

1. 从 `start`（默认 `Path.cwd()`）向上逐级查找。
2. 命中第一个含 `.trellis/` 子目录的祖先（含 `start` 自身）→ 返回该目录。
3. 一直找到文件系统根仍未命中 → 返回 `start`（回退 cwd，保持独立模式）。

语义：「先看有没有安装（`.trellis/` 是否存在），再向上找；找不到回退 cwd」——与用户决策一致。

### --repo-root 默认行为调整

当前：
```python
parser.add_argument("--repo-root", default=os.environ.get("ONION_SDD_ROOT") or ".", ...)
...
repo_root = Path(args.repo_root).resolve()
```

改为：
```python
parser.add_argument("--repo-root", default=None, ...)
...
if args.repo_root is None:
    args.repo_root = os.environ.get("ONION_SDD_ROOT") or str(resolve_repo_root(Path.cwd()))
repo_root = Path(args.repo_root).resolve()
```

优先级不变：显式 `--repo-root` > `ONION_SDD_ROOT` > 自动解析。仅「两者都未提供」时从 `.` 改为自动向上解析。

### 向后兼容性分析

| 场景 | 旧行为 | 新行为 | 结论 |
|------|--------|--------|------|
| `.trellis/` 在 cwd | repo-root=cwd | 向上找到 cwd 自身命中 → cwd | 一致 |
| 子包 cwd，外层有 `.trellis/` | repo-root=子包（bug） | 向上找到外层根 | 修复 |
| 无 `.trellis/` | repo-root=cwd | 找不到 → 回退 cwd | 一致 |

唯一行为变化正是 bug 场景，其余不变。现有调用方（显式传 `--repo-root` 或设 `ONION_SDD_ROOT`）完全不受影响。

### 连带修复

`ensure_onion_gitignored`（0.1.1 新增）写 `repo_root / ".gitignore"`。旧逻辑在子包 cwd 会把 ignore 写进子包 `.gitignore`；新逻辑 repo-root=外层根，ignore 落到真正仓库根。无需额外改 ensure_onion_gitignored。

### 边界情况

- 多层 `.trellis/`（嵌套）：向上查找取最近者，正确。
- `.onion-sdd/current.json` 位置：随 repo-root 落到含 `.trellis/` 的外层根，与 `openspec/`、`.trellis/` 同根，符合 monorepo 单 change 跟踪模型。
- `resolve_trellis_active_task` 已用 `.trellis/scripts/task.py` 存在性判可用性，与新 repo-root 一致（都在外层根）。

### rules/onion-sdd.mdc 小注

在「运行态」段补一句：repo-root 默认自动向上解析到含 `.trellis/` 的目录，找不到回退 cwd；手动调用优先让脚本自动解析，避免硬编码 `--repo-root .`。

## D2: 规范类交付物门禁

### 规划期硬规则（openspec-change/SKILL.md）

新增小节「规范/约定的归属」：

- tasks.md 只装产品/验收交付物（对应 README 分工表）。
- 编码约定/规范是 Phase 3.3 spec 积累动作，目标 `.trellis/spec/<package>/<layer>/`（无 Trellis 时才退回项目 `docs/`），不进 tasks.md、不落 `docs/`。
- tasks.md 出现「落规范/落约定到 docs/」类条目视为规划缺陷，应改为 Phase 3.3 spec update。

### 归档期 WARN（finish_check.py）

新增检查 `check_convention_in_docs`：

- 扫描 change 影响文件中路径匹配 `docs/**` 且文件名（不区分大小写）含 `convention|guideline|standard|规范|约定` 的新增/修改文件。
- 命中则输出 WARN：`检测到 docs/<file> 疑似编码规范，建议迁入 .trellis/spec/<package>/<layer>/（Phase 3.3 spec update）`。
- WARN 不改变 exit code（不阻塞归档）；与其他 hard fail 检查正交。

实现要点：复用 finish_check.py 现有文件枚举方式（change 目录 + git diff），仅追加一条非致命检查。pattern 收窄到 convention 类关键词，避免对 API 文档等合法 `docs/` 文件误报。

### 误报控制

- 仅文件名命中关键词才 WARN，路径只要求在 `docs/**` 下。
- WARN 非 fatal，即便误报也不阻塞。
- 后续视误报率再决定是否升级 HARD FAIL（Out of Scope）。

## 发版 0.1.2

- CHANGELOG：`[Unreleased]` 下新增 `[0.1.2] - <date>`，Added 记 D1/D2，Changed 视情况。
- plugin.json：version `0.1.1` → `0.1.2`。
- marketplace.json：不动（无能力摘要变化）。

## 风险

- repo-root 自动解析改变「未显式传 --repo-root」的默认：已论证仅 bug 场景变化，且显式传参不受影响。
- finish_check WARN 误报：pattern 收窄 + 非 fatal，风险可控。
- 不改 Trellis 源码/脚本，无跨系统副作用。
