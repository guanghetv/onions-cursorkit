#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { authorEmail, branchName, repoName, stagedDiffFingerprint } from "./aicr-utils.mjs";

const defaultEventFile = ".git/aicr/events.ndjson";
const eventFile = process.env.AICR_EVENT_LOG || defaultEventFile;

async function appendEvent(event) {
  await fs.mkdir(path.dirname(eventFile), { recursive: true });
  await fs.appendFile(eventFile, `${JSON.stringify(event)}\n`, "utf8");
}

function ensureRequiredFields(payload) {
  const requiredFields = ["event", "repo", "branch", "author"];
  for (const key of requiredFields) {
    if (!payload[key] || String(payload[key]).trim().length === 0) {
      throw new Error(`missing required field: ${key}`);
    }
  }
}

function parsePayload() {
  const jsonArg = process.argv[2];
  if (!jsonArg) {
    throw new Error("missing payload argument");
  }
  return JSON.parse(jsonArg);
}

function parseFlagArgs(argv) {
  const args = { event: "", extra: "{}" };
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

async function main() {
  if (process.argv.includes("--self-check")) {
    console.log("SELF_CHECK_OK");
    return;
  }

  let payload;
  if (process.argv.includes("--event")) {
    const args = parseFlagArgs(process.argv);
    if (!args.event) {
      throw new Error("missing --event");
    }
    let extra = {};
    try {
      extra = JSON.parse(args.extra || "{}");
    } catch (error) {
      throw new Error(`invalid --extra json: ${error.message}`);
    }
    payload = {
      event: args.event,
      repo: repoName(),
      branch: branchName(),
      author: authorEmail(),
      ...extra
    };
  } else {
    payload = parsePayload();
  }

  ensureRequiredFields(payload);

  if (Array.isArray(payload.files) && payload.files.length > 0) {
    payload.diff_fingerprint = stagedDiffFingerprint(payload.files);
  }

  payload.timestamp = payload.timestamp || new Date().toISOString();
  await appendEvent(payload);
  console.log("EVENT_WRITTEN");
}

main().catch((error) => {
  console.error(`EVENT_WRITE_FAILED: ${error.message}`);
  process.exit(1);
});
