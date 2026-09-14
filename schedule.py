"""
schedule.py - the part that makes it run BY ITSELF.

Open a SECOND terminal window, leave it open, and run:

    python schedule.py --drop        # watch the drop/ folder
    python schedule.py               # read your mailbox

Every 5 minutes it wakes up, runs exactly one pass of run_once.py, and goes
back to sleep. You can watch it tick. That is the point - when an assessor
asks "show me it running by itself", you point at this window, drop a file,
and say nothing while it picks it up.

Leave it running. Ctrl-C stops it.

    python schedule.py --drop --once     # one pass, then stop (for testing)
    python schedule.py --drop --every 60 # a faster tick while you experiment

Uses only the Python standard library - nothing to pip install.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

import config  # noqa: F401  - reads your .env into os.environ on import
import run_once

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_PATH = os.path.join(HERE, "records.json")

DEFAULT_EVERY = int(os.environ.get("RUN_EVERY_SECONDS", "300"))

# Where to push records so your live page can show them. Both come from .env.
SYNC_URL = os.environ.get("SYNC_URL", "").strip()
SYNC_TOKEN = os.environ.get("SYNC_TOKEN", "").strip()


def stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def push_to_page() -> None:
    """Send records.json up to your deployed page. Never fatal - if the page
    is unreachable, the job keeps working and you still have the local file."""
    if not SYNC_URL or not SYNC_TOKEN:
        return
    try:
        with open(STORE_PATH, encoding="utf-8") as fh:
            body = fh.read().encode("utf-8")
    except OSError:
        return

    url = SYNC_URL.rstrip("/")
    if not url.endswith("/records"):
        url += "/records"

    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Sync-Token": SYNC_TOKEN},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            info = json.loads(resp.read().decode("utf-8", errors="replace"))
            print(f"  [{stamp()}] page updated ({info.get('stored')} record(s))", flush=True)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip().splitlines()
        print(f"  [{stamp()}] could not update the page: HTTP {exc.code} "
              f"{detail[0] if detail else ''}", flush=True)
        if exc.code == 403:
            print("           SYNC_TOKEN in .env does not match the one on Railway.", flush=True)
    except Exception as exc:                         # noqa: BLE001 - never crash the loop
        print(f"  [{stamp()}] could not reach the page: {exc}", flush=True)


def main() -> int:
    args = sys.argv[1:]

    # ── Refuse --demo on a loop ──────────────────────────────────────────
    # The demo transcript never changes, so a scheduled --demo re-reads the
    # same file every 5 minutes forever: 288 Claude calls a day, and zero new
    # records after the first one. That is pure waste, so we stop you.
    if "--demo" in args:
        print("WHAT BROKE:  --demo on a schedule reads the same sample file over")
        print("             and over. It adds nothing after the first run and it")
        print("             burns your Claude usage all day.")
        print("TYPE THIS:   python schedule.py --drop")
        print("             (and save your .txt transcripts into the drop/ folder)")
        print("IF THAT FAILS: put your hand up - this is not your fault.")
        return 1

    every = DEFAULT_EVERY
    if "--every" in args:
        try:
            every = max(10, int(args[args.index("--every") + 1]))
        except (IndexError, ValueError):
            print("--every needs a number of seconds, e.g. --every 60")
            return 1

    once = "--once" in args
    # Hand the mode flags straight through to run_once.
    run_once.sys.argv = [run_once.__file__] + [a for a in args
                                               if a in ("--drop", "--demo")]

    mode = "drop folder" if "--drop" in args else "mailbox"
    print(f"Watching your {mode}. One pass every {every}s.")
    if SYNC_URL and SYNC_TOKEN:
        print(f"Records will be pushed to {SYNC_URL}")
    else:
        print("Not pushing to a live page (set SYNC_URL and SYNC_TOKEN in .env to).")
    print("Leave this window open. Ctrl-C to stop.\n", flush=True)

    passes = 0
    try:
        while True:
            passes += 1
            print(f"[{stamp()}] pass {passes}", flush=True)
            try:
                run_once.main()
            except Exception as exc:                 # noqa: BLE001
                # One bad pass must never kill the loop - that is the whole
                # reason this runs as a loop and not as a single script.
                print(f"  [{stamp()}] this pass failed: {exc}", flush=True)
                print("           carrying on; the next pass is in "
                      f"{every}s.", flush=True)
            else:
                push_to_page()

            if once:
                print("\n--once given, so stopping here.")
                return 0

            print(f"  [{stamp()}] sleeping {every}s\n", flush=True)
            time.sleep(every)
    except KeyboardInterrupt:
        print(f"\nStopped after {passes} pass(es). "
              "Nothing is running now - start me again before your demo.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
