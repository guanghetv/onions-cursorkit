#!/usr/bin/env node
import fs from "node:fs";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { authorEmail, branchName, headSha, repoName } from "./aicr-utils.mjs";

const eventFile = process.env.AICR_EVENT_LOG || ".git/aicr/events.ndjson";
const loggerPath = fileURLToPath(new URL("./event-log.mjs", import.meta.url));

const ATTEMPT_EVENTS = new Set([
  "commit_attempted",
  "commit_blocked_without_cr",
  "commit_bypassed_cr"
]);

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

function filterEvents(events, { repo, branch, author }) {
  return events.filter(
    (event) =>
      (!repo || event.repo === repo) &&
      (!branch || event.branch === branch) &&
      (!author || event.author === author)
  );
}

function latestEvent(events, name, predicate = () => true) {
  let latest = null;
  let latestTs = 0;
  for (const event of events) {
    if (event.event !== name || !predicate(event)) {
      continue;
    }
    const ts = Date.parse(event.timestamp || "");
    if (Number.isNaN(ts) || ts < latestTs) {
      continue;
    }
    latestTs = ts;
    latest = event;
  }
  return latest;
}

function attemptTimestampsDesc(events) {
  const timestamps = [];
  for (const event of events) {
    if (!ATTEMPT_EVENTS.has(event.event)) {
      continue;
    }
    const ts = Date.parse(event.timestamp || "");
    if (!Number.isNaN(ts)) {
      timestamps.push(ts);
    }
  }
  return timestamps.sort((a, b) => b - a);
}

function crMatchesCommitCycle(lastCr, prevAttemptTs, lastAttemptTs) {
  const crTs = Date.parse(lastCr.timestamp || "");
  if (Number.isNaN(crTs) || Number.isNaN(lastAttemptTs)) {
    return false;
  }
  return crTs > prevAttemptTs && crTs <= lastAttemptTs;
}

function hasLinkedSha(events, sha) {
  return events.some(
    (event) =>
      event.event === "commit_cr_linked" && String(event.commit_sha) === String(sha)
  );
}

async function writeEvent(extra) {
  process.env.AICR_EVENT_LOG = eventFile;
  const { spawnSync } = await import("node:child_process");
  const result = spawnSync(
    process.execPath,
    [loggerPath, "--event", "commit_cr_linked", "--extra", JSON.stringify(extra)],
    {
      encoding: "utf8"
    }
  );
  if (result.status !== 0) {
    throw new Error(result.stderr || "EVENT_WRITE_FAILED");
  }
}

async function main() {
  if (process.argv.includes("--self-check")) {
    console.log("SELF_CHECK_OK");
    return;
  }

  const repo = repoName();
  const branch = branchName();
  const author = authorEmail();
  const commitSha = headSha();
  const allEvents = readEvents(eventFile);
  const scoped = filterEvents(allEvents, { repo, branch, author });

  if (hasLinkedSha(scoped, commitSha)) {
    console.log("ALREADY_LINKED");
    return;
  }

  const lastAttempt = latestEvent(scoped, "commit_attempted");
  if (!lastAttempt || lastAttempt.status !== "allowed") {
    console.log("SKIP_NON_ALLOWED_COMMIT");
    return;
  }

  const attemptTsDesc = attemptTimestampsDesc(scoped);
  const lastAttemptTs = attemptTsDesc[0] ?? Number.NaN;
  const prevAttemptTs = attemptTsDesc[1] ?? 0;

  const lastCr = latestEvent(
    scoped,
    "cr_completed",
    (event) => event.status === "pass" && event.diff_fingerprint
  );

  if (!lastCr) {
    console.log("NO_PASS_CR_TO_LINK");
    return;
  }

  if (!crMatchesCommitCycle(lastCr, prevAttemptTs, lastAttemptTs)) {
    console.log("CR_NOT_FOR_THIS_COMMIT");
    return;
  }

  await writeEvent({
    commit_sha: commitSha,
    diff_fingerprint: lastCr.diff_fingerprint,
    status: "pass"
  });

  console.log(`LINKED:${commitSha}`);
}

main().catch((error) => {
  console.error(`LINK_FAILED: ${error.message}`);
  process.exit(1);
});
