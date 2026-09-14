"""
run_once.py — the job your cron runs. Boots, does one pass, exits.

    python run_once.py            # read the mailbox
    python run_once.py --demo     # read sample_transcript.txt instead (no email needed)

This file is the SKELETON. The two places marked YOUR WORK are what you are
being marked on. Everything else is plumbing we have already tested for you.

Run it by hand until it behaves, then let the cron run it every 5 minutes.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import date, datetime

import config  # noqa: F401  - reads your .env into os.environ on import
from claude_helper import ask_json, ClaudeError

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(HERE, ".claude", "skills", "worklog", "SKILL.md")

LOCK_PATH = os.path.join(HERE, ".job.lock")
LOCK_STALE_SECONDS = 600          # if a lock is older than this, assume a crash
STORE_PATH = os.path.join(HERE, "records.json")


# ─────────────────────────────────────────────────────────────────────────────
# The lock. Do not delete this.
#
# Your cron fires every 5 minutes. If one run takes longer than 5 minutes, the
# next one starts on top of it and you write the SAME transcript twice. You then
# spend the afternoon convinced your de-duplication prompt is broken when in fact
# it is fine. This lock is the fix.
# ─────────────────────────────────────────────────────────────────────────────

def acquire_lock() -> bool:
    if os.path.exists(LOCK_PATH):
        age = time.time() - os.path.getmtime(LOCK_PATH)
        if age < LOCK_STALE_SECONDS:
            print(f"Another run is still going ({int(age)}s old). Exiting quietly.")
            return False
        print(f"Found a stale lock ({int(age)}s old) - a previous run probably crashed. Taking over.")
    with open(LOCK_PATH, "w", encoding="utf-8") as fh:
        fh.write(str(os.getpid()))
    return True


def release_lock() -> None:
    try:
        os.remove(LOCK_PATH)
    except FileNotFoundError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Storage. A JSON file is fine to start. Swap it for your own Notion / Sheet /
# Airtable once the pipeline works end to end — not before.
# ─────────────────────────────────────────────────────────────────────────────

def load_records() -> list[dict]:
    if not os.path.exists(STORE_PATH):
        return []
    try:
        with open(STORE_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        print("records.json was unreadable; starting a fresh list.")
        return []

    # It must be a LIST of records. If someone hand-edited it into an object,
    # every loop below would crash with a confusing error a long way from here.
    if not isinstance(data, list):
        print("records.json is not a list of records; starting a fresh list.")
        return []
    return [r for r in data if isinstance(r, dict) and isinstance(r.get("title"), str)]


def save_records(records: list[dict]) -> None:
    tmp = STORE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, STORE_PATH)      # atomic: never leaves a half-written file


# ─────────────────────────────────────────────────────────────────────────────
# YOUR WORK #1 — the extraction prompt.
#
# This is most of your mark. Getting text back is easy; deciding correctly what
# is a task, who owns it, when it is due, and when you genuinely do not know —
# that is the job. Read the "Four decisions" section of the guide.
# ─────────────────────────────────────────────────────────────────────────────

def load_rules() -> str:
    """Read your extraction rules out of your skill file.

    THIS IS THE POINT OF A SKILL FILE. Open
    .claude/skills/worklog/SKILL.md, change a rule, save, run this job again -
    and the behaviour changes without you touching any Python.

    If the file is missing we fall back to a bare minimum so the job still runs,
    but you will score badly: the skill file is most of your mark.
    """
    try:
        text = open(SKILL_PATH, encoding="utf-8").read()
    except OSError:
        print(f"!! No skill file at {SKILL_PATH} - using bare fallback rules.")
        print("!! Write your skill file. It is Step 5 and it is worth real marks.")
        return ("Extract real work items as JSON objects with the fields: type "
                "(task|decision|blocker), title, owner, due, quote, confidence "
                "(high|low), ask.")

    # Strip the YAML front-matter - the model only needs the body.
    #
    # Careful: a plain "---" horizontal rule is also valid Markdown, and people
    # do start files with one. If we split blindly, someone whose file opens
    # with a rule loses their ENTIRE ruleset and never finds out - the job
    # still runs, it just quietly stops following their rules. So only strip a
    # block that actually looks like front-matter.
    if text.lstrip().startswith("---"):
        parts = text.lstrip().split("---", 2)
        if len(parts) == 3 and re.search(r"^\s*(name|description)\s*:", parts[1], re.M):
            text = parts[2]
        else:
            print("!! The top of your SKILL.md is not front-matter, so nothing was")
            print("!! stripped. If your rules look ignored, check that the file")
            print("!! starts with the ---name: worklog--- block.")
    return text.strip()


def extract_items(source_text: str, existing: list[dict]) -> list[dict]:
    open_titles = [r["title"] for r in existing if r.get("status") != "done"][:40]

    prompt = f"""Today is {date.today().isoformat()} ({date.today():%A}).

{load_rules()}

---

Items already open. Do NOT create a duplicate of these - if the conversation
refers to one of them, reuse its exact title:
{json.dumps(open_titles, ensure_ascii=False, indent=2)}

---

CONVERSATION:
{source_text}
"""
    return ask_json(prompt, timeout=180)


# ─────────────────────────────────────────────────────────────────────────────
# YOUR WORK #2 — validation. Never trust the model's shape.
#
# In our own testing the model was told "high" or "low" and returned "medium".
# If you write straight into Notion without checking, you get silent rubbish.
# ─────────────────────────────────────────────────────────────────────────────

def validate(items) -> list[dict]:
    if not isinstance(items, list):
        print("Model did not return a list. Skipping this batch.")
        return []

    clean, dropped = [], 0
    for it in items:
        if not isinstance(it, dict) or not it.get("title"):
            dropped += 1
            continue
        # The model is told to return a string title. It does not always.
        # merge() calls .strip() on this, so a list or a number here would
        # crash the whole run - check the TYPE, not just that it is truthy.
        if not isinstance(it["title"], str):
            dropped += 1
            continue
        if it.get("type") not in ("task", "decision", "blocker"):
            dropped += 1
            continue
        if it.get("confidence") not in ("high", "low"):
            it["confidence"] = "low"          # coerce, don't discard
        due = it.get("due")
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except (ValueError, TypeError):
                it["due"] = None
                it["ask"] = it.get("ask") or f"Could not read the date {due!r} - what is the real deadline?"
        it.setdefault("status", "open")
        it["captured_at"] = datetime.now().isoformat(timespec="seconds")
        clean.append(it)

    if dropped:
        print(f"Dropped {dropped} malformed item(s).")
    return clean


def merge(existing: list[dict], new: list[dict]) -> tuple[list[dict], int]:
    """Add only genuinely new items. Title match is the crude first pass —
    improve this, it is part of what you are marked on."""
    seen = {r["title"].strip().lower() for r in existing}
    added = 0
    for it in new:
        if it["title"].strip().lower() in seen:
            continue
        existing.append(it)
        seen.add(it["title"].strip().lower())
        added += 1
    return existing, added


DROP_DIR = os.path.join(HERE, "drop")
DONE_DIR = os.path.join(DROP_DIR, "done")


def _from_drop_folder() -> list[dict]:
    """Read every .txt file dropped into ./drop/, then move it to ./drop/done/.

    This is the fallback input. If your mailbox is not working yet, save a
    transcript as a .txt file in the drop folder and the job picks it up on its
    next run. Same pipeline, no email needed - so a mailbox problem never stops
    you building the part you are actually marked on.
    """
    os.makedirs(DONE_DIR, exist_ok=True)
    out = []
    for name in sorted(os.listdir(DROP_DIR)):
        path = os.path.join(DROP_DIR, name)
        if not name.lower().endswith(".txt") or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            out.append({"subject": name, "body": fh.read(), "_path": path})
    return out


def _archive_drop(src: dict) -> None:
    path = src.get("_path")
    if not path or not os.path.exists(path):
        return
    stamp = datetime.now().strftime("%H%M%S")
    os.replace(path, os.path.join(DONE_DIR, f"{stamp}_{os.path.basename(path)}"))


def get_sources(mode: str) -> list[dict]:
    if mode == "demo":
        path = os.path.join(HERE, "sample_transcript.txt")
        # errors="replace" so a transcript saved in another encoding cannot
        # crash the run - same as the drop folder does.
        with open(path, encoding="utf-8", errors="replace") as fh:
            return [{"subject": "sample_transcript.txt", "body": fh.read()}]

    if mode == "drop":
        os.makedirs(DROP_DIR, exist_ok=True)
        return _from_drop_folder()

    from inbox import fetch_unread, MailboxError
    try:
        return fetch_unread(subject_contains=os.environ.get("SUBJECT_FILTER", ""))
    except MailboxError as exc:
        print(f"Mailbox problem: {exc}")
        print("Tip: you can keep working with  python run_once.py --drop  "
              "and save transcripts as .txt files in the drop/ folder.")
        return []


def main() -> int:
    mode = "mail"
    if "--demo" in sys.argv:
        mode = "demo"
    elif "--drop" in sys.argv:
        mode = "drop"

    if not acquire_lock():
        return 0
    try:
        sources = get_sources(mode)
        if not sources:
            print("Nothing new. Exiting.")
            return 0

        records = load_records()
        total_added = 0

        for src in sources:
            body = (src.get("body") or "").strip()
            if len(body) < 40:
                print(f"Skipping '{src.get('subject','')}' - too short to be a transcript.")
                continue
            print(f"Reading: {src.get('subject','(no subject)')[:70]}")
            try:
                items = validate(extract_items(body, records))
            except ClaudeError as exc:
                print(f"  Claude problem: {exc}")
                continue
            records, added = merge(records, items)
            total_added += added
            print(f"  {len(items)} item(s) read, {added} new.")
            _archive_drop(src)          # drop-folder files move to drop/done/ once read

        save_records(records)
        print(f"\nDone. {total_added} new item(s). {len(records)} total in {os.path.basename(STORE_PATH)}.")
        return 0
    finally:
        release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
