#!/usr/bin/env python3
"""
block-env-commit.py - stop Claude committing your secrets.

Wired up in .claude/settings.json as a PreToolUse hook on Bash.
Before ANY bash command runs, this looks at it. If it is a git commit and a
secret is staged, it exits 2 - which tells Claude Code to refuse the command
and show the message.

It checks TWO things, because secrets arrive two ways:

  1. FILENAMES  - .env, .mcp.json (your Notion token!), *.pem, *.key
  2. CONTENT    - a token pasted straight into a .py file. Your cohort audit
                  said this was the number one problem, and a filename check
                  alone never catches it.

Why this exists: a password that reaches GitHub is not fixed by deleting the
file afterwards - the commit history keeps it. The only reliable fix is to
never let it in.

WHAT THIS DOES NOT COVER - read this, it matters:
    This is a Claude Code hook. It fires when CLAUDE runs a git commit.
    It does NOT fire when you commit from the VS Code sidebar, from GitHub
    Desktop, or by typing git commit in your own terminal.
    Run  python preflight.py  and it will install a real git hook that does
    cover those. Until then: commit through Claude Code.

Test it:
    echo "NOT_A_REAL_SECRET=test" > .env
    git add -f .env
    # then ask Claude to commit. It will be refused.
    git restore --staged .env
"""

import json
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# 1. Files that must never reach a commit.
# ---------------------------------------------------------------------------
DANGEROUS_PATH = re.compile(
    r"(^|/)("
    # .env and .env.local and .env.production - but NOT .env.example and
    # friends, which are templates with no real values in them and MUST be
    # committed. Without this exception the hook blocks the very first commit
    # every learner makes, which teaches them the check is noise.
    r"\.env(\.(?!example$|sample$|template$)[^/]*)?$"
    r"|\.mcp\.json$"            # your Notion token lives here
    r"|.*\.pem$"
    r"|.*\.key$"
    r"|credentials\.json$"
    r"|service_account.*\.json$"
    r")"
)

# ---------------------------------------------------------------------------
# 2. Secrets pasted INSIDE a file. Each pattern is a real token shape.
# ---------------------------------------------------------------------------
DANGEROUS_CONTENT = [
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),      "an Anthropic API key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}"),          "a GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),  "a GitHub token"),
    (re.compile(r"\bntn_[A-Za-z0-9]{20,}"),          "a Notion token"),
    (re.compile(r"\bsecret_[A-Za-z0-9]{32,}"),       "a Notion token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"), "a Slack token"),
    (re.compile(r"OPENAPI_MCP_HEADERS.*Bearer\s+\S+"), "a token in an MCP header"),
]

# Fake values used by the Step 9 test, and the placeholder in .mcp.json.example.
# Without this the hook cries wolf on its own teaching examples.
ALLOWED = re.compile(r"NOT_A_REAL_SECRET|YOUR_NOTION_TOKEN|hunter2|paste-your-token-here")


def _git(*args: str) -> str:
    """Run a git command and return stdout. Never raises - a broken git must
    not break the session."""
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True,
            timeout=10, encoding="utf-8", errors="replace",
        )
        return out.stdout or ""
    except Exception:
        return ""


def staged_files() -> list[str]:
    return [ln.strip() for ln in _git("diff", "--cached", "--name-only").splitlines() if ln.strip()]


def staged_secrets() -> list[str]:
    """Look inside what is being committed, not just at the filenames."""
    diff = _git("diff", "--cached", "-U0")
    found = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue                       # only added lines
        if ALLOWED.search(line):
            continue                       # our own test fixtures
        for pattern, label in DANGEROUS_CONTENT:
            if pattern.search(line):
                found.append(label)
                break
    return sorted(set(found))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                                   # never break the session

    command = (payload.get("tool_input") or {}).get("command", "")
    if "git commit" not in command:
        return 0

    bad_files = [f for f in staged_files() if DANGEROUS_PATH.search(f)]
    bad_content = staged_secrets()

    if not bad_files and not bad_content:
        return 0

    lines = ["BLOCKED: you are about to commit a secret.", ""]

    if bad_files:
        lines.append("These files must never be committed:")
        lines += [f"  - {f}" for f in bad_files]
        lines.append("")
        lines.append("TYPE THIS to take them out of the commit:")
        lines.append("    git restore --staged " + " ".join(bad_files))
        lines.append("")

    if bad_content:
        lines.append("A line you are committing looks like " + ", ".join(bad_content) + ".")
        lines.append("")
        lines.append("TYPE THIS to see it:")
        lines.append("    git diff --cached")
        lines.append("")
        lines.append("Move the value into .env and read it with os.environ instead.")
        lines.append("")

    lines.append("If this file has ALREADY been pushed at some point, change the")
    lines.append("password or regenerate the token as well - deleting the file does")
    lines.append("not remove it from the history.")
    lines.append("")
    lines.append("If you think this is wrong, put your hand up. Do not force it.")

    print("\n".join(lines), file=sys.stderr)
    return 2                                       # 2 = block the tool call


if __name__ == "__main__":
    sys.exit(main())
