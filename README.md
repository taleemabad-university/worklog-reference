# My work log

**Copy this to `README.md` and make every line true.**

```
cp README.template.md README.md
```

> **One false claim fails the whole submission.** That is not harshness — a
> README describing software that does not exist is worse than no README,
> because someone will rely on it. Before you hand this in, read it line by
> line and ask of every sentence: *can I show this on my live URL right now?*
> If no — delete the line, or fix the feature. Deleting is allowed and costs
> you nothing.

---

## What it does

> One sentence, the shape from Step 1.

I send ______________________, and within 5 minutes ______________________
appears in ______________________.

## Who it is for

> Your actual job. A coach, an RM, HR, finance — say which, and what you
> personally stop doing by hand because of this.

## It is live at

- **Page:** https://______________________
- **Repo:** https://github.com/______________________

## How it runs

- `serve.py` — the page. Deployed on Railway. Reads `records.json`.
- `schedule.py` — the job. Runs on my laptop, one pass every 5 minutes.
- `run_once.py` — one pass: read new input, ask Claude, validate, de-duplicate, save.
- `.claude/skills/worklog/SKILL.md` — **the rules.** Change this file, the
  behaviour changes, no Python touched.

To run it yourself:

```
python preflight.py        # checks everything, tells you what to fix
python serve.py            # the page, on http://localhost:8000
python schedule.py --drop  # the job, in a second terminal
```

## What it decides

> This is the 25-point row. Say what it does, honestly, including where it is weak.

- **Task / decision / blocker / chatter:** ______________________
- **Owner and date:** ______________________
- **Already open, or new:** ______________________
- **When it does not know:** ______________________

## What I cut, and why

> At least one real entry. Someone who cut nothing did not plan.

- I cut ______________________ because ______________________
- I cut ______________________ because ______________________

## What does not work yet

> Being straight here scores better than silence. An assessor will find it anyway.

- ______________________
- ______________________

## Evals

See [`evals/results.md`](evals/results.md). **PASS: ___ FAIL: ___**, including
at least one honest failure with a reason.

## Safety

- No secrets in this repo. `.env` and `.mcp.json` are in `.gitignore`, and a
  pre-commit hook blocks them.
- **This system sends nothing to anyone.** It reads and it writes records. There
  is no email, no WhatsApp, no message to a teacher or a colleague, by design.
- The mailbox reader only ever opens mail whose subject matches `SUBJECT_FILTER`.

## Who helped me

> Saying so is not cheating, it is working.

- ______________________
