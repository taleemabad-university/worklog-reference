"""
preflight.py - one command that answers "am I OK?"

    python preflight.py              # check everything
    python preflight.py --quick      # skip the slow Claude round-trip
    python preflight.py --step 4     # only what Step 4 needs

Every red line tells you the exact thing to type next. If a fix is not
obvious, put your hand up - a red light here is information, not a failure.

It also installs a real git hook that stops you committing secrets from ANY
git client, not just from Claude Code.

Uses only the Python standard library.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

import config  # noqa: F401  - reads your .env into os.environ on import

HERE = os.path.dirname(os.path.abspath(__file__))

OK, WARN, BAD = "ok", "warn", "bad"

# Which step each check belongs to, so --step N can filter.
results: list[tuple[str, int, str, str, str]] = []   # (state, step, label, detail, fix)


def record(state: str, step: int, label: str, detail: str = "", fix: str = "") -> None:
    results.append((state, step, label, detail, fix))


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    """Run a command, return (exit code, combined output). Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
    except FileNotFoundError:
        return 127, "not found"
    except Exception as exc:                        # noqa: BLE001
        return 1, str(exc)


# ─────────────────────────────────────────────────────────────────────────────
# The checks
# ─────────────────────────────────────────────────────────────────────────────

def check_shell() -> None:
    if os.name != "nt":
        record(OK, 0, "Shell", "macOS/Linux terminal")
        return
    # On Windows every command in the brief assumes Git Bash.
    if os.environ.get("MSYSTEM") or "bash" in os.environ.get("SHELL", "").lower():
        record(OK, 0, "Shell", "Git Bash")
    else:
        record(WARN, 0, "Shell", "this does not look like Git Bash",
               "Press Start, type 'Git Bash', open it, and run this again "
               "from there.\n               Commands in the brief are written "
               "for Git Bash, not PowerShell.")


def check_python() -> None:
    v = sys.version_info
    if v >= (3, 8):
        record(OK, 0, "Python", f"{v.major}.{v.minor}.{v.micro}")
    else:
        record(BAD, 0, "Python", f"{v.major}.{v.minor} is too old",
               "install Python 3.8 or newer from python.org")


def check_claude() -> None:
    exe = shutil.which("claude") or shutil.which("claude.exe")
    if not exe:
        record(BAD, 0, "claude CLI", "not on your PATH",
               "close this terminal completely, open a new one, then:  "
               "claude --version")
        return
    code, out = run([exe, "--version"])
    record(OK if code == 0 else BAD, 0, "claude CLI",
           out.splitlines()[0] if out else "", "" if code == 0 else "claude --version")


def check_claude_answers(quick: bool) -> None:
    if quick:
        record(WARN, 0, "Claude answers", "skipped (--quick)")
        return
    try:
        from claude_helper import ask, ClaudeError
    except Exception as exc:                        # noqa: BLE001
        record(BAD, 0, "Claude answers", f"could not import claude_helper: {exc}",
               "make sure you are in the folder that has claude_helper.py in it")
        return
    try:
        reply = ask("Reply with exactly: HELLO", timeout=90, retries=1)
        record(OK if "HELLO" in reply.upper() else WARN, 0, "Claude answers",
               reply[:40])
    except ClaudeError as exc:
        record(BAD, 0, "Claude answers", str(exc).splitlines()[0],
               "python claude_helper.py     (to see the full error)")


def check_skill_file() -> None:
    path = os.path.join(HERE, ".claude", "skills", "worklog", "SKILL.md")
    if not os.path.exists(path):
        record(BAD, 5, "Skill file", "missing",
               "it must be at exactly  .claude/skills/worklog/SKILL.md")
        return
    text = open(path, encoding="utf-8", errors="replace").read()
    if not text.lstrip().startswith("---"):
        record(WARN, 5, "Skill file", "the ---name: worklog--- block at the top is gone",
               "put the front-matter block back, or run_once.py may drop your "
               "whole file")
        return
    # Has it actually been made theirs? A pure starter file scores 0 on harness.
    starter_len = 4630        # the shipped starter, measured
    record(OK if len(text) > starter_len + 200 else WARN, 5, "Skill file",
           f"{len(text)} chars"
           + ("" if len(text) > starter_len + 200 else "  - still looks like the starter"),
           "" if len(text) > starter_len + 200 else
           "open .claude/skills/worklog/SKILL.md and make the rules yours - "
           "this is most of your mark")


def check_lock_intact() -> None:
    path = os.path.join(HERE, "run_once.py")
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        record(BAD, 7, "Job lock", "run_once.py not found", "")
        return
    record(OK if "acquire_lock" in text else BAD, 7, "Job lock",
           "present" if "acquire_lock" in text else "deleted",
           "" if "acquire_lock" in text else
           "put acquire_lock() back - without it, overlapping runs duplicate "
           "everything and it looks exactly like broken de-duplication")


def check_gitignore() -> None:
    path = os.path.join(HERE, ".gitignore")
    if not os.path.exists(path):
        record(BAD, 3, ".gitignore", "missing",
               "create it BEFORE your first commit and put .env in it")
        return
    text = open(path, encoding="utf-8", errors="replace").read()
    missing = [p for p in (".env", ".mcp.json") if not re.search(rf"^{re.escape(p)}\s*$",
                                                                text, re.M)]
    record(OK if not missing else BAD, 3, ".gitignore",
           "covers .env and .mcp.json" if not missing else f"missing: {', '.join(missing)}",
           "" if not missing else
           "add these lines to .gitignore, each on its own line:\n               "
           + "\n               ".join(missing))


def check_git_ignoring_for_real() -> None:
    """The .gitignore file existing is not proof. Ask git."""
    if not os.path.isdir(os.path.join(HERE, ".git")):
        record(WARN, 3, "Git repo", "not created yet (that is Step 3)",
               "git init")
        return
    leaked = []
    for f in (".env", ".mcp.json"):
        code, _ = run(["git", "-C", HERE, "check-ignore", "-q", f])
        if code != 0:
            leaked.append(f)
    record(OK if not leaked else BAD, 3, "Git really ignores secrets",
           "yes" if not leaked else f"NO - {', '.join(leaked)} would be committed",
           "" if not leaked else
           "fix .gitignore, then:  git rm --cached " + " ".join(leaked))

    code, out = run(["git", "-C", HERE, "config", "user.email"])
    record(OK if out.strip() else WARN, 3, "Git identity",
           out.strip() or "not set",
           "" if out.strip() else
           'git config --global user.email "you@taleemabad.com"')


def check_gh() -> None:
    if not shutil.which("gh"):
        record(BAD, 3, "GitHub CLI", "not installed", "install gh, then:  gh auth login")
        return
    code, out = run(["gh", "auth", "status"])
    if code != 0:
        record(BAD, 3, "GitHub login", "not logged in", "gh auth login")
        return
    who = ""
    c2, o2 = run(["gh", "api", "user", "--jq", ".login"])
    if c2 == 0:
        who = o2.strip()
    record(OK, 3, "GitHub login", who or "logged in")


def check_collaborator() -> None:
    if not shutil.which("gh") or not os.path.isdir(os.path.join(HERE, ".git")):
        return
    code, out = run(["git", "-C", HERE, "remote", "get-url", "origin"])
    if code != 0:
        record(WARN, 3, "Collaborator", "no GitHub repo yet (Step 3)",
               "gh repo create my-work-log --private --source=. --push")
        return
    m = re.search(r"github\.com[:/]([^/]+)/([^/.\s]+)", out)
    if not m:
        return
    owner, repo = m.group(1), m.group(2)
    c2, o2 = run(["gh", "api", f"repos/{owner}/{repo}/collaborators", "--jq", ".[].login"])
    ok = "taleemabad-university" in o2
    record(OK if ok else BAD, 3, "Collaborator",
           "taleemabad-university added" if ok else "taleemabad-university NOT added",
           "" if ok else
           f"gh api -X PUT repos/{owner}/{repo}/collaborators/taleemabad-university "
           "-f permission=push")


def check_railway() -> None:
    if not shutil.which("railway"):
        record(BAD, 4, "Railway CLI", "not installed", "install the Railway CLI")
        return
    code, out = run(["railway", "whoami"])
    record(OK if code == 0 else BAD, 4, "Railway login",
           out.splitlines()[0][:50] if code == 0 else "not logged in",
           "" if code == 0 else "railway login")


def check_live_page() -> None:
    url = (os.environ.get("SYNC_URL") or os.environ.get("DEPLOY_URL") or "").strip()
    if not url:
        record(WARN, 4, "Live page", "SYNC_URL not set in .env yet",
               "after  railway up  , put your public URL in .env as\n"
               "               SYNC_URL=https://your-app.up.railway.app")
        return
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/health", timeout=15) as r:
            code = r.status
    except urllib.error.HTTPError as exc:
        code = exc.code
    except Exception as exc:                        # noqa: BLE001
        record(BAD, 4, "Live page", f"could not reach it: {exc}",
               "railway logs        (to see why it is not up)")
        return
    record(OK if code == 200 else BAD, 4, "Live page", f"{url} -> HTTP {code}",
           "" if code == 200 else "railway logs")


def check_sync_token() -> None:
    token = os.environ.get("SYNC_TOKEN", "").strip()
    record(OK if token else WARN, 4, "Sync token",
           "set" if token else "not set - your live page will stay empty",
           "" if token else
           "pick any long random string, then put the SAME value in both:\n"
           "               .env       SYNC_TOKEN=your-secret\n"
           "               Railway    railway variables --set SYNC_TOKEN=your-secret")


def check_records() -> None:
    path = os.path.join(HERE, "records.json")
    if not os.path.exists(path):
        record(WARN, 7, "records.json", "none yet",
               "python run_once.py --demo")
        return
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:                               # noqa: BLE001
        record(BAD, 7, "records.json", "not valid JSON",
               "delete it and run again:  rm records.json && python run_once.py --drop")
        return
    record(OK if isinstance(data, list) else BAD, 7, "records.json",
           f"{len(data)} record(s)" if isinstance(data, list) else "not a list",
           "" if isinstance(data, list) else "rm records.json")


def check_readme() -> None:
    path = os.path.join(HERE, "README.md")
    if not os.path.exists(path):
        record(BAD, 11, "README", "missing - this is a gate",
               "cp README.template.md README.md   then make every line true")
        return
    text = open(path, encoding="utf-8", errors="replace").read()

    # If you forked the reference repo, its README is still sitting here.
    # It describes OUR build, not yours, so it would sail past the blanks
    # check below and show green on a gate you have not actually done.
    if "reference build for Final Build Day" in text:
        record(BAD, 11, "README", "this is still the reference README, not yours",
               "cp README.template.md README.md   then make every line true")
        return

    todo = len(re.findall(r"\bTODO\b|\bFILL THIS IN\b|_{4,}", text))
    record(OK if todo == 0 else WARN, 11, "README",
           f"{len(text)} chars" + ("" if todo == 0 else f", {todo} blank(s) left"),
           "" if todo == 0 else "finish the blanks - one false claim fails the "
           "whole submission")


def check_evals() -> None:
    path = os.path.join(HERE, "evals", "results.md")
    if not os.path.exists(path):
        record(BAD, 10, "Evals", "evals/results.md missing - this is a gate",
               "cp evals/results.template.md evals/results.md")
        return
    text = open(path, encoding="utf-8", errors="replace").read()
    passes = len(re.findall(r"\bPASS\b", text))
    fails = len(re.findall(r"\bFAIL\b", text))
    pending = len(re.findall(r"\bPENDING\b", text))
    if pending or (passes + fails) < 5:
        record(BAD, 10, "Evals",
               f"PASS {passes} / FAIL {fails} / PENDING {pending}",
               "you need at least 5 real cases and at least one honest FAIL. "
               "PENDING counts as nothing.")
    elif fails == 0:
        record(WARN, 10, "Evals", f"PASS {passes} / FAIL {fails}",
               "everything passing means your cases are too easy - an assessor "
               "will pick a harder one live")
    else:
        record(OK, 10, "Evals", f"PASS {passes} / FAIL {fails}")


# The git hook we install. Note it TESTS each interpreter instead of just
# locating one: on Windows `command -v python` happily finds the Microsoft
# Store stub, which is not Python and exits with an error. Finding it is not
# the same as it working, and a secret check that silently never runs is worse
# than no check at all - you would believe you were covered.
PRE_COMMIT_HOOK = r"""#!/bin/sh
# Installed by preflight.py - blocks secrets from ANY git client,
# including the VS Code sidebar and your own terminal.
EXE=""
for C in python3 python py; do
  if "$C" -c "import sys" >/dev/null 2>&1; then EXE="$C"; break; fi
done
if [ -z "$EXE" ]; then
  echo "pre-commit: could not find a working Python, so the secret check" >&2
  echo "could not run. This commit is blocked on purpose." >&2
  echo "TYPE THIS:  python --version" >&2
  exit 1
fi
echo '{"tool_input":{"command":"git commit"}}' | "$EXE" .claude/hooks/block-env-commit.py || exit 1
"""


def install_git_hook() -> None:
    """Install a real pre-commit hook, so secrets are blocked no matter which
    git client you use - VS Code's sidebar, GitHub Desktop, or your terminal."""
    git_dir = os.path.join(HERE, ".git")
    if not os.path.isdir(git_dir):
        return
    hook_path = os.path.join(git_dir, "hooks", "pre-commit")
    marker = "block-env-commit"
    if os.path.exists(hook_path) and marker in open(hook_path, encoding="utf-8",
                                                    errors="replace").read():
        record(OK, 9, "Git pre-commit hook", "installed")
        return
    os.makedirs(os.path.dirname(hook_path), exist_ok=True)
    with open(hook_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(PRE_COMMIT_HOOK)
    try:
        os.chmod(hook_path, 0o755)
    except OSError:
        pass
    record(OK, 9, "Git pre-commit hook", "installed just now")


# ─────────────────────────────────────────────────────────────────────────────

GATES = [
    ("1 Runs by itself",   lambda s: s.get("Job lock") == OK),
    ("2 On GitHub",        lambda s: s.get("Collaborator") == OK),
    ("3 Deployed",         lambda s: s.get("Live page") == OK),
    ("4 Skill file real",  lambda s: s.get("Skill file") == OK),
    ("5 MCP works",        lambda s: os.path.exists(os.path.join(HERE, ".mcp.json"))),
    ("6 A hook fires",     lambda s: s.get("Git pre-commit hook") == OK),
    ("7 README is true",   lambda s: s.get("README") == OK),
    ("8 Evals recorded",   lambda s: s.get("Evals") == OK),
]


def main() -> int:
    args = sys.argv[1:]
    quick = "--quick" in args
    only_step = None
    if "--step" in args:
        try:
            only_step = int(args[args.index("--step") + 1])
        except (IndexError, ValueError):
            print("--step needs a number, e.g. --step 4")
            return 1

    check_shell()
    check_python()
    check_claude()
    check_claude_answers(quick)
    check_skill_file()
    check_lock_intact()
    check_gitignore()
    check_git_ignoring_for_real()
    install_git_hook()
    check_gh()
    check_collaborator()
    check_railway()
    check_sync_token()
    check_live_page()
    check_records()
    check_readme()
    check_evals()

    shown = [r for r in results if only_step is None or r[1] == only_step]

    print()
    print("  PREFLIGHT" + (f" - step {only_step} only" if only_step is not None else ""))
    print("  " + "-" * 66)
    mark = {OK: "[OK]  ", WARN: "[!]   ", BAD: "[X]   "}
    for state, step, label, detail, fix in shown:
        print(f"  {mark[state]}{label:<26} {detail}")
        if fix and state != OK:
            for i, line in enumerate(fix.split("\n")):
                print(f"           {'-> ' if i == 0 else ''}{line}")
    print("  " + "-" * 66)

    greens = sum(1 for r in shown if r[0] == OK)
    reds = [r[2] for r in shown if r[0] == BAD]
    print(f"  {greens} of {len(shown)} green.")

    if only_step is None:
        state = {label: st for st, _, label, _, _ in results}
        got = [name for name, test in GATES if test(state)]
        print(f"  GATES: {len(got)} of 8 checkable here are green.")
        print("         (gate 9, your three questions, is asked in the room.)")

    if reds:
        print()
        print("  Fix these, in this order:")
        for r in reds:
            print(f"    - {r}")
        print()
        print("  If a fix does not work, put your hand up. A red light is")
        print("  information, not a failure.")
    else:
        print("  Nothing is blocking you. Go.")
    print()
    return 1 if reds else 0


if __name__ == "__main__":
    raise SystemExit(main())
