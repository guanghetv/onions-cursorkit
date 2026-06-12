#!/usr/bin/env node

/**
 * 从 ai-guardrails 仓库同步 skills / rules / mcp 模板到本仓库插件目录。
 *
 * ai-guardrails 是内容源（source of truth），本脚本将其内容按主题映射为
 * onions-plugins 市场中的插件，请勿手改同步产物，改动请提交到 ai-guardrails。
 *
 * 用法：
 *   node scripts/sync-guardrails.mjs                       # 默认源：../ai-guardrails
 *   node scripts/sync-guardrails.mjs --source /path/to/ai-guardrails
 *   node scripts/sync-guardrails.mjs --dry-run
 */

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");

const DEFAULT_SOURCE = path.resolve(repoRoot, "../ai-guardrails");

/**
 * 插件映射表：ai-guardrails 内容 → 本仓库插件目录。
 *
 * - skills: packages/skills/src/<name> → plugins/<plugin>/skills/<name>
 * - rules:  packages/rules/src/<name>/<name>.mdc → plugins/<plugin>/rules/<name>.mdc
 * - mcp:    packages/mcp/templates/mcp.json → plugins/<plugin>/mcp.json
 *
 * 同步时脚本接管目标插件的 skills/、rules/ 与 mcp.json（全删全建），
 * assets/ 与 .cursor-plugin/ 不受影响。
 */
const PLUGIN_MAPPING = {
  frontend: {
    skills: [
      "fe-security",
      "frontend-tech-stack-skill",
      "frontend-page-audit",
      "frontend-engineering-standards",
      "user-optimization",
    ],
    rules: [
      "commit-rule",
      "fe-engineering-baseline",
      "fe-engineering-build-test-quality",
      "fe-engineering-dependencies",
      "fe-engineering-monorepo",
      "fe-engineering-release-deploy",
      "fe-engineering-toolchain-env",
      "fe-engineering-workspace-layout",
      "user-optimization-new-feature",
      "user-optimization-refactor",
    ],
  },
  "fe-figma-flow": {
    skills: [
      "figma-read-skill",
      "figma-img-cdn-skill",
      "responsive-layout",
      "responsive-layout-analysis",
      "design-tokens",
    ],
    mcp: true,
  },
  "fe-onion-stack": {
    skills: [
      "onion-ui-skill",
      "onion-utils-skill",
      "onion-video",
      "axios-skill",
    ],
  },
};

/**
 * 上游 frontmatter 缺失字段的修补表（cursorkit 校验要求 rule 必须有 description）。
 * 修补仅在上游缺失时注入，上游补齐后可删除对应条目。
 */
const RULE_DESCRIPTION_FIXES = {
  "commit-rule": "Commit 信息规范：约定式提交格式、类型与中文描述要求。",
};

const args = process.argv.slice(2);
let sourceRoot = DEFAULT_SOURCE;
let dryRun = false;

for (let i = 0; i < args.length; i += 1) {
  const arg = args[i];
  if (arg === "--source") {
    sourceRoot = path.resolve(args[i + 1] ?? "");
    i += 1;
  } else if (arg.startsWith("--source=")) {
    sourceRoot = path.resolve(arg.slice("--source=".length));
  } else if (arg === "--dry-run") {
    dryRun = true;
  } else if (arg === "--help" || arg === "-h") {
    console.log(
      "Usage: node scripts/sync-guardrails.mjs [--source <ai-guardrails path>] [--dry-run]"
    );
    process.exit(0);
  } else {
    console.error(`Unknown argument: ${arg}`);
    process.exit(1);
  }
}

const skillsSrc = path.join(sourceRoot, "packages/skills/src");
const rulesSrc = path.join(sourceRoot, "packages/rules/src");
const mcpTemplate = path.join(sourceRoot, "packages/mcp/templates/mcp.json");

const log = (msg) => console.log(`[sync-guardrails] ${msg}`);
const warn = (msg) => console.warn(`[sync-guardrails][warn] ${msg}`);

async function pathExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

/** 去掉 frontmatter 前的空行/空白，保证文件以 "---\n" 开头（校验器要求）。 */
function normalizeFrontmatterStart(content) {
  const normalized = content.replace(/\r\n/g, "\n");
  const trimmed = normalized.replace(/^[\s\n]+(?=---\n)/, "");
  return trimmed;
}

/** 若 rule 缺 description，按修补表注入；仍缺失则抛错。 */
function ensureRuleDescription(content, ruleName) {
  if (!content.startsWith("---\n")) {
    throw new Error(`rule "${ruleName}" 缺少 YAML frontmatter`);
  }
  const end = content.indexOf("\n---\n", 4);
  if (end === -1) {
    throw new Error(`rule "${ruleName}" frontmatter 未闭合`);
  }
  const block = content.slice(4, end);
  if (/^description\s*:/m.test(block)) {
    return content;
  }
  const fix = RULE_DESCRIPTION_FIXES[ruleName];
  if (!fix) {
    throw new Error(
      `rule "${ruleName}" 缺少 description 且无修补条目，请在上游补齐或在 RULE_DESCRIPTION_FIXES 中登记`
    );
  }
  warn(`rule "${ruleName}" 上游缺少 description，已注入修补文案`);
  return `---\ndescription: ${fix}\n${block}\n---\n${content.slice(end + 5)}`;
}

async function readSourceVersion() {
  const meta = { syncedAt: new Date().toISOString(), source: sourceRoot };
  try {
    const pkg = JSON.parse(
      await fs.readFile(path.join(sourceRoot, "package.json"), "utf8")
    );
    meta.sourceName = pkg.name ?? "ai-guardrails";
    meta.sourceVersion = pkg.version ?? "unknown";
  } catch {
    meta.sourceVersion = "unknown";
  }
  try {
    meta.sourceCommit = execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: sourceRoot,
      encoding: "utf8",
    }).trim();
  } catch {
    /* 非 git 目录（如 npm tarball 解包）时忽略 */
  }
  return meta;
}

async function rmIfExists(target) {
  if (await pathExists(target)) {
    if (dryRun) {
      log(`(dry-run) rm -rf ${path.relative(repoRoot, target)}`);
    } else {
      await fs.rm(target, { recursive: true });
    }
  }
}

async function copySkill(skillName, destSkillsDir) {
  const src = path.join(skillsSrc, skillName);
  if (!(await pathExists(path.join(src, "SKILL.md")))) {
    // 允许 skill 集合目录（子目录各含 SKILL.md），如 user-optimization
    const entries = await fs.readdir(src, { withFileTypes: true });
    const hasNested = entries.some((e) => e.isDirectory());
    if (!hasNested) {
      throw new Error(`skill "${skillName}" 缺少 SKILL.md：${src}`);
    }
  }
  const dest = path.join(destSkillsDir, skillName);
  if (dryRun) {
    log(`(dry-run) copy skill ${skillName} -> ${path.relative(repoRoot, dest)}`);
    return;
  }
  await fs.cp(src, dest, { recursive: true });

  // 归一化所有 SKILL.md 的 frontmatter 起始位置
  const stack = [dest];
  while (stack.length > 0) {
    const current = stack.pop();
    const entries = await fs.readdir(current, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(entryPath);
      } else if (entry.name === "SKILL.md") {
        const content = await fs.readFile(entryPath, "utf8");
        const normalized = normalizeFrontmatterStart(content);
        if (normalized !== content) {
          warn(`已归一化 frontmatter 起始空行: ${path.relative(repoRoot, entryPath)}`);
          await fs.writeFile(entryPath, normalized);
        }
      }
    }
  }
}

async function copyRule(ruleName, destRulesDir) {
  const srcFile = path.join(rulesSrc, ruleName, `${ruleName}.mdc`);
  if (!(await pathExists(srcFile))) {
    throw new Error(`rule "${ruleName}" 缺少 ${ruleName}.mdc：${srcFile}`);
  }
  const dest = path.join(destRulesDir, `${ruleName}.mdc`);
  if (dryRun) {
    log(`(dry-run) copy rule ${ruleName} -> ${path.relative(repoRoot, dest)}`);
    return;
  }
  let content = normalizeFrontmatterStart(await fs.readFile(srcFile, "utf8"));
  content = ensureRuleDescription(content, ruleName);
  await fs.mkdir(destRulesDir, { recursive: true });
  await fs.writeFile(dest, content);
}

async function syncPlugin(pluginName, mapping, sourceMeta) {
  const pluginDir = path.join(repoRoot, "plugins", pluginName);
  if (!(await pathExists(path.join(pluginDir, ".cursor-plugin", "plugin.json")))) {
    throw new Error(
      `插件 ${pluginName} 缺少 .cursor-plugin/plugin.json，请先创建插件清单`
    );
  }

  log(`同步插件 ${pluginName} ...`);

  const skillsDir = path.join(pluginDir, "skills");
  const rulesDir = path.join(pluginDir, "rules");
  const mcpFile = path.join(pluginDir, "mcp.json");

  await rmIfExists(skillsDir);
  await rmIfExists(rulesDir);
  if (mapping.mcp) {
    await rmIfExists(mcpFile);
  }

  for (const skillName of mapping.skills ?? []) {
    await copySkill(skillName, skillsDir);
  }
  for (const ruleName of mapping.rules ?? []) {
    await copyRule(ruleName, rulesDir);
  }
  if (mapping.mcp) {
    if (dryRun) {
      log(`(dry-run) copy mcp.json -> plugins/${pluginName}/mcp.json`);
    } else {
      await fs.copyFile(mcpTemplate, mcpFile);
    }
  }

  const meta = {
    ...sourceMeta,
    plugin: pluginName,
    skills: mapping.skills ?? [],
    rules: mapping.rules ?? [],
    mcp: Boolean(mapping.mcp),
  };
  if (!dryRun) {
    await fs.writeFile(
      path.join(pluginDir, ".sync-meta.json"),
      `${JSON.stringify(meta, null, 2)}\n`
    );
  }
}

async function reportUnmapped() {
  const mappedSkills = new Set(
    Object.values(PLUGIN_MAPPING).flatMap((m) => m.skills ?? [])
  );
  const mappedRules = new Set(
    Object.values(PLUGIN_MAPPING).flatMap((m) => m.rules ?? [])
  );

  const skillEntries = await fs.readdir(skillsSrc, { withFileTypes: true });
  for (const entry of skillEntries) {
    if (entry.isDirectory() && !mappedSkills.has(entry.name)) {
      warn(`上游 skill 未映射到任何插件（跳过）: ${entry.name}`);
    }
  }
  const ruleEntries = await fs.readdir(rulesSrc, { withFileTypes: true });
  for (const entry of ruleEntries) {
    if (entry.isDirectory() && !mappedRules.has(entry.name)) {
      warn(`上游 rule 未映射到任何插件（跳过）: ${entry.name}`);
    }
  }
}

async function main() {
  for (const [label, p] of [
    ["skills 源目录", skillsSrc],
    ["rules 源目录", rulesSrc],
    ["mcp 模板", mcpTemplate],
  ]) {
    if (!(await pathExists(p))) {
      console.error(`[sync-guardrails][error] ${label}不存在: ${p}`);
      console.error("请用 --source 指定 ai-guardrails 仓库路径");
      process.exit(1);
    }
  }

  const sourceMeta = await readSourceVersion();
  log(
    `内容源: ${sourceMeta.sourceName ?? "ai-guardrails"}@${sourceMeta.sourceVersion}` +
      (sourceMeta.sourceCommit ? ` (${sourceMeta.sourceCommit.slice(0, 8)})` : "")
  );

  for (const [pluginName, mapping] of Object.entries(PLUGIN_MAPPING)) {
    await syncPlugin(pluginName, mapping, sourceMeta);
  }

  await reportUnmapped();

  log(dryRun ? "dry-run 完成，未写入文件" : "同步完成");
  log("请运行 node scripts/validate-template.mjs 校验");
}

await main();
