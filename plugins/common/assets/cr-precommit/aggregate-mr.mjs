#!/usr/bin/env node
import fs from "node:fs/promises";
import process from "node:process";
import { readEvents } from "./read-events.mjs";

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

function readCommits(rawValue) {
  const parsed = JSON.parse(rawValue || "[]");
  if (!Array.isArray(parsed)) {
    throw new Error("commits must be an array");
  }
  return parsed.map((item) => String(item));
}

function isPassStatus(status) {
  return status === undefined || status === null || status === "pass";
}

function collectCoveredShas(events) {
  const covered = new Set();

  for (const event of events) {
    if (event.event === "commit_cr_linked") {
      if (event.commit_sha && isPassStatus(event.status)) {
        covered.add(String(event.commit_sha));
      }
      continue;
    }

    if (event.event === "cr_completed" && event.commit_sha && event.status === "pass") {
      covered.add(String(event.commit_sha));
    }
  }

  return covered;
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.events) {
    throw new Error("missing --events argument");
  }

  const commits = readCommits(args.commits || "[]");
  const events = readEvents(args.events);
  const covered = collectCoveredShas(events);

  const missingCommits = commits.filter((sha) => !covered.has(sha));
  const coveredCommits = commits.length - missingCommits.length;
  const coverageRate = commits.length === 0 ? 1 : coveredCommits / commits.length;

  const result = {
    total_commits: commits.length,
    covered_commits: coveredCommits,
    coverage_rate: coverageRate,
    missing_commits: missingCommits,
    updated_at: new Date().toISOString()
  };

  if (args.output) {
    await fs.writeFile(args.output, `${JSON.stringify(result, null, 2)}\n`, "utf8");
  }
  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  console.error(`AGGREGATE_FAILED: ${error.message}`);
  process.exit(1);
});
