#!/usr/bin/env node
import process from "node:process";
import { fileURLToPath } from "node:url";
import { authorEmail, branchName, headSha, repoName } from "./repo-context.mjs";
import { filterEvents, readEvents } from "./read-events.mjs";

const eventFile = process.env.AICR_EVENT_LOG || ".git/aicr/events.ndjson";
const loggerPath = fileURLToPath(new URL("./event-log.mjs", import.meta.url));

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

function hasLinkedSha(events, sha) {
  return events.some(
    (event) =>
      event.event === "commit_cr_linked" && String(event.commit_sha) === String(sha)
  );
}

function hasLinkedFingerprint(events, fingerprint) {
  return events.some(
    (event) =>
      event.event === "commit_cr_linked" &&
      event.diff_fingerprint &&
      event.diff_fingerprint === fingerprint
  );
}

async function writeEvent(payload) {
  process.env.AICR_EVENT_LOG = eventFile;
  const { spawnSync } = await import("node:child_process");
  const result = spawnSync(process.execPath, [loggerPath, JSON.stringify(payload)], {
    encoding: "utf8"
  });
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
  if (lastAttempt?.status === "bypassed") {
    console.log("SKIP_BYPASSED_COMMIT");
    return;
  }

  const lastCr = latestEvent(
    scoped,
    "cr_completed",
    (event) => event.status === "pass" && event.diff_fingerprint
  );

  if (!lastCr) {
    console.log("NO_PASS_CR_TO_LINK");
    return;
  }

  if (hasLinkedFingerprint(scoped, lastCr.diff_fingerprint)) {
    console.log("CR_ALREADY_LINKED");
    return;
  }

  await writeEvent({
    event: "commit_cr_linked",
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
