# A work log that fills itself in

**The reference build for Final Build Day — Taleemabad, Path to Agentic Mastery.**
Tuesday 15 September 2026. The full assignment is in [`ASSIGNMENT.md`](ASSIGNMENT.md).

---

## The problem it solves

Work disappears. You do three school observations and the weekly report shows zero. A decision gets made in a sync and a week later nobody can find it. Someone chases the same form four times because there is no list of who has done it.

The work happened. It just never got written down anywhere anyone else could see.

Writing it up by hand is the obvious fix, and it never survives a real week. Nobody types up their own day at 6pm.

**So this stops typing it up.** It is an agent that keeps the record for you, out of what you already produce.

```
  A meeting transcript arrives — by email, or dropped in as a .txt
                              |
                              v
  Every 5 minutes a job wakes up on YOUR LAPTOP, reads what is new,
  works out what actually happened, writes it down, and exits
                              |
                              v
  Your records — one row per task, decision or blocker,
  each with an owner, a real date, and the words it came from
                              |
                              v
  A live page ON THE INTERNET:
  what I did · what's open · what I decided · what's stuck
```

It runs on **your own Claude subscription**, through the `claude` command. No API key, no billing setup.

---

## How it is put together

Two halves, deliberately kept apart, because they fail for different reasons.

| | Where it runs | What it is |
|---|---|---|
| **The page** | Railway, on the internet | `serve.py` — reads `records.json`, draws four columns. Standard library only: **no dependencies, nothing to install, so the build cannot fail.** |
| **The job** | Your laptop, second terminal | `schedule.py` — one pass every 5 minutes. You can watch it tick, which is what makes a demo convincing. |

The job pushes its records up to the page over one authenticated POST. That is the only connection between them.

Keeping the job on the laptop means it uses the Claude login you already have — no long-lived token to mint, paste, or leak.

---

## Run it

```bash
python preflight.py          # am I OK? Every red line says what to type next.
python serve.py              # the page, on http://localhost:8000
python schedule.py --drop    # the job, in a second terminal
```

Then save a `.txt` transcript into `drop/` and wait. No mailbox, no API key, no setup.

---

## If an organiser sent you here at 12:35

You are not behind, and taking this costs you your distinction — **not your certificate**.

```bash
gh repo fork taleemabad-university/worklog-reference --clone --fork-name my-work-log
cd my-work-log
python preflight.py
```

Then go to **Step 4** of `ASSIGNMENT.md` and deploy:

```bash
railway init && railway up && railway domain
```

And carry on from **Step 5**. Steps 5 to 12 are still yours to do, and they are where the marks are.

---

## What is in here

| File | What it is |
|---|---|
| `preflight.py` | **Run this first, and whenever you are stuck.** Checks everything, names the fix, installs a git secret-guard. |
| `serve.py` | The live page. **This is what you deploy.** |
| `schedule.py` | The 5-minute loop. Runs on your laptop. |
| `run_once.py` | One pass: read input → ask Claude → validate → de-duplicate → save. |
| `claude_helper.py` | Talks to Claude through your own subscription. |
| `inbox.py` | Reads a mailbox over IMAP. Optional — `--drop` needs none of it. |
| `config.py` | Reads your `.env`. |
| `.claude/skills/worklog/SKILL.md` | **The rules.** Edit this Markdown file and the behaviour changes, with no Python touched. |
| `.claude/hooks/block-env-commit.py` | Refuses to commit secrets — by filename **and** by content. |
| `.env.example` | Every setting, with a placeholder and where to get each value. |
| `evals/cases/` | Five hard test cases: chatter only, a vague date, one task said three times, mixed Urdu and English, and no owner at all. |
| `README.template.md` | Copy to `README.md` and make every line true. |

---

## What this is not

This is the **starter**, not a finished submission. The skill file is still generic, there is no `evals/results.md`, and this README is mine rather than yours. Three of the nine gates live in exactly those gaps, and they have to be yours:

```bash
cp README.template.md README.md
cp evals/results.template.md evals/results.md
```

`preflight.py` will keep showing a red `README` until you do — replacing this page is part of the work, not an afterthought.

---

## The interesting problem

Getting text back from a model is easy. **Deciding correctly is the job**, and four decisions carry most of the marks:

1. **Is this a task, a decision, a blocker — or just chatter?** Extracting the tea order is as wrong as missing a real task.
2. **Who owns it, and by when?** *"Ali will look at it next week"* is owner `Ali` and a real calendar date. Dates are the most error-prone field there is — the starter still gets *"push it to Friday"* wrong, and that failure is written up in `evals/results.template.md` rather than hidden.
3. **Is this already open, or is it new?** Ten people reporting one problem is **one** item.
4. **Do you know enough to act?** When it cannot tell, it must **ask** — not guess. A system that quietly invents an owner is worse than useless, because people believe it.

---

## Safety

- **No credentials in this repository.** `.env` and `.mcp.json` are gitignored and blocked two ways: a Claude Code hook, and a real git `pre-commit` hook that `preflight.py` installs so it also covers the VS Code sidebar and your own terminal.
- The secret check reads **file contents**, not just filenames — a token pasted into a `.py` is caught too.
- The mailbox reader refuses to run without a subject filter, so it can never sweep up personal or HR mail.
- **Nothing here sends anything to anyone.** It reads, and it writes records. No email, no WhatsApp, no message to a teacher or a colleague, by design.
