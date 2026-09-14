# Work log — reference build

**This is the starter kit for Final Build Day, known to work.**
Build day: Tuesday 15 September 2026. The assignment is in [`ASSIGNMENT.md`](ASSIGNMENT.md).

---

## If an organiser sent you here at 12:35

You are not behind, and taking this costs you your distinction, **not your certificate**. Take it, get deployed, and spend the afternoon on the part that actually carries the marks — your skill file, your decisions, your evals.

```bash
gh repo fork taleemabad-university/worklog-reference --clone --fork-name my-work-log
cd my-work-log
python preflight.py
```

Then go straight to **Step 4** in `ASSIGNMENT.md` and deploy:

```bash
railway init
railway up
railway domain
```

Then carry on from **Step 5**. Steps 5 to 12 are still yours to do, and they are where the marks are.

---

## What is in here

| File | What it is |
|---|---|
| `preflight.py` | **Run this first, and whenever you are stuck.** Checks everything and tells you what to type next. |
| `serve.py` | The live page. Reads `records.json`, draws four columns. Installs nothing. **This is what you deploy.** |
| `schedule.py` | The job, on a 5-minute loop. Runs on **your laptop**, in its own terminal window. |
| `run_once.py` | One pass: read new input, ask Claude, validate, de-duplicate, save. |
| `claude_helper.py` | Talks to Claude through your own subscription. No API key. |
| `inbox.py` | Reads your mailbox over IMAP. Optional — `--drop` needs none of it. |
| `config.py` | Reads your `.env`. |
| `.claude/skills/worklog/SKILL.md` | **The rules.** Change this file and the behaviour changes, with no Python touched. Most of your mark is here. |
| `.claude/hooks/block-env-commit.py` | Stops you committing secrets. |
| `evals/cases/` | Five hard test cases, ready to run. |
| `README.template.md` | Copy to `README.md` and make every line true. |

## The three commands

```bash
python preflight.py          # am I OK?
python serve.py              # the page, on http://localhost:8000
python schedule.py --drop    # the job, in a second terminal
```

## What this is not

This is the **starter**, not a finished submission. There is deliberately no `README.md`, no `evals/results.md`, and the skill file is still generic. Those are three of the nine gates and they have to be yours.

## Safety

No credentials in this repository. `.env` and `.mcp.json` are gitignored and hook-blocked; `preflight.py` installs a real git pre-commit hook that covers commits from any git client, including the VS Code sidebar.

**Nothing in this system sends anything to anyone.** It reads and it writes records. There is no email, no WhatsApp, no message to a teacher or a colleague, by design.
