# onion-branch-gate

onion-sdd 开发前分支门禁：在修改业务代码前检测受保护分支与跨 change 分支复用两类风险场景，命中后拦截并路由到分支创建/复用流程。

## ADDED Requirements

### Requirement: 受保护分支拦截

系统 MUST 在修改业务代码前检测当前 git 分支，如果命中受保护分支列表（精确匹配 `master`/`main`/`develop`，前缀匹配 `release/*`，或 `git branch --show-current` 为空即 detached HEAD），必须停止修改业务代码并向用户说明，不得静默继续。

#### Scenario: 在 master 上直接开发被拦截

- **WHEN** 当前分支是 `master`，且即将进入 implement 阶段修改业务代码
- **THEN** 系统停止修改业务代码，说明当前处于受保护分支
- **AND** 提供飞书链接驱动创建分支、`feat/<change-id>` 兜底命名、或用户自行创建分支三种路径供选择

#### Scenario: OpenSpec 草稿阶段不受影响

- **WHEN** 当前分支是 `master`，但只是在编写 `proposal.md`/`tasks.md` 草稿，尚未修改业务代码
- **THEN** 系统不触发分支门禁，允许继续编写草稿

#### Scenario: 用户明确要求继续当前分支

- **WHEN** 分支门禁命中受保护分支，用户明确表示"就在当前分支继续改"
- **THEN** 系统尊重用户选择，记录例外，本次 change 生命周期内不再重复拦截同一分支

### Requirement: 跨 change 分支复用检测

系统 MUST 在修改业务代码前判定当前分支是否绑定着另一个活跃 change：优先使用 Trellis active task 的 `branch` 字段与 `meta.onion.change_id`；无 Trellis 或未绑定时，解析当前分支名是否匹配 `feat/<change-id>` 格式且对应 `openspec/changes/` 下真实存在的未归档目录。判定出的 change-id 与本次要处理的 change 不同时，必须触发与受保护分支相同的拦截+路由动作；两层判定均无法确定归属时不得触发。

#### Scenario: Trellis 绑定的跨 change 分支复用被拦截

- **WHEN** 存在 Trellis active task，其 `branch` 字段等于当前分支，`meta.onion.change_id` 为 `change-A`
- **AND** 本次要处理的是新建的 `change-B`
- **THEN** 系统停止修改业务代码，说明当前分支已绑定 `change-A`，继续会把两次不相关改动混进同一分支的 commit 历史
- **AND** 提供飞书链接驱动创建分支、`feat/<change-id>` 兜底命名、或用户自行创建分支三种路径供选择

#### Scenario: 无 Trellis 时按分支名兜底判定

- **WHEN** 没有 Trellis active task 绑定当前分支，当前分支名为 `feat/change-A`，且 `openspec/changes/change-A/` 目录真实存在且未归档
- **AND** 本次要处理的是新建的 `change-B`
- **THEN** 系统按分支名解析出绑定的 change-id 为 `change-A`，触发与 Trellis 绑定场景相同的拦截+路由动作

#### Scenario: 无法判定归属时不拦截

- **WHEN** 没有 Trellis active task 绑定当前分支，且当前分支名不匹配 `feat/<change-id>` 格式，或解析出的 change-id 在 `openspec/changes/` 下找不到对应未归档目录
- **THEN** 系统视为无法判定，不触发跨 change 分支复用检测，继续正常流程

### Requirement: `/onsf-auto` 无交互特化

`/onsf-auto` 无交互自动模式下，系统 MUST 在命中任一触发条件（受保护分支或跨 change 分支复用）时自动按 `feat/<change-id>` 模板生成分支名并切换，不停止、不拦截、无需用户确认；跨 change 分支复用命中时，MUST 在最终输出的风险/blocker 清单中单独点名，不得与受保护分支场景的常规提示合并为一句话。

#### Scenario: auto 模式检测到受保护分支自动切换

- **WHEN** `/onsf-auto` 运行时检测到当前分支是 `master`
- **THEN** 系统自动生成 `feat/<change-id>` 分支并 `git checkout -b` 切换，不停止
- **AND** 在最终输出中说明已自动创建并切换的分支名

#### Scenario: auto 模式检测到跨 change 分支复用需单独点名

- **WHEN** `/onsf-auto` 运行时检测到当前分支绑定着另一个活跃 change `change-A`
- **THEN** 系统自动生成 `feat/<change-id-B>` 分支并切换，不停止
- **AND** 在最终输出的风险/blocker 清单中单独点名"检测到当前分支绑定另一个 change `change-A`，已自动切换到 `feat/<change-id-B>`"，不与常规的"已自动创建分支"提示合并
