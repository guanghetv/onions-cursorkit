#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import process from "node:process";
import { authorEmail, branchName, gitRemoteProjectPath, repoName } from "./repo-context.mjs";
import { readEvents } from "./read-events.mjs";
import { gitlabFetch, gitlabJson, resolveGitLabAuth } from "./gitlab-auth.mjs";

const eventFile = process.env.AICR_EVENT_LOG || ".git/aicr/events.ndjson";
const packageName = process.env.AICR_CI_PACKAGE || "aicr-events";

function authorKey(email) {
  return crypto.createHash("sha256").update(String(email)).digest("hex").slice(0, 16);
}

function encodeProjectPath(path) {
  return encodeURIComponent(path);
}

async function uploadPackage({ apiBase, projectId, auth, branch, author, body }) {
  const version = `${branch}--${authorKey(author)}--${Date.now()}`;
  const url =
    `${apiBase}/projects/${projectId}/packages/generic/${packageName}/${encodeURIComponent(version)}/events.ndjson`;

  await gitlabFetch(url, auth, {
    method: "PUT",
    headers: { "Content-Type": "application/octet-stream" },
    body
  });
}

async function resolveProjectId(apiBase, auth) {
  if (process.env.CI_PROJECT_ID) {
    return String(process.env.CI_PROJECT_ID);
  }
  const projectPath = gitRemoteProjectPath();
  if (!projectPath) {
    throw new Error("cannot resolve project id (configure origin remote)");
  }
  const data = await gitlabJson(`${apiBase}/projects/${encodeProjectPath(projectPath)}`, auth);
  return String(data.id);
}

async function main() {
  if (process.argv.includes("--self-check")) {
    console.log("SELF_CHECK_OK");
    return;
  }

  const auth = resolveGitLabAuth({ localOnly: true });
  const apiBase = (process.env.GITLAB_API_BASE || "https://gitlab.yc345.tv/api/v4").replace(/\/$/, "");
  const branch = branchName();
  const author = authorEmail();
  const events = readEvents(eventFile);

  if (events.length === 0) {
    console.log("NO_EVENTS_TO_UPLOAD");
    return;
  }

  const body = `${events.map((event) => JSON.stringify(event)).join("\n")}\n`;
  const snapshotDir = ".git/aicr/ci-export";
  const snapshotPath = `${snapshotDir}/${repoName()}-${branch}-${authorKey(author)}.ndjson`;
  await fs.mkdir(snapshotDir, { recursive: true });
  await fs.writeFile(snapshotPath, body, "utf8");
  console.log(`LOCAL_SNAPSHOT:${snapshotPath}`);

  if (!auth) {
    console.log("SKIP_UPLOAD_NO_TOKEN");
    return;
  }

  const projectId = await resolveProjectId(apiBase, auth);
  await uploadPackage({ apiBase, projectId, auth, branch, author, body });
  console.log("UPLOAD_OK");
}

main().catch((error) => {
  console.error(`UPLOAD_EVENTS_FAILED: ${error.message}`);
  process.exit(1);
});
