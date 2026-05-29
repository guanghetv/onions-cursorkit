#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import process from "node:process";

const schemaPath = new URL("./schema.json", import.meta.url);
const defaultEventFile = ".git/aicr/events.ndjson";
const eventFile = process.env.AICR_EVENT_LOG || defaultEventFile;

function fingerprint(files) {
  const normalized = [...files]
    .map((file) => String(file))
    .sort()
    .join("|");
  return crypto.createHash("sha256").update(normalized).digest("hex");
}

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

async function main() {
  if (process.argv.includes("--self-check")) {
    await fs.access(schemaPath);
    console.log("SELF_CHECK_OK");
    return;
  }

  const payload = parsePayload();
  ensureRequiredFields(payload);

  if (Array.isArray(payload.files) && payload.files.length > 0) {
    payload.diff_fingerprint = fingerprint(payload.files);
  }

  payload.timestamp = payload.timestamp || new Date().toISOString();
  await appendEvent(payload);
  console.log("EVENT_WRITTEN");
}

main().catch((error) => {
  console.error(`EVENT_WRITE_FAILED: ${error.message}`);
  process.exit(1);
});
