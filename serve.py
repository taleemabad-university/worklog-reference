"""
serve.py - the live web page. This is the thing you deploy.

    python serve.py            # then open http://localhost:8000

It reads records.json and draws four columns:

    WHAT I DID   ·   WHAT'S OPEN   ·   WHAT I DECIDED   ·   WHAT'S STUCK

That is all it does. It does NOT call Claude, it does NOT need Node, it does
NOT need your token. That is deliberate: this is the piece that has to be
live by 12:35, so it is the piece with the fewest ways to fail. A build that
installs nothing cannot fail to install something.

The job that fills records.json is schedule.py, and it runs on your laptop.

Uses only the Python standard library - nothing to pip install.
"""

from __future__ import annotations

import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_PATH = os.path.join(HERE, "records.json")

# Railway (and most hosts) tell you which port to listen on through $PORT.
# Locally there is no $PORT, so we fall back to 8000.
PORT = int(os.environ.get("PORT", "8000"))

OWNER = os.environ.get("OWNER_NAME", "my work log")

# ─────────────────────────────────────────────────────────────────────────────
# How records get from your laptop to this page.
#
# The job runs on your laptop. This page runs on the internet. They talk over
# one POST: schedule.py sends the records up, this saves them, the page shows
# them. SYNC_TOKEN is the shared password that stops anyone else writing to
# your page.
#
# Set the SAME value in two places:
#   on Railway   railway variables --set SYNC_TOKEN=some-long-random-string
#   in your .env SYNC_TOKEN=some-long-random-string
#
# If it is not set, this page simply refuses every POST. That is the safe
# default: a page nobody can write to is better than a page anyone can.
# ─────────────────────────────────────────────────────────────────────────────
SYNC_TOKEN = os.environ.get("SYNC_TOKEN", "").strip()
MAX_UPLOAD = 2_000_000          # 2 MB is far more than a work log ever needs

COLUMNS = [
    ("What I did",     "done",     "Finished. Evidence that the week happened."),
    ("What's open",    "task",     "Not done yet. Someone owns each of these."),
    ("What I decided", "decision", "Settled, so nobody re-opens the argument."),
    ("What's stuck",   "blocker",  "Stopping work. These need somebody else."),
]


def load_records() -> list[dict]:
    """Read records.json. Never raise - an empty page beats a 500."""
    try:
        with open(STORE_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


def bucket(records: list[dict], key: str) -> list[dict]:
    if key == "done":
        return [r for r in records if r.get("status") == "done"]
    return [r for r in records if r.get("type") == key and r.get("status") != "done"]


def card(rec: dict) -> str:
    title = html.escape(str(rec.get("title", "(no title)")))
    owner = rec.get("owner")
    due = rec.get("due")
    ask = rec.get("ask")
    quote = rec.get("quote")
    low = rec.get("confidence") == "low"

    meta = []
    if owner:
        meta.append(f'<span class="who">{html.escape(str(owner))}</span>')
    if due:
        meta.append(f'<span class="due">{html.escape(str(due))}</span>')
    if low:
        meta.append('<span class="low">needs checking</span>')

    out = [f'<article class="card{" is-low" if low else ""}">']
    out.append(f"<h3>{title}</h3>")
    if meta:
        out.append(f'<p class="meta">{" ".join(meta)}</p>')
    if ask:
        out.append(f'<p class="ask">{html.escape(str(ask))}</p>')
    if quote:
        out.append(f'<blockquote>{html.escape(str(quote))}</blockquote>')
    out.append("</article>")
    return "".join(out)


def render() -> str:
    records = load_records()
    total = len(records)

    if total == 0:
        body = (
            '<div class="empty">'
            "<h2>Nothing captured yet.</h2>"
            "<p>This page is live, which is the hard part. It fills itself in "
            "once the job finds something to read.</p>"
            "<p>On your laptop, in a second terminal:</p>"
            "<pre>python schedule.py</pre>"
            "<p>Then save a <code>.txt</code> transcript into the "
            "<code>drop/</code> folder and wait.</p>"
            "</div>"
        )
    else:
        cols = []
        for label, key, blurb in COLUMNS:
            items = bucket(records, key)
            cards = "".join(card(r) for r in items) or '<p class="none">Nothing here.</p>'
            cols.append(
                f'<section class="col"><header><h2>{label}</h2>'
                f'<p class="count">{len(items)}</p></header>'
                f'<p class="blurb">{blurb}</p>{cards}</section>'
            )
        body = f'<div class="board">{"".join(cols)}</div>'

    return TEMPLATE.replace("{{BODY}}", body).replace("{{TOTAL}}", str(total)).replace(
        "{{OWNER}}", html.escape(OWNER)
    )


TEMPLATE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{OWNER}}</title>
<style>
:root{
  --paper:#EFF1EC; --lift:#F7F8F5; --ink:#16305B; --soft:#4A5F82;
  --rule:#BFCBD6; --stamp:#B3261E; --tick:#1C6B4A;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#11161F; --lift:#161C27; --ink:#DCE6F2; --soft:#93A6C0;
  --rule:#2B3647; --stamp:#E8776F; --tick:#5FBF92;
}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:16px/1.5 Georgia,"Iowan Old Style",serif;padding:0 16px}
.wrap{max-width:1200px;margin:0 auto;padding-block:32px}
header.top{border-bottom:2px solid var(--ink);padding-bottom:12px;margin-bottom:24px;
  display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;justify-content:space-between}
h1{font-size:1.5rem;margin:0;letter-spacing:.01em}
.tot{font-size:.85rem;color:var(--soft);font-family:Consolas,ui-monospace,monospace}
.board{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
@media(max-width:900px){.board{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.board{grid-template-columns:1fr}}
.col{min-width:0}
.col>header{display:flex;align-items:baseline;justify-content:space-between;
  border-bottom:1px solid var(--rule);padding-bottom:6px}
.col h2{font-size:.95rem;margin:0;text-transform:uppercase;letter-spacing:.08em}
.count{margin:0;font:700 1.1rem/1 Consolas,ui-monospace,monospace;color:var(--soft)}
.blurb{font-size:.78rem;color:var(--soft);margin:8px 0 14px}
.card{background:var(--lift);border:1px solid var(--rule);border-left:3px solid var(--ink);
  padding:12px;margin-bottom:12px}
.card.is-low{border-left-color:var(--stamp)}
.card h3{margin:0 0 6px;font-size:.95rem;line-height:1.35}
.meta{margin:0 0 6px;font-size:.75rem;font-family:Consolas,ui-monospace,monospace}
.who{color:var(--tick);font-weight:700}
.due{color:var(--soft)}
.low{color:var(--stamp)}
.ask{margin:6px 0 0;font-size:.8rem;color:var(--stamp);font-style:italic}
blockquote{margin:8px 0 0;padding-left:10px;border-left:2px solid var(--rule);
  font-size:.78rem;color:var(--soft)}
.none{font-size:.8rem;color:var(--soft);font-style:italic}
.empty{max-width:60ch;border:1px solid var(--rule);background:var(--lift);padding:24px}
.empty h2{margin-top:0}
pre{background:var(--paper);border:1px solid var(--rule);padding:10px;overflow-x:auto;
  font:.85rem/1.5 Consolas,ui-monospace,monospace}
code{font-family:Consolas,ui-monospace,monospace;font-size:.9em}
footer{margin-top:32px;border-top:1px solid var(--rule);padding-top:10px;
  font-size:.75rem;color:var(--soft)}
</style></head><body>
<div class="wrap">
<header class="top"><h1>{{OWNER}}</h1><p class="tot">{{TOTAL}} record(s)</p></header>
{{BODY}}
<footer>Written by an agent from meeting transcripts. Nothing here was sent to anyone.</footer>
</div></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str, code: int = 200) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:          # noqa: N802  (stdlib naming)
        path = self.path.split("?")[0]
        if path in ("/health", "/healthz"):
            self._send(b"ok", "text/plain; charset=utf-8")
        elif path == "/records.json":
            body = json.dumps(load_records(), indent=2, ensure_ascii=False)
            self._send(body.encode("utf-8"), "application/json; charset=utf-8")
        elif path in ("/", "/index.html"):
            self._send(render().encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(b"Not found", "text/plain; charset=utf-8", 404)

    def do_POST(self) -> None:         # noqa: N802  (stdlib naming)
        """Accept a records upload from schedule.py running on a laptop."""
        if self.path.split("?")[0] != "/records":
            self._send(b"Not found", "text/plain; charset=utf-8", 404)
            return

        if not SYNC_TOKEN:
            self._send(
                b"SYNC_TOKEN is not set on this server, so uploads are refused.\n"
                b"Set it with: railway variables --set SYNC_TOKEN=your-secret\n",
                "text/plain; charset=utf-8", 503,
            )
            return

        # Compare against the header. Not constant-time, but this guards a
        # work log, not a bank.
        if self.headers.get("X-Sync-Token", "") != SYNC_TOKEN:
            self._send(b"Wrong or missing X-Sync-Token.\n",
                       "text/plain; charset=utf-8", 403)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_UPLOAD:
            self._send(b"Bad Content-Length.\n", "text/plain; charset=utf-8", 400)
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._send(b"Body was not valid JSON.\n", "text/plain; charset=utf-8", 400)
            return

        if not isinstance(payload, list):
            self._send(b"Expected a JSON list of records.\n",
                       "text/plain; charset=utf-8", 400)
            return

        # Write atomically, so a half-finished upload can never be served.
        tmp = STORE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, STORE_PATH)

        print(f"  sync: stored {len(payload)} record(s)", flush=True)
        self._send(json.dumps({"ok": True, "stored": len(payload)}).encode("utf-8"),
                   "application/json; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        # One tidy line per request, so Railway's log view stays readable.
        print(f"  {self.address_string()} {fmt % args}", flush=True)


def main() -> int:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving your work log on http://localhost:{PORT}", flush=True)
    print(f"Reading records from {STORE_PATH}", flush=True)
    if not os.path.exists(STORE_PATH):
        print("No records.json yet - the page will say so. That is fine.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
