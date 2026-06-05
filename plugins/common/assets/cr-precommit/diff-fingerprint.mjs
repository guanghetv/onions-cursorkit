#!/usr/bin/env node
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { gitTopLevel } from "./repo-context.mjs";

/**
 * Hash staged diff content for the given paths (not file names alone).
 * Used by pre-commit gate and cr_completed event logging.
 */
export function stagedDiffFingerprint(files) {
  const sorted = [...(files || [])].map(String).filter(Boolean).sort();
  if (sorted.length === 0) {
    return "";
  }

  const repoRoot = gitTopLevel();
  const diff = execFileSync("git", ["-C", repoRoot, "diff", "--cached", "--", ...sorted], {
    encoding: "utf8",
    maxBuffer: 10 * 1024 * 1024
  });

  return crypto.createHash("sha256").update(diff).digest("hex");
}
