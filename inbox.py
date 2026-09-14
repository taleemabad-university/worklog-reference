"""
inbox.py - read new email out of any mailbox, using only the standard library.

Your meeting notetaker emails you a transcript. This fetches those emails so
your job can read them. Works with Gmail, Outlook, or any IMAP mailbox.

    from inbox import fetch_unread

    for msg in fetch_unread(subject_contains="transcript"):
        print(msg["subject"], msg["from"], len(msg["body"]))

GMAIL SETUP (5 minutes, do it BEFORE hackathon day):
  1. Your Google account must have 2-Step Verification switched on.
  2. Go to  https://myaccount.google.com/apppasswords
  3. Create an app password. Google shows you 16 letters. Copy them.
  4. Put them in your .env as IMAP_PASSWORD (spaces don't matter).
  That app password is NOT your normal password, and you can revoke it anytime.

OUTLOOK / OFFICE 365: host is outlook.office365.com. If your organisation has
disabled IMAP you will get a LOGIN failed error — tell an organiser early and
use the fallback in the guide.
"""

from __future__ import annotations

import email
import email.policy
import imaplib
import os
import re

import config  # noqa: F401  - reads your .env into os.environ on import

__all__ = ["fetch_unread", "MailboxError"]


class MailboxError(RuntimeError):
    """Raised when the mailbox cannot be reached or read."""


def _cfg(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def fetch_unread(
    *,
    subject_contains: str = "",
    mark_seen: bool = True,
    limit: int = 20,
    folder: str = "INBOX",
) -> list[dict]:
    """Return a list of unread emails as plain dicts.

    Each dict has: uid, subject, from, date, body  (body is plain text).

    Set mark_seen=False while you are testing, so the same email keeps coming
    back and you don't have to send yourself a new one every time.
    """
    host = _cfg("IMAP_HOST", "imap.gmail.com")
    user = _cfg("IMAP_USER")
    password = _cfg("IMAP_PASSWORD")

    if not user or not password:
        raise MailboxError(
            "WHAT BROKE:  IMAP_USER and IMAP_PASSWORD are not set.\n"
            "TYPE THIS:   cp .env.example .env\n"
            "             then open .env and fill in those two lines.\n"
            "For Gmail, IMAP_PASSWORD is a 16-character app password from\n"
            "https://myaccount.google.com/apppasswords - NOT your normal password.\n"
            "IF THAT FAILS: use  python run_once.py --drop  instead. It needs no\n"
            "mailbox at all and it runs the exact same pipeline."
        )

    # ─── Safety rail: never read mail we were not pointed at ──────────────
    #
    # Without a subject filter this would fetch the newest 20 unread messages
    # of ANY kind - HR letters, salary mail, personal mail - send their full
    # text to Claude, and mark them read so you never notice they arrived.
    #
    # So we refuse to run without one. Your notetaker's emails have a
    # predictable subject; name part of it and we only ever touch those.
    if not subject_contains:
        raise MailboxError(
            "WHAT BROKE:  SUBJECT_FILTER is not set, so this would read EVERY\n"
            "             unread email in your mailbox - including personal and\n"
            "             HR mail - and mark it read. It will not do that.\n"
            "TYPE THIS:   add a line to your .env, for example\n"
            "                 SUBJECT_FILTER=transcript\n"
            "             then forward your notetaker mail so the subject\n"
            "             contains that word.\n"
            "IF THAT FAILS: use  python run_once.py --drop  instead."
        )

    try:
        conn = imaplib.IMAP4_SSL(host, 993)
    except OSError as exc:
        raise MailboxError(f"Could not reach {host}: {exc}") from exc

    try:
        try:
            conn.login(user, password.replace(" ", ""))
        except imaplib.IMAP4.error as exc:
            raise MailboxError(
                f"Mailbox rejected the login for {user}.\n"
                "For Gmail this almost always means you used your normal "
                "password instead of a 16-character app password."
            ) from exc

        conn.select(folder)
        # Filter on the SERVER, so the bodies of unrelated mail are never even
        # downloaded. We still re-check the subject below, because some servers
        # match loosely.
        status, data = conn.search(None, "UNSEEN", "SUBJECT", f'"{subject_contains}"')
        if status != "OK":
            raise MailboxError(f"Could not search {folder}.")

        uids = data[0].split()
        if not uids:
            return []
        uids = uids[-limit:]          # newest N

        out: list[dict] = []
        for uid in uids:
            # BODY.PEEK does NOT mark the message read; we decide that ourselves.
            status, raw = conn.fetch(uid, "(BODY.PEEK[])")
            if status != "OK" or not raw or not raw[0]:
                continue

            msg = email.message_from_bytes(raw[0][1], policy=email.policy.default)
            subject = str(msg.get("Subject", ""))

            if subject_contains.lower() not in subject.lower():
                continue

            # Say out loud what we are about to read. If a subject here is not
            # a meeting transcript, your filter is too wide - fix it now.
            print(f"  mailbox: reading '{subject[:60]}'")

            out.append({
                "uid": uid.decode(),
                "subject": subject,
                "from": str(msg.get("From", "")),
                "date": str(msg.get("Date", "")),
                "body": _plain_body(msg),
            })

            if mark_seen:
                conn.store(uid, "+FLAGS", "\\Seen")

        return out
    finally:
        try:
            conn.logout()
        except Exception:
            pass


def _plain_body(msg) -> str:
    """Get readable text out of an email, preferring plain text over HTML."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return _decode(part)
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return _strip_html(_decode(part))
        return ""
    if msg.get_content_type() == "text/html":
        return _strip_html(_decode(msg))
    return _decode(msg)


def _decode(part) -> str:
    try:
        payload = part.get_payload(decode=True)
        if payload is None:
            return ""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")
    except Exception:
        return ""


def _strip_html(html: str) -> str:
    """Crude but dependency-free HTML to text."""
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
                .replace("&quot;", '"'))
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


if __name__ == "__main__":
    # Self-test: python inbox.py
    try:
        msgs = fetch_unread(
            subject_contains=os.environ.get("SUBJECT_FILTER", ""),
            mark_seen=False,          # a test must never consume your mail
            limit=5,
        )
    except MailboxError as exc:
        print("PROBLEM:\n", exc)
        raise SystemExit(1)
    print(f"Found {len(msgs)} unread email(s).")
    for m in msgs:
        print(f"  - {m['subject'][:70]}  ({len(m['body'])} chars)")
    print("\nNothing was marked as read. Your mailbox is untouched.")
