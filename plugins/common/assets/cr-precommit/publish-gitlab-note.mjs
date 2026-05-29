#!/usr/bin/env node
import fs from "node:fs/promises";
import process from "node:process";
import {
  authSourceLabel,
  gitlabJson,
  gitlabText,
  resolveGitLabAuth
} from "./gitlab-auth.mjs";

const DEFAULT_MARKER = "<!-- aicr-coverage -->";

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
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

function required(args, key) {
  const value = args[key];
  if (!value) {
    throw new Error(`missing --${key} argument`);
  }
  return value;
}

async function readReport(reportPath) {
  const raw = await fs.readFile(reportPath, "utf8");
  return JSON.parse(raw);
}

function buildComment(report, marker) {
  const rate = Number(report.coverage_rate ?? 0);
  const percentage = Number.isFinite(rate) ? `${(rate * 100).toFixed(1)}%` : "N/A";
  const missing = Array.isArray(report.missing_commits) ? report.missing_commits : [];
  const missingLines = missing.length === 0
    ? "- 无"
    : missing.slice(0, 20).map((sha) => `- \`${sha}\``).join("\n");

  return [
    marker,
    "## AICR 提交前自检覆盖率",
    "",
    `- 总提交数: **${report.total_commits ?? 0}**`,
    `- 已覆盖提交数: **${report.covered_commits ?? 0}**`,
    `- 覆盖率: **${percentage}**`,
    "",
    "### 未覆盖提交",
    missingLines,
    "",
    `_updated_at: ${report.updated_at || new Date().toISOString()}_`
  ].join("\n");
}

async function main() {
  const args = parseArgs(process.argv);
  const apiBase = (args["api-base"] || process.env.GITLAB_API_BASE || "https://gitlab.yc345.tv/api/v4").replace(/\/$/, "");
  const project = encodeURIComponent(required(args, "project-id"));
  const mrIid = required(args, "mr-iid");
  const reportFile = required(args, "report-file");
  const marker = args.marker || DEFAULT_MARKER;
  const dryRun = args["dry-run"] === "true";
  const auth = resolveGitLabAuth();

  if (!auth && !dryRun) {
    throw new Error("missing CI_JOB_TOKEN or GITLAB_TOKEN");
  }

  const report = await readReport(reportFile);
  const body = buildComment(report, marker);
  const notesUrl = `${apiBase}/projects/${project}/merge_requests/${mrIid}/notes`;

  if (dryRun) {
    console.log(
      JSON.stringify(
        { mode: "dry-run", auth: authSourceLabel(auth), notes_url: notesUrl, body },
        null,
        2
      )
    );
    return;
  }

  const notes = await gitlabJson(notesUrl, auth);
  const existing = Array.isArray(notes)
    ? notes.find((note) => typeof note.body === "string" && note.body.includes(marker))
    : null;

  if (existing?.id) {
    const updateUrl = `${notesUrl}/${existing.id}`;
    await gitlabJson(updateUrl, auth, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body })
    });
    console.log(`NOTE_UPDATED:${existing.id}`);
    return;
  }

  const created = await gitlabJson(notesUrl, auth, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body })
  });
  console.log(`NOTE_CREATED:${created.id}`);
}

main().catch((error) => {
  console.error(`PUBLISH_FAILED: ${error.message}`);
  process.exit(1);
});
