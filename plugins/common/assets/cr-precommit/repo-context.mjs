#!/usr/bin/env node
import { execSync } from "node:child_process";

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
