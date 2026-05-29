#!/usr/bin/env node
import fs from "node:fs/promises";
import process from "node:process";
import { gitlabJson, resolveGitLabAuth } from "./gitlab-auth.mjs";

function parseArgs(argv) {
  const args = {};
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

async function main() {
  const args = parseArgs(process.argv);
  if (args.selfCheck) {
    console.log("SELF_CHECK_OK");
    return;
  }

  const auth = resolveGitLabAuth();
  const apiBase = (args["api-base"] || process.env.GITLAB_API_BASE || "https://gitlab.yc345.tv/api/v4").replace(/\/$/, "");
  const projectId = args["project-id"] || process.env.CI_PROJECT_ID;
  const mrIid = args["mr-iid"] || process.env.CI_MERGE_REQUEST_IID;
  const output = args.output || "mr-commits.json";

  if (!auth || !projectId || !mrIid) {
    throw new Error("missing CI_JOB_TOKEN (or GITLAB_TOKEN), project id, or mr iid");
  }

  const commits = await gitlabJson(
    `${apiBase}/projects/${projectId}/merge_requests/${mrIid}/commits?per_page=100`,
    auth
  );
  const ids = commits.map((commit) => String(commit.id));
  const payload = JSON.stringify(ids, null, 2);
  await fs.writeFile(output, `${payload}\n`, "utf8");
  console.log(`COMMITS:${ids.length}`);
}

main().catch((error) => {
  console.error(`LIST_MR_COMMITS_FAILED: ${error.message}`);
  process.exit(1);
});
