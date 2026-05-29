#!/usr/bin/env bash
set -euo pipefail

TARGET_REPO="${1:-$(pwd)}"
AICR_DIR="$TARGET_REPO/.githooks/aicr"
EVENTS="$TARGET_REPO/.git/aicr/events.ndjson"
TEST_SHA="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"

cd "$TARGET_REPO"

for script in event-log.mjs validate-cr-gate.mjs link-cr-commit.mjs upload-events-ci.mjs fetch-events-ci.mjs list-mr-commits.mjs; do
  node "$AICR_DIR/$script" --self-check
done

mkdir -p "$(dirname "$EVENTS")"
repo_name="$(basename "$(git rev-parse --show-toplevel)")"
branch_name="$(git branch --show-current 2>/dev/null || echo test)"
author_name="$(git config user.email 2>/dev/null || echo test@example.com)"

node "$AICR_DIR/event-log.mjs" "{\"event\":\"cr_completed\",\"repo\":\"$repo_name\",\"branch\":\"$branch_name\",\"author\":\"$author_name\",\"status\":\"pass\",\"files\":[\"smoke.txt\"]}"
node "$AICR_DIR/event-log.mjs" "{\"event\":\"commit_cr_linked\",\"repo\":\"$repo_name\",\"branch\":\"$branch_name\",\"author\":\"$author_name\",\"status\":\"pass\",\"commit_sha\":\"$TEST_SHA\",\"diff_fingerprint\":\"$(node -e "const c=require('crypto'); process.stdout.write(c.createHash('sha256').update('smoke.txt').digest('hex'))")\"}"

result="$(node "$AICR_DIR/aggregate-mr.mjs" --events "$EVENTS" --commits "[\"$TEST_SHA\"]")"
echo "$result" | node -e "
const data = JSON.parse(require('fs').readFileSync(0,'utf8'));
if (data.coverage_rate !== 1 || data.covered_commits !== 1) {
  console.error('SMOKE_FAILED: expected 100% coverage', data);
  process.exit(1);
}
console.log('SMOKE_OK');
"
