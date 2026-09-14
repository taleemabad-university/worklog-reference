"""
config.py - reads your .env file so the rest of the kit can see your settings.

You do not call anything in here yourself. `run_once.py` and `inbox.py` import
it at the top, and by the time your code runs, everything in .env is available
through os.environ.

    # .env
    IMAP_USER=you@taleemabad.com
    IMAP_PASSWORD=abcd efgh ijkl mnop
    SUBJECT_FILTER=transcript

    # anywhere in your code
    import os
    os.environ["IMAP_USER"]

Uses only the Python standard library - nothing to pip install. (You may have
used python-dotenv on the course; this does the same job with no install step,
which is one less thing to go wrong this morning.)

Values already set in your real environment always win. That is what lets
Railway's variables override your .env in the cloud without you changing code.
"""

from __future__ import annotations

import os

__all__ = ["load_env", "require", "ENV_PATH", "MissingSetting"]

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(HERE, ".env")


class MissingSetting(RuntimeError):
    """Raised when something the kit needs is not in your .env."""


def load_env(path: str = ENV_PATH) -> int:
    """Read KEY=VALUE lines out of `path` into os.environ. Returns how many
    it set. A missing .env is NOT an error - plenty of the kit works without
    one, and --drop mode needs nothing at all."""
    if not os.path.exists(path):
        return 0

    loaded = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            # People paste "export FOO=bar" out of guides. Cope with it.
            if key.startswith("export "):
                key = key[len("export "):].strip()
            value = value.strip()
            # Strip one matching pair of surrounding quotes, and nothing else -
            # a Gmail app password has spaces in it and must survive intact.
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            if not key:
                continue
            if key in os.environ:        # real environment wins (this is how
                continue                 # Railway variables override .env)
            os.environ[key] = value
            loaded += 1
    return loaded


def require(name: str, why: str, fix: str) -> str:
    """Fetch a setting, or fail with a message that tells you what to type.

    Every error in this kit follows the same shape on purpose:
        WHAT BROKE / TYPE THIS / IF THAT FAILS
    """
    value = os.environ.get(name, "").strip()
    if value:
        return value
    raise MissingSetting(
        f"WHAT BROKE:  {name} is not set. {why}\n"
        f"TYPE THIS:   {fix}\n"
        f"IF THAT FAILS: put your hand up - this is not your fault.\n"
        f"(Looked in {ENV_PATH})"
    )


# Load on import. Every module that needs settings just imports this first.
LOADED = load_env()


if __name__ == "__main__":
    # Self-test: python config.py
    if not os.path.exists(ENV_PATH):
        print(f"No .env found at {ENV_PATH}")
        print("TYPE THIS:   cp .env.example .env")
        print("Then open .env and fill it in. You can also skip this entirely")
        print("and use  python run_once.py --drop  which needs no settings.")
        raise SystemExit(0)
    print(f"Read {LOADED} setting(s) from {ENV_PATH}:")
    for key in ("IMAP_HOST", "IMAP_USER", "SUBJECT_FILTER"):
        print(f"  {key:16} = {os.environ.get(key, '(not set)')}")
    # Never print the password itself.
    pw = os.environ.get("IMAP_PASSWORD", "")
    print(f"  {'IMAP_PASSWORD':16} = {'set (' + str(len(pw)) + ' chars)' if pw else '(not set)'}")
