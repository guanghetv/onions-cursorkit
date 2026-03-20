#!/usr/bin/env bash
set -euo pipefail

log_info() {
  printf '[info] %s\n' "$*"
}

log_warn() {
  printf '[warn] %s\n' "$*"
}

log_error() {
  printf '[error] %s\n' "$*" >&2
}

die() {
  log_error "$*"
  exit 1
}

require_cmd() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "缺少必要命令: $cmd"
}

ensure_writable_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    die "目标路径不存在: $dir"
  fi
  if [[ ! -w "$dir" ]]; then
    die "目标路径不可写: $dir"
  fi
}

abs_path() {
  local dir="$1"
  (cd "$dir" && pwd)
}

now_timestamp() {
  date +"%Y%m%d%H%M%S"
}

is_ssh_repo() {
  local repo="$1"
  [[ "$repo" =~ ^git@[^:]+:.+(\.git)?$ ]] || [[ "$repo" =~ ^ssh://[^/]+/.+ ]]
}

fetch_source_repo() {
  local repo="$1"
  local dest="$2"
  require_cmd git
  log_info "拉取安装源: $repo"
  git clone --depth 1 "$repo" "$dest" >/dev/null 2>&1 || die "拉取安装源失败"
}

sync_file() {
  local src="$1"
  local dest="$2"
  local dry_run="$3"
  local force="$4"
  local backup="$5"
  local backup_path="$6"

  if [[ -f "$dest" ]]; then
    if cmp -s "$src" "$dest"; then
      log_info "已一致，跳过: $dest"
      return 0
    fi
    if [[ "$force" == "true" ]]; then
      log_warn "覆盖文件: $dest"
      [[ "$dry_run" == "true" ]] || cp "$src" "$dest"
      return 0
    fi
    if [[ "$backup" == "true" ]]; then
      log_warn "冲突备份: $dest -> $backup_path"
      if [[ "$dry_run" == "false" ]]; then
        mkdir -p "$(dirname "$backup_path")"
        cp "$dest" "$backup_path"
        cp "$src" "$dest"
      fi
      return 0
    fi
    die "文件冲突: ${dest}（使用 --force 或 --backup）"
  fi

  log_info "写入文件: $dest"
  if [[ "$dry_run" == "false" ]]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
  fi
}

sync_tree() {
  local src_dir="$1"
  local dest_dir="$2"
  local dry_run="$3"
  local force="$4"
  local backup="$5"
  local backup_root="$6"

  if [[ ! -d "$src_dir" ]]; then
    die "源目录不存在: $src_dir"
  fi

  while IFS= read -r src_file; do
    local rel="${src_file#$src_dir/}"
    local dest_file="$dest_dir/$rel"
    sync_file "$src_file" "$dest_file" "$dry_run" "$force" "$backup" "$backup_root/$rel"
  done < <(find "$src_dir" -type f)
}
