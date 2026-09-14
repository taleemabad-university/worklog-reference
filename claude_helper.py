"""
claude_helper.py — talk to Claude from your code, using YOUR Claude subscription.

No API key. No billing setup. It shells out to the `claude` CLI you already
signed into for the course, in headless mode (`claude -p`).

    from claude_helper import ask, ask_json

    text  = ask("Write one sentence about teaching.")
    items = ask_json("List 2 fruits as JSON array of objects with a 'name' key.")

Requires: Python 3.8+, and `claude` on your PATH (you already have it).
Uses only the Python standard library — nothing to pip install.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time

import config  # noqa: F401  - reads your .env into os.environ on import

__all__ = ["ask", "ask_json", "ClaudeError", "cli_path"]

# Tools Claude must never use for a plain text/JSON generation call.
# Your cron job should reason about text, not touch the filesystem or network.
_BLOCKED_TOOLS = (
    "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,"
    "NotebookEdit,Task,MultiEdit,TodoWrite"
)

_DEFAULT_MODEL = os.environ.get("CLAUDE_HELPER_MODEL", "haiku")
_DEFAULT_TIMEOUT = int(os.environ.get("CLAUDE_HELPER_TIMEOUT", "120"))


class ClaudeError(RuntimeError):
    """Raised when Claude could not be reached or did not return usable output."""


def cli_path() -> str:
    """Find the `claude` executable. Handles .exe/.cmd on Windows."""
    found = shutil.which("claude") or shutil.which("claude.exe")
    if not found:
        raise ClaudeError(
            "The `claude` command was not found on your PATH.\n"
            "Open a terminal and run:  claude --version\n"
            "If that fails, reinstall Claude Code and reopen your terminal."
        )
    return found


def _workdir() -> str:
    """A stable scratch folder to run Claude in.

    Why not a fresh temp folder per call: on Windows the claude CLI keeps a
    handle on its working directory, so deleting it straight after the call
    raises WinError 32 ("being used by another process") and crashes your job.
    We found that the hard way. One reused folder avoids it completely.
    """
    path = os.path.join(tempfile.gettempdir(), "claude_helper_work")
    os.makedirs(path, exist_ok=True)
    return path


def ask(
    prompt: str,
    *,
    model: str = _DEFAULT_MODEL,
    timeout: int = _DEFAULT_TIMEOUT,
    retries: int = 2,
    mcp_config: str = "",
    allow_tools: str = "",
) -> str:
    """Send `prompt` to Claude and return its reply as plain text.

    mcp_config : path to a .mcp.json file. Gives Claude your MCP servers - for
                 example the Notion one, so it can write records straight into
                 your own Notion. We pass the path explicitly rather than
                 relying on the current folder, which is what lets this work
                 from the clean scratch folder.
    allow_tools: comma-separated tools to permit, e.g. "mcp__notion". You MUST
                 pass this when using MCP, otherwise every tool stays blocked
                 and Claude will politely tell you it cannot do anything.

    Raises ClaudeError if Claude cannot be reached or keeps failing.
    """
    if not prompt or not prompt.strip():
        raise ClaudeError("Empty prompt. Give Claude something to read.")

    exe = cli_path()
    cmd = [
        exe,
        "-p",
        "--output-format", "json",
        "--model", model,
    ]
    if mcp_config:
        if not os.path.exists(mcp_config):
            raise ClaudeError(
                f"MCP config not found: {mcp_config}. "
                "Copy .mcp.json.example to .mcp.json and put your token in it."
            )
        cmd += ["--mcp-config", os.path.abspath(mcp_config)]
    if allow_tools:
        cmd += ["--allowed-tools", allow_tools]
    else:
        cmd += ["--disallowed-tools", _BLOCKED_TOOLS]

    # Run in an empty scratch directory. If you run Claude inside your project
    # folder it silently loads that project's CLAUDE.md and context, which makes
    # replies slower, dearer, and sometimes wrong. This keeps every call clean.
    last_error = ""
    workdir = _workdir()
    for attempt in range(retries + 1):
        try:
            proc = subprocess.run(
                cmd,
                input=prompt,              # prompt goes in on stdin — no shell escaping
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                cwd=workdir,
            )
        except subprocess.TimeoutExpired:
            last_error = f"Claude did not answer within {timeout}s."
            _backoff(attempt, retries)
            continue
        except OSError as exc:
            raise ClaudeError(f"Could not start the claude CLI: {exc}") from exc

        if proc.returncode != 0:
            # stderr carries warnings AND errors; keep it short for humans.
            detail = (proc.stderr or "").strip().splitlines()
            last_error = detail[-1] if detail else f"exit code {proc.returncode}"
            _backoff(attempt, retries)
            continue

        # stdout is the JSON envelope. Warnings go to stderr, so stdout is clean.
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            last_error = "Claude returned something that was not JSON."
            _backoff(attempt, retries)
            continue

        if envelope.get("is_error"):
            last_error = str(envelope.get("result") or "Claude reported an error.")
            _backoff(attempt, retries)
            continue

        result = envelope.get("result")
        if not isinstance(result, str) or not result.strip():
            last_error = "Claude returned an empty reply."
            _backoff(attempt, retries)
            continue

        return result.strip()

    raise ClaudeError(f"Claude failed after {retries + 1} attempt(s). Last problem: {last_error}")


def ask_json(
    prompt: str,
    *,
    model: str = _DEFAULT_MODEL,
    timeout: int = _DEFAULT_TIMEOUT,
    retries: int = 2,
    mcp_config: str = "",
    allow_tools: str = "",
):
    """Like ask(), but insists on valid JSON and returns the parsed object.

    Claude sometimes wraps JSON in ```json fences or adds a sentence before it.
    This strips that and, if the JSON is still broken, asks again.
    """
    instruction = (
        "\n\nReturn ONLY valid JSON. No explanation, no commentary, "
        "no markdown code fences. Start your reply with { or [."
    )

    last_error = ""
    for attempt in range(retries + 1):
        raw = ask(prompt + instruction, model=model, timeout=timeout, retries=0,
                  mcp_config=mcp_config, allow_tools=allow_tools)
        cleaned = _strip_fences(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            last_error = f"{exc}  (Claude said: {cleaned[:200]!r})"
            _backoff(attempt, retries)

    raise ClaudeError(f"Claude did not return valid JSON. Last problem: {last_error}")


def _strip_fences(text: str) -> str:
    """Remove ```json fences and any prose before the first { or [."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t[3:]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
        t = t.strip()
        if t.lower().startswith("json"):
            t = t[4:].strip()
    starts = [i for i in (t.find("{"), t.find("[")) if i != -1]
    if starts:
        first = min(starts)
        closer = "}" if t[first] == "{" else "]"
        last = t.rfind(closer)
        if last > first:
            t = t[first:last + 1]
    return t.strip()


def _backoff(attempt: int, retries: int) -> None:
    if attempt < retries:
        time.sleep(2 ** attempt)


if __name__ == "__main__":
    # Self-test: run `python claude_helper.py` to check your setup works.
    print("claude CLI:", cli_path())
    print("plain text:", ask("Reply with exactly: HELLO"))
    print("json      :", ask_json('Return {"ok": true} and nothing else.'))
    print("\nAll good. You can import ask() and ask_json() in your own code.")
