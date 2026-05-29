#!/usr/bin/env node
import process from "node:process";
import { fileURLToPath } from "node:url";
import { authorEmail, branchName, repoName } from "./repo-context.mjs";

const loggerPath = fileURLToPath(new URL("./event-log.mjs", import.meta.url));
const eventFile = process.env.AICR_EVENT_LOG || ".git/aicr/events.ndjson";

async function main() {
  const eventName = process.argv[2];
  const extraJson = process.argv[3] || "{}";
  if (!eventName) {
    throw new Error("usage: log-hook-event.mjs <event> [json-extra]");
  }

  let extra = {};
  try {
    extra = JSON.parse(extraJson);
  } catch (error) {
    throw new Error(`invalid json-extra: ${error.message}`);
  }

  const payload = {
    event: eventName,
    repo: repoName(),
    branch: branchName(),
    author: authorEmail(),
    ...extra
  };

  process.env.AICR_EVENT_LOG = eventFile;
  const { spawnSync } = await import("node:child_process");
  const result = spawnSync(process.execPath, [loggerPath, JSON.stringify(payload)], {
    encoding: "utf8"
  });
  if (result.status !== 0) {
    process.stderr.write(result.stderr || "EVENT_WRITE_FAILED\n");
    process.exit(result.status || 1);
  }
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exit(1);
});
