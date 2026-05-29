#!/usr/bin/env node
import fs from "node:fs/promises";
import process from "node:process";
import { gitlabJson, gitlabText, resolveGitLabAuth } from "./gitlab-auth.mjs";

const packageName = process.env.AICR_CI_PACKAGE || "aicr-events";

function parseArgs(argv) {
  const args = { merge: true };
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

async function listPackages(apiBase, projectId, auth, branch) {
  const url = `${apiBase}/projects/${projectId}/packages?package_type=generic&package_name=${encodeURIComponent(packageName)}&order_by=created_at&sort=desc&per_page=100`;
  const packages = await gitlabJson(url, auth);
  return packages.filter((item) => {
    const version = String(item.version || "");
    return version.startsWith(`${branch}--`);
  });
}

async function downloadPackageFile(apiBase, projectId, auth, packageId, fileName) {
  const url = `${apiBase}/projects/${projectId}/packages/${packageId}/package_files`;
  const files = await gitlabJson(url, auth);
  const target = files.find((file) => file.file_name === fileName) || files[0];
  if (!target) {
    return "";
  }
  return gitlabText(target.download_url || `${url}/${target.id}/download`, auth);
}

async function mergeLocalSnapshots(outputPath, branch) {
  const dir = ".git/aicr/ci-export";
  let merged = [];
  try {
    const files = await fs.readdir(dir);
    for (const file of files) {
      if (!file.includes(`-${branch}-`) || !file.endsWith(".ndjson")) {
        continue;
      }
      const raw = await fs.readFile(`${dir}/${file}`, "utf8");
      merged = merged.concat(
        raw
          .split("\n")
          .filter(Boolean)
          .map((line) => {
            try {
              return JSON.parse(line);
            } catch {
              return null;
            }
          })
          .filter(Boolean)
      );
    }
  } catch {
    return 0;
  }
  if (merged.length === 0) {
    return 0;
  }
  await fs.mkdir(outputPath.split("/").slice(0, -1).join("/") || ".", { recursive: true });
  await fs.writeFile(outputPath, `${merged.map((e) => JSON.stringify(e)).join("\n")}\n`, "utf8");
  return merged.length;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.selfCheck) {
    console.log("SELF_CHECK_OK");
    return;
  }

  const output = args.output || ".git/aicr/events.ndjson";
  const branch = args.branch || process.env.CI_MERGE_REQUEST_SOURCE_BRANCH_NAME || process.env.CI_COMMIT_REF_NAME || "";
  const auth = resolveGitLabAuth();
  const apiBase = (args["api-base"] || process.env.GITLAB_API_BASE || "https://gitlab.yc345.tv/api/v4").replace(/\/$/, "");
  const projectId = args["project-id"] || process.env.CI_PROJECT_ID;

  if (!auth || !projectId) {
    const localCount = branch ? await mergeLocalSnapshots(output, branch) : 0;
    console.log(localCount > 0 ? `LOCAL_MERGE:${localCount}` : "NO_REMOTE_OR_LOCAL_EVENTS");
    return;
  }

  const packages = branch ? await listPackages(apiBase, projectId, auth, branch) : [];
  const lines = [];
  for (const pkg of packages.slice(0, 50)) {
    const content = await downloadPackageFile(apiBase, projectId, auth, pkg.id, "events.ndjson");
    for (const line of content.split("\n").filter(Boolean)) {
      lines.push(line);
    }
  }

  if (lines.length === 0 && branch) {
    await mergeLocalSnapshots(output, branch);
    console.log("FALLBACK_LOCAL_SNAPSHOT");
    return;
  }

  await fs.mkdir(output.split("/").slice(0, -1).join("/") || ".", { recursive: true });
  await fs.writeFile(output, `${lines.join("\n")}\n`, "utf8");
  console.log(`FETCHED:${lines.length}`);
}

main().catch((error) => {
  console.error(`FETCH_EVENTS_FAILED: ${error.message}`);
  process.exit(1);
});
