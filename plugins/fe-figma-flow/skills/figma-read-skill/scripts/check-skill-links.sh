#!/usr/bin/env bash
# check-skill-links.sh
# ----------------------------------------------------------------------------
# 校验 figma-read-skill 内部 markdown 链接的路径铁律：
#
#   1. SKILL.md 与所有 phase / orchestrator-checklist / template 文件互相引用
#      时路径**不带** `references/` 前缀（同级根目录）。
#   2. phase / orchestrator-checklist / SKILL.md 引用 `references/` 下子文档
#      时路径**必须带** `references/` 前缀。
#   3. 所有相对链接的目标文件必须真实存在。
#
# 历史 bug `cf53224` 就是因为把 phase 文件之间互相引用写成了
# `references/phase-2-...md`（多余前缀）导致路径错位。本脚本是为了把这条铁律
# 从"靠 markdown 提醒人"升级为"靠 CI / 本地 hook 自动守护"。
#
# 退出码:
#   0  全部通过
#   1  发现违规链接
#   2  脚本自身错误（找不到目录等）
# ----------------------------------------------------------------------------

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo "❌ 找不到 SKILL.md，期望路径: $SKILL_DIR/SKILL.md" >&2
  exit 2
fi

# 同级根目录中的"流程主线"文件白名单（与 SKILL.md 同级）
ROOT_FILES=(
  "SKILL.md"
  "phase-1-dependency-check.md"
  "phase-2-audit-and-codegen.md"
  "phase-3-verification.md"
  "implementation-audit-template.md"
  "orchestrator-checklist.md"
)

errors=0
checked_links=0

# 提取一份 markdown 文件中所有形如 [text](path.md...) 的相对链接
# 过滤规则：
#   - 跳过反引号包裹的内联代码（如 `[xxx.md](xxx.md)` 是文档示例，不是真链接）
#   - 跳过围栏代码块 ``` ... ``` 内部
#   - 跳过 http(s):// 与锚点 #xxx 开头的链接
extract_links() {
  local file="$1"
  awk '
    /^```/ { in_fence = !in_fence; next }
    !in_fence {
      line = $0
      gsub(/`[^`]*`/, "", line)
      print line
    }
  ' "$file" \
    | grep -oE '\[[^]]+\]\([^)]+\.md[^)]*\)' 2>/dev/null \
    | sed -E 's/^\[[^]]+\]\(([^)]+)\)$/\1/' \
    | grep -Ev '^https?://' \
    | grep -Ev '^#' \
    || true
}

# 校验单个链接
# 参数: $1=源文件相对路径（如 SKILL.md / phase-2-...md / references/xxx.md）
#       $2=链接 raw 字符串
check_link() {
  local src_rel="$1"
  local link_raw="$2"
  # 去掉锚点
  local link="${link_raw%%#*}"

  # 空链接（纯锚点）跳过
  [[ -z "$link" ]] && return 0

  checked_links=$((checked_links + 1))

  # 源文件所在目录（绝对路径）
  local src_dir
  src_dir="$(cd "$SKILL_DIR/$(dirname "$src_rel")" && pwd)"

  # 解析为绝对路径
  local target_abs
  target_abs="$(cd "$src_dir" 2>/dev/null && cd "$(dirname "$link")" 2>/dev/null && pwd)/$(basename "$link")"

  # 1) 文件存在性
  if [[ ! -f "$target_abs" ]]; then
    echo "❌ [$src_rel] 链接目标不存在: $link"
    errors=$((errors + 1))
    return 0
  fi

  # 推算 target 相对 SKILL_DIR 的路径
  local target_rel="${target_abs#$SKILL_DIR/}"

  # 2) 路径铁律：根目录文件之间互相引用，不得带 `references/` 前缀
  local target_basename
  target_basename="$(basename "$link")"
  local target_in_root=0
  for f in "${ROOT_FILES[@]}"; do
    if [[ "$f" == "$target_basename" && "$target_rel" == "$target_basename" ]]; then
      target_in_root=1
      break
    fi
  done

  if [[ $target_in_root -eq 1 ]]; then
    if [[ "$link" == references/* ]]; then
      echo "❌ [$src_rel] 根目录文件被错误地带上 references/ 前缀: $link （应写为 $target_basename）"
      errors=$((errors + 1))
    fi
  fi

  # 3) 路径铁律：references/ 子文档必须带 references/ 前缀（仅当源在根目录时校验）
  if [[ "$target_rel" == references/* ]]; then
    local src_in_root=0
    for f in "${ROOT_FILES[@]}"; do
      if [[ "$f" == "$src_rel" ]]; then
        src_in_root=1
        break
      fi
    done
    if [[ $src_in_root -eq 1 && "$link" != references/* ]]; then
      echo "❌ [$src_rel] 引用 references/ 子文档时缺少 references/ 前缀: $link （应写为 references/$(basename "$link")）"
      errors=$((errors + 1))
    fi
  fi
}

# 主循环：遍历所有 .md 文件
echo "🔍 校验目录: $SKILL_DIR"
echo

while IFS= read -r -d '' md_file; do
  src_rel="${md_file#$SKILL_DIR/}"
  while IFS= read -r link; do
    [[ -z "$link" ]] && continue
    check_link "$src_rel" "$link"
  done < <(extract_links "$md_file")
done < <(find "$SKILL_DIR" -type f -name "*.md" -not -path "*/node_modules/*" -print0)

echo
echo "----------------------------------------"
echo "✅ 已校验链接数: $checked_links"
if [[ $errors -eq 0 ]]; then
  echo "✅ 全部通过"
  exit 0
else
  echo "❌ 发现 $errors 处违规"
  exit 1
fi
