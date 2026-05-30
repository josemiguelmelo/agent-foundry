#!/usr/bin/env bash
# End-to-end CLI smoke tests for agent-foundry.
#
# Uses an isolated HOME so real provider installs are not touched.
# Requires: agent-foundry on PATH (or AGENT_FOUNDRY_BIN), git, network for remote repo tests.
#
# Usage:
#   ./scripts/e2e-cli.sh
#   USE_LOCAL_SOURCE=1 ./scripts/e2e-cli.sh   # test checkout without reinstalling pipx
#   ./scripts/e2e-cli.sh --skip-network       # local fixture + registry only
#   ./scripts/e2e-cli.sh --keep-temp          # leave temp dirs for inspection

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXTERNAL_REPO_URL="${EXTERNAL_REPO_URL:-https://github.com/mattpocock/skills.git}"
LOCAL_FIXTURE="${REPO_ROOT}/tests/fixtures/external-repo"
if [[ "${USE_LOCAL_SOURCE:-0}" == "1" ]]; then
  AGENT_FOUNDRY="${AGENT_FOUNDRY_BIN:-${REPO_ROOT}/scripts/run-local-cli.sh}"
else
  AGENT_FOUNDRY="${AGENT_FOUNDRY_BIN:-agent-foundry}"
fi

SKIP_NETWORK=0
KEEP_TEMP=0
for arg in "$@"; do
  case "$arg" in
    --skip-network) SKIP_NETWORK=1 ;;
    --keep-temp) KEEP_TEMP=1 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

PASS=0
FAIL=0
CURRENT=""

pass() {
  PASS=$((PASS + 1))
  printf '  \033[32mPASS\033[0m %s\n' "$1"
}

fail() {
  FAIL=$((FAIL + 1))
  printf '  \033[31mFAIL\033[0m %s\n' "$1"
  if [[ -n "${2:-}" ]]; then
    printf '        %s\n' "$2"
  fi
}

section() {
  CURRENT="$1"
  printf '\n== %s ==\n' "$1"
}

run_expect_ok() {
  local label="$1"
  shift
  local out
  if out="$("$@" 2>&1)"; then
    pass "$label"
    return 0
  fi
  fail "$label" "exit $?; output: ${out//$'\n'/ | }"
  return 1
}

run_expect_fail() {
  local label="$1"
  local expected_code="$2"
  shift 2
  local code=0
  local out
  out="$("$@" 2>&1)" || code=$?
  if [[ "$code" -eq "$expected_code" ]]; then
    pass "$label (exit $code)"
    return 0
  fi
  fail "$label" "expected exit $expected_code, got $code; output: ${out//$'\n'/ | }"
  return 1
}

assert_path_exists() {
  local label="$1"
  local path="$2"
  if [[ -e "$path" ]]; then
    pass "$label"
  else
    fail "$label" "missing: $path"
    return 1
  fi
}

assert_path_missing() {
  local label="$1"
  local path="$2"
  if [[ ! -e "$path" ]]; then
    pass "$label"
  else
    fail "$label" "still exists: $path"
    return 1
  fi
}

cleanup() {
  if [[ "$KEEP_TEMP" -eq 1 ]]; then
    printf '\nTemp HOME kept at: %s\n' "$E2E_HOME"
    printf 'Project dir kept at: %s\n' "$PROJECT_DIR"
    return
  fi
  rm -rf "$E2E_HOME" "$PROJECT_DIR"
}
trap cleanup EXIT

# --- setup ---
section "Prerequisites"
command -v "$AGENT_FOUNDRY" >/dev/null || {
  echo "agent-foundry not found. Install it or set AGENT_FOUNDRY_BIN." >&2
  exit 2
}
command -v git >/dev/null || {
  echo "git is required for remote --repo tests." >&2
  exit 2
}
pass "agent-foundry: $(command -v "$AGENT_FOUNDRY")"
pass "git: $(command -v git)"

E2E_HOME="$(mktemp -d "${TMPDIR:-/tmp}/agent-foundry-e2e-home.XXXXXX")"
PROJECT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/agent-foundry-e2e-project.XXXXXX")"
export HOME="$E2E_HOME"

section "Help / parser smoke"
run_expect_ok "main --help" "$AGENT_FOUNDRY" --help
run_expect_ok "install --help" "$AGENT_FOUNDRY" install --help
run_expect_ok "install-plugin --help" "$AGENT_FOUNDRY" install-plugin --help

section "Registry: validate-plugins"
(
  cd "$REPO_ROOT"
  run_expect_ok "validate-plugins" "$AGENT_FOUNDRY" validate-plugins
)

section "Registry: install-plugin + uninstall-plugin (cursor-cli, git)"
run_expect_ok "install-plugin cursor-cli git" \
  "$AGENT_FOUNDRY" install-plugin cursor-cli git --repo "$REPO_ROOT"
assert_path_exists "cursor skill commit installed" "$HOME/.cursor/skills/commit/SKILL.md"
run_expect_ok "uninstall-plugin cursor-cli git" \
  "$AGENT_FOUNDRY" uninstall-plugin cursor-cli git --repo "$REPO_ROOT"
assert_path_missing "cursor skill commit removed" "$HOME/.cursor/skills/commit/SKILL.md"

section "Registry: install skill (scoped) + uninstall"
run_expect_ok "install skill cursor-cli git:commit" \
  "$AGENT_FOUNDRY" install skill cursor-cli git:commit --repo "$REPO_ROOT"
assert_path_exists "scoped skill commit installed" "$HOME/.cursor/skills/commit/SKILL.md"
run_expect_ok "uninstall skill cursor-cli commit" \
  "$AGENT_FOUNDRY" uninstall skill cursor-cli commit
assert_path_missing "scoped skill commit uninstalled" "$HOME/.cursor/skills/commit/SKILL.md"

section "Local external fixture: --path skills override"
run_expect_ok "install skill codex commit (alt-skills)" \
  "$AGENT_FOUNDRY" install skill codex commit \
  --repo "$LOCAL_FIXTURE" \
  --path "skills:./alt-skills"
assert_path_exists "alt-skills commit installed (codex)" \
  "$HOME/.codex/plugins/specific-skill-external-commit/skills/commit/SKILL.md"
run_expect_ok "uninstall skill codex commit (fixture)" \
  "$AGENT_FOUNDRY" uninstall skill codex commit
assert_path_missing "alt-skills commit removed (codex)" \
  "$HOME/.codex/plugins/specific-skill-external-commit"

section "Local external fixture: scoped plugin skill"
run_expect_ok "install skill cursor-cli my-plugin:plugin-skill" \
  "$AGENT_FOUNDRY" install skill cursor-cli my-plugin:plugin-skill \
  --repo "$LOCAL_FIXTURE"
assert_path_exists "plugin skill installed" "$HOME/.cursor/skills/plugin-skill/SKILL.md"
run_expect_ok "uninstall skill cursor-cli my-plugin:plugin-skill" \
  "$AGENT_FOUNDRY" uninstall skill cursor-cli my-plugin:plugin-skill
assert_path_missing "plugin skill removed" "$HOME/.cursor/skills/plugin-skill/SKILL.md"

section "Local external fixture: agent install"
run_expect_ok "install agent cursor-cli senior-reviewer" \
  "$AGENT_FOUNDRY" install agent cursor-cli senior-reviewer \
  --repo "$LOCAL_FIXTURE"
assert_path_exists "agent installed" "$HOME/.cursor/agents/senior-reviewer.md"
run_expect_ok "uninstall agent cursor-cli senior-reviewer" \
  "$AGENT_FOUNDRY" uninstall agent cursor-cli senior-reviewer
assert_path_missing "agent removed" "$HOME/.cursor/agents/senior-reviewer.md"

if [[ "$SKIP_NETWORK" -eq 1 ]]; then
  section "Remote mattpocock/skills (skipped)"
  pass "--skip-network set"
else
  section "Remote mattpocock/skills: engineering path (codex)"
  run_expect_ok "install skill codex tdd (--path engineering)" \
    "$AGENT_FOUNDRY" install skill codex tdd \
    --repo "$EXTERNAL_REPO_URL" \
    --path "skills:./skills/engineering"
  assert_path_exists "codex tdd plugin" \
    "$HOME/.codex/plugins/specific-skill-external-tdd/skills/tdd/SKILL.md"
  run_expect_ok "uninstall skill codex tdd (no --repo/--path)" \
    "$AGENT_FOUNDRY" uninstall skill codex tdd
  assert_path_missing "codex tdd plugin removed" \
    "$HOME/.codex/plugins/specific-skill-external-tdd"

  section "Remote mattpocock/skills: productivity path (cursor-cli)"
  run_expect_ok "install skill cursor-cli handoff (--path productivity)" \
    "$AGENT_FOUNDRY" install skill cursor-cli handoff \
    --repo "$EXTERNAL_REPO_URL" \
    --path "skills:./skills/productivity"
  assert_path_exists "cursor handoff skill" "$HOME/.cursor/skills/handoff/SKILL.md"
  run_expect_ok "uninstall skill cursor-cli handoff" \
    "$AGENT_FOUNDRY" uninstall skill cursor-cli handoff
  assert_path_missing "cursor handoff removed" "$HOME/.cursor/skills/handoff/SKILL.md"

  section "Remote mattpocock/skills: negative cases"
  run_expect_fail "tdd without --path fails" 1 \
    "$AGENT_FOUNDRY" install skill codex tdd --repo "$EXTERNAL_REPO_URL"
  run_expect_fail "unknown skill fails" 1 \
    "$AGENT_FOUNDRY" install skill codex not-a-real-skill \
    --repo "$EXTERNAL_REPO_URL" \
    --path "skills:./skills/engineering"
  run_expect_fail "bad --path on install-plugin fails" 2 \
    "$AGENT_FOUNDRY" install-plugin cursor-cli git \
    --repo "$REPO_ROOT" \
    --path "skills:./does-not-exist"
fi

section "In-project scope (--in-project)"
(
  cd "$PROJECT_DIR"
  run_expect_ok "install skill cursor-cli plugin-skill in project" \
    "$AGENT_FOUNDRY" install skill cursor-cli my-plugin:plugin-skill \
    --repo "$LOCAL_FIXTURE" \
    --in-project
  assert_path_exists "in-project skill" "$PROJECT_DIR/.cursor/skills/plugin-skill/SKILL.md"
  run_expect_ok "uninstall skill cursor-cli my-plugin:plugin-skill in project" \
    "$AGENT_FOUNDRY" uninstall skill cursor-cli my-plugin:plugin-skill --in-project
  assert_path_missing "in-project skill removed" "$PROJECT_DIR/.cursor/skills/plugin-skill/SKILL.md"
)

section "Summary"
TOTAL=$((PASS + FAIL))
printf '\nResults: %d passed, %d failed (%d checks)\n' "$PASS" "$FAIL" "$TOTAL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
