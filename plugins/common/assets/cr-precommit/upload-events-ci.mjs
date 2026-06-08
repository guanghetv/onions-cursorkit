#!/usr/bin/env node
import fs from "node:fs";
import fsp from "node:fs/promises";
import process from "node:process";
import { authorEmail, branchName, gitRemoteProjectPath, repoName } from "./aicr-utils.mjs";

const eventFile = process.env.AICR_EVENT_LOG || ".git/aicr/events.ndjson";
const SNAPSHOT_RETAIN = Math.max(1, Number.parseInt(process.env.AICR_SNAPSHOT_RETAIN || "3", 10) || 3);

function readEvents(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  return fs
    .readFileSync(filePath, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function resolveAicrIngestUrl() {
  const ingestUrl = process.env.AICR_INGEST_URL;
  if (ingestUrl && ingestUrl.trim()) {
    return ingestUrl.trim();
  }
  return "https://aicrfe.yc345.tv/review/aicr/events";
}

async function pruneLocalSnapshots(snapshotDir, prefix) {
  let names;
  try {
    names = await fsp.readdir(snapshotDir);
  } catch {
    return;
  }

  const candidates = [];
  for (const name of names) {
    if (!name.startsWith(prefix) || !name.endsWith(".ndjson")) {
      continue;
    }
    const filePath = `${snapshotDir}/${name}`;
    const stat = await fsp.stat(filePath);
    candidates.push({ filePath, mtimeMs: stat.mtimeMs });
  }

  candidates.sort((a, b) => b.mtimeMs - a.mtimeMs);
  const stale = candidates.slice(SNAPSHOT_RETAIN);
  await Promise.all(stale.map((item) => fsp.unlink(item.filePath)));
}

async function uploadToAicrService({ ingestUrl, payload }) {
  const headers = { "Content-Type": "application/json" };
  const response = await fetch(ingestUrl, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`aicr ingest failed (${response.status}): ${body}`);
  }
}

async function main() {
  if (process.argv.includes("--self-check")) {
    console.log("SELF_CHECK_OK");
    return;
  }

  const branch = branchName();
  const author = authorEmail();
  const projectId = (process.env.AICR_PROJECT_ID || process.env.CI_PROJECT_ID || "").trim();
  const projectPath = (process.env.AICR_PROJECT_PATH || "").trim() || gitRemoteProjectPath();
  const events = readEvents(eventFile);

  if (events.length === 0) {
    console.log("NO_EVENTS_TO_UPLOAD");
    return;
  }

  const body = `${events.map((event) => JSON.stringify(event)).join("\n")}\n`;
  const snapshotDir = ".git/aicr/ci-export";
  const branchSlug = branch.replace(/\//g, "-");
  const snapshotPath = `${snapshotDir}/${repoName()}-${branchSlug}-${Date.now()}.ndjson`;
  await fsp.mkdir(snapshotDir, { recursive: true });
  await fsp.writeFile(snapshotPath, body, "utf8");
  await pruneLocalSnapshots(snapshotDir, `${repoName()}-${branchSlug}-`);
  console.log(`LOCAL_SNAPSHOT:${snapshotPath}`);

  if (!projectId && !projectPath) {
    console.error(
      "MISSING_PROJECT_SCOPE: set AICR_PROJECT_PATH or AICR_PROJECT_ID (CI uses CI_PROJECT_ID); ensure git remote origin resolves to a GitLab project path"
    );
    process.exit(1);
  }

  const ingestUrl = resolveAicrIngestUrl();
  await uploadToAicrService({
    ingestUrl,
    payload: {
      project_id: projectId,
      project_path: projectPath,
      repo: repoName(),
      branch,
      author,
      events,
    },
  });
  console.log("UPLOAD_OK");
}

main().catch((error) => {
  console.error(`UPLOAD_EVENTS_FAILED: ${error.message}`);
  process.exit(1);
});
