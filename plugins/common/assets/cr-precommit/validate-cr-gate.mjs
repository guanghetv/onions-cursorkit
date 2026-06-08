#!/usr/bin/env node
import fs from "node:fs";
import { execSync } from "node:child_process";
import process from "node:process";
import { stagedDiffFingerprint } from "./aicr-utils.mjs";

function parseArgs(argv) {
  const args = { selfCheck: false };
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--self-check") {
      args.selfCheck = true;
      continue;
    }
    if (!token.startsWith("--")) {
      continue;
    }
    const key = token.slice(2);
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`missing value for --${key}`);
    }
    args[key] = value;
    i += 1;
  }
  return args;
}

function getStagedFiles() {
  const out = execSync("git diff --cached --name-only", { encoding: "utf8" });
  return out.split("\n").filter(Boolean);
}

function validate(eventFile, repo, branch, author, stagedFiles) {
  if (!fs.existsSync(eventFile)) {
    return { ok: false, reason: "no_event_log" };
  }

  const lines = fs.readFileSync(eventFile, "utf8").split("\n").filter(Boolean);
  let lastCrTs = 0;
  let lastAttemptTs = 0;
  let lastCrEvent = null;

  for (const line of lines) {
    let event;
    try {
      event = JSON.parse(line);
    } catch {
      continue;
    }
    if (event.repo !== repo || event.branch !== branch || event.author !== author) {
      continue;
    }
    if (!event.timestamp) {
      continue;
    }
    const ts = Date.parse(event.timestamp);
    if (Number.isNaN(ts)) {
      continue;
    }

    if (event.event === "cr_completed") {
      if (ts >= lastCrTs) {
        lastCrTs = ts;
        lastCrEvent = event;
      }
      continue;
    }

    if (
      event.event === "commit_attempted" ||
      event.event === "commit_blocked_without_cr" ||
      event.event === "commit_bypassed_cr"
    ) {
      if (ts > lastAttemptTs) {
        lastAttemptTs = ts;
      }
    }
  }

  if (!lastCrEvent || lastCrTs <= lastAttemptTs) {
    return { ok: false, reason: "no_valid_cr" };
  }

  if (stagedFiles.length === 0) {
    return { ok: true, reason: "empty_staged" };
  }

  const expectedFingerprint = stagedDiffFingerprint(stagedFiles);
  const crFiles = Array.isArray(lastCrEvent.files) ? lastCrEvent.files.map(String).sort() : [];
  const stagedSorted = [...stagedFiles].map(String).sort();

  if (crFiles.length === 0) {
    return { ok: false, reason: "missing_cr_files" };
  }

  if (JSON.stringify(crFiles) !== JSON.stringify(stagedSorted)) {
    return {
      ok: false,
      reason: "files_mismatch",
      expected: stagedSorted,
      got: crFiles
    };
  }

  if (!lastCrEvent.diff_fingerprint || lastCrEvent.diff_fingerprint !== expectedFingerprint) {
    return { ok: false, reason: "fingerprint_mismatch" };
  }

  if (lastCrEvent.status !== "pass") {
    return {
      ok: false,
      reason: lastCrEvent.status === "fail" ? "cr_has_findings" : "cr_status_missing_or_invalid"
    };
  }

  return { ok: true, reason: "ok" };
}

function main() {
  try {
    const args = parseArgs(process.argv);
    if (args.selfCheck) {
      console.log("SELF_CHECK_OK");
      return;
    }

    const eventFile = args.events || process.env.AICR_EVENT_LOG || ".git/aicr/events.ndjson";
    const repo = args.repo;
    const branch = args.branch;
    const author = args.author;

    if (!repo || !branch || !author) {
      throw new Error("missing --repo/--branch/--author");
    }

    const stagedFiles = getStagedFiles();
    const result = validate(eventFile, repo, branch, author, stagedFiles);

    if (result.ok) {
      console.log("CR_GATE_OK");
      return;
    }

    const messages = {
      no_event_log: "未发现 /cr 事件日志，请先执行 /cr",
      no_valid_cr: "未发现有效的 /cr 记录，请先执行 /cr",
      missing_cr_files: "最近一次 /cr 未记录审查文件列表，请重新执行 /cr",
      files_mismatch: "暂存区文件与 /cr 审查范围不一致，请对当前暂存区重新执行 /cr",
      fingerprint_mismatch: "暂存区变更与 /cr 记录不匹配，请对当前暂存区重新执行 /cr",
      cr_has_findings:
        "最近一次 /cr 报告存在问题（🔴/🟠），须由开发者修复后重新 /cr，禁止直接提交",
      cr_status_missing_or_invalid:
        "最近一次 /cr 未标记为通过（status=pass），请重新执行 /cr"
    };

    console.error(`[aicr-reminder] ${messages[result.reason] || result.reason}`);
    if (result.reason === "files_mismatch") {
      console.error(`[aicr-reminder] 暂存区: ${(result.expected || []).join(", ")}`);
      console.error(`[aicr-reminder] /cr 范围: ${(result.got || []).join(", ")}`);
    }
    process.exit(1);
  } catch (error) {
    console.error(`VALIDATOR_CRASH: ${error.message}`);
    process.exit(2);
  }
}

main();
