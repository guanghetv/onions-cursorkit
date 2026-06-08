#!/usr/bin/env node
import crypto from "node:crypto";
import { execFileSync, execSync } from "node:child_process";
import process from "node:process";

export function gitTopLevel() {
  try {
    return execSync("git rev-parse --show-toplevel", { encoding: "utf8" }).trim();
  } catch {
    return process.cwd();
  }
}

export function repoName() {
  const top = gitTopLevel();
  return top.split("/").pop() || "unknown";
}

export function branchName() {
  try {
    return execSync("git branch --show-current", { encoding: "utf8" }).trim() || "unknown";
  } catch {
    return "unknown";
  }
}

export function authorEmail() {
  try {
    return execSync("git config user.email", { encoding: "utf8" }).trim() || "unknown";
  } catch {
    return "unknown";
  }
}

export function headSha() {
  return execSync("git rev-parse HEAD", { encoding: "utf8" }).trim();
}

export function gitRemoteProjectPath() {
  try {
    const url = execSync("git remote get-url origin", { encoding: "utf8" }).trim();
    if (url.startsWith("git@")) {
      const part = url.split(":")[1] || "";
      return part.replace(/\.git$/, "");
    }
    const parsed = new URL(url);
    return parsed.pathname.replace(/^\//, "").replace(/\.git$/, "");
  } catch {
    return "";
  }
}

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
