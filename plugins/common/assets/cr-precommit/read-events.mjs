#!/usr/bin/env node
import fs from "node:fs";

export function readEvents(filePath) {
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

export function filterEvents(events, { repo, branch, author }) {
  return events.filter(
    (event) =>
      (!repo || event.repo === repo) &&
      (!branch || event.branch === branch) &&
      (!author || event.author === author)
  );
}
