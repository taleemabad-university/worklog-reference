# BUILD A WORK LOG THAT FILLS ITSELF IN

**Path to Agentic Mastery — Final Build Day**
**Tuesday 15 September 2026 · 10:00 am – 4:30 pm · 12 steps · 3 levels · 1 shipped product**

---

## What you'll walk away with

- ✓ A working agent that reads your meetings and writes your work down for you
- ✓ Running on a schedule, on the internet, at a URL you can send to anyone
- ✓ A skill file, an MCP connection and a hook — the harness, in a real product
- ✓ Evals that prove it works, and a failure you can explain
- ✓ Your certificate

**You do not need to be the best coder in the room to pass this.** You need to finish, be honest about what you built, and be able to answer questions about your own work.

---

## The thing you are building

Work disappears. You do three school observations and the weekly report shows zero. A decision gets made in a sync and a week later nobody can find it. Someone chases the same form four times because there is no list of who has done it. The work happened — it just never got written down anywhere anyone else could see.

Writing it up by hand is the obvious fix and it never survives a real week. Nobody types up their own day at 6pm.

**So stop typing it up.** Build an agent that keeps the record for you, from what you already produce.

```
  A meeting transcript lands in your email
  (or you send yourself a voice note / a quick message)
                    |
                    v
  Every 5 minutes, a job wakes up on YOUR LAPTOP, reads what is
  new, works out what actually happened, writes it down, exits
                    |
                    v
  Your records - one row per task, decision or blocker
                    |
                    v
  A live web page ON THE INTERNET:
  what I did - what's open - what I decided - what's stuck
```

It runs on **your Claude subscription**, through the `claude` command you already use. No API key. No billing setup.

**Your version is tuned to your own job.** A coach captures observations done, lesson plans reviewed, school visits, teacher issues raised. An RM captures coach complaints and roster corrections. Someone in HR or admin captures tasks, deadlines and approvals chased. Someone in finance or data captures approvals, spend items, requests received.

Same system. Your words.

---

## Three levels

Work through them **in order**. Do not build a hook at 11am when nothing is deployed.

| | | What it is |
|---|---|---|
| **LEVEL 1** | **Ship it** | It runs on a schedule · it is deployed · it is on GitHub · your README is true |
| **LEVEL 2** | **Show your craft** | A skill file · an MCP connection · a working hook |
| **FINAL BOSS** | **Prove it** | Evals with an honest failure · and you answer three questions about your own build |

**All three are required to be certified.** But Level 1 first, always. Someone with Level 1 finished and Level 2 half-done is in a far better place at 4pm than the reverse.

---

## The day

| Time | | |
|---|---|---|
| 10:00 am – 10:15 am | Briefing — read this | |
| 10:15 am – 10:50 am | **Step 0** — Get your tools working | 35 min |
| 10:50 am – 11:05 am | **Step 1** — Say what you are building | 15 min |
| 11:05 am – 11:30 am | **Step 2** — Get the kit, prove Claude answers you | 25 min |
| **11:30 am – 12:00 pm** | **☕ Tea** | |
| 12:00 pm – 12:20 pm | **Step 3** — Put it on GitHub | 20 min |
| 12:20 pm – 12:35 pm | **Step 4** — Deploy it while it is still empty | 15 min |
| 12:35 pm – 1:00 pm | **Step 5** — Write your skill file | 25 min |
| 1:00 pm – 1:30 pm | **Step 6** — Teach it to read your work | 30 min |
| **1:30 pm – 2:10 pm** | **🍽 Lunch** | |
| 2:10 pm – 3:00 pm | **Step 7** — Make it decide well | 50 min |
| 3:00 pm – 3:10 pm | **Step 7b** — Make it run by itself | 10 min |
| 3:10 pm – 3:30 pm | **Step 8** — Send records to Notion through MCP | 20 min |
| 3:30 pm – 3:45 pm | **Step 9** — Add your safety hook | 15 min |
| 3:45 pm – 4:00 pm | **Step 10** — Run your evals | 15 min |
| 4:00 pm – 4:10 pm | **Step 11** — Freeze. Make your README true | 10 min |
| 4:10 pm – 4:30 pm | **Step 12** — Demo | 20 min |

> **The hard gate is 12:35 pm.** If your page is not live on the internet by then, stop building features and put your hand up. Deploying at 3pm is exactly how most of you finished the course with a `railway.json` and no live URL.

---

# THE STEPS

---

## Step 0 — Get your tools working

**35 min · Step 0 of 12**

**Why:** People who start coding before their tools work lose the time back with interest at 2pm.

### First — which terminal are you in?

> **Windows: use Git Bash. Not PowerShell, not Command Prompt.**
> Press Start, type `Git Bash`, open it. You already have it — it came with git.
>
> **Mac: use Terminal.** Nothing to do.
>
> **Every command in this brief is written for those two.** Pasted into
> PowerShell, some of them fail in ways that look like your mistake and are not.

### Then — one command

```bash
python preflight.py
```

It checks everything below, and **every red line tells you exactly what to type next.** Run it any time you are unsure where you stand. It is the fastest answer you will get all day to *"am I on track?"*

A good one looks like this:

```
  PREFLIGHT
  ------------------------------------------------------------------
  [OK]  Shell                      Git Bash
  [OK]  Python                     3.13.6
  [OK]  claude CLI                 2.1.271 (Claude Code)
  [OK]  Claude answers             HELLO
  [!]   Skill file                 still looks like the starter
  [X]   Railway login              not logged in
           -> railway login
  ------------------------------------------------------------------
  GATES: 2 of 8 checkable here are green.
```

`[OK]` is done · `[!]` is fine for now · `[X]` is fix this before you move on.

### What it is checking

| # | Run this | It passed when |
|---|---|---|
| 1 | `claude --version` | A version number prints |
| 2 | `python claude_helper.py` | You see `HELLO` then `{'ok': True}` |
| 3 | `python run_once.py --demo` | It writes `records.json` — see below |
| 4 | `gh auth status` | It says you are logged in. If not: `gh auth login` |
| 5 | `railway login` | `railway whoami` returns your name |
| 6 | Gmail **app password** — [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) | `python inbox.py` lists your unread mail |

**Check 3 — done looks like this.** Your terminal shows:

```
Reading: sample_transcript.txt
  6 item(s) read, 6 new.

Done. 6 new item(s). 6 total in records.json.
```

Your numbers may differ. **If there is no `Done.` line, you are not done.**

**✅ Checkpoint:** Checks 1–5 green, and `python preflight.py` shows no `[X]`.

**⚠️ If it doesn't work:**
- *Check 6 fighting you at 10:50 am?* **Leave it. You do not need email today.** You can build, deploy, evaluate and demo this entire assignment without your mailbox ever working — see Step 6. Losing an hour to IMAP is the easiest avoidable way to fail today.
- *`claude` not found?* Close your terminal completely and open a new one.
- *Anything else red?* Read the `->` line underneath it. That is the command.

**Next: Step 1 — say what you are building.**

---

## Step 1 — Say what you are building, in one sentence

**15 min · Step 1 of 12**

**Why:** The people who fail this day are not the ones who cannot code. They are the ones who never decided what "finished" meant.

Write **one sentence** in this shape, on paper, and show it to an organiser:

> *"I send **[what]**, and within 5 minutes **[what record]** appears in **[where]**."*

Real examples:

> *"I forward my coaching sync transcript, and within 5 minutes each teacher issue raised appears in my Notion with the school named."*

> *"I send myself a voice note after a school visit, and within 5 minutes the follow-ups appear on my week page with who owns them."*

**✅ Checkpoint:** An organiser has read your sentence and signed it off.

**⚠️ If it doesn't work:** If you cannot fill in the blanks, your idea is too big. Cut it until you can. One input, one record, one place.

**Next: Step 2 — get the kit.**

---

## Step 2 — Get the kit and prove Claude answers you

**25 min · Step 2 of 12 · LEVEL 1**

**Why:** Everything later assumes Claude is reachable from your code. Prove it now, not at 3pm.

Copy the starter folder somewhere sensible, then:

```bash
python claude_helper.py
```

```bash
python run_once.py --demo
```

Now run that second one **again**:

```bash
python run_once.py --demo
```

**✅ Checkpoint:** The first `--demo` run added items. **The second should add 0**, or very few. That is de-duplication already working — you will make it much better in Step 7.

> If the second run adds a *few* items instead of zero, that is the model rewording a title, not you doing something wrong. Move on. Only worry if it adds *everything* again.

**⚠️ If it doesn't work:**
- *`ModuleNotFoundError`?* You are in the wrong folder. Change into the folder that has `claude_helper.py` in it.
- *Second run added everything again?* Delete `records.json` and try once more. If it still does, tell an organiser — that is the kit misbehaving, not you.

**Next: Step 3 — GitHub.**

---

## Step 3 — Put it on GitHub

**20 min · Step 3 of 12 · LEVEL 1**

**Why:** Your work is not gradeable until it is in a repo we can open. This is a hard requirement, not paperwork.

**File: `.gitignore`** — check this exists *before* your first commit, and that it contains `.env`.

One command per line:

```bash
git init
```

```bash
git add .
```

```bash
git commit -m "Work log - initial"
```

```bash
gh repo create my-work-log --private --source=. --push
```

Now add us as a collaborator. **This is required.** First, find your GitHub username:

```bash
gh api user --jq .login
```

Copy what it prints. Everywhere below, put it where `YOUR-USERNAME` is:

```bash
gh api -X PUT repos/YOUR-USERNAME/my-work-log/collaborators/taleemabad-university -f permission=push
```

**✅ Checkpoint:** This prints `taleemabad-university`:

```bash
gh api repos/YOUR-USERNAME/my-work-log/collaborators --jq '.[].login'
```

**⚠️ If it doesn't work:**
- *`gh: command not found`?* Go back to Step 0, check 4.
- *Did a password reach GitHub?* **Change the password.** Deleting the file does not remove it from the history.

**Next: Step 4 — deploy.**

---

## Step 4 — Deploy it while it is still empty

**15 min · Step 4 of 12 · LEVEL 1 · THE HARD GATE**

**Why:** This is the most important step of the day. Deploy something pointless *now*, while there is nothing to go wrong, and you spend the afternoon adding features to a thing that already works. Leave it until 3pm and you will not deploy at all — we have the evidence from your own course projects.

What you are deploying is `serve.py` — the page. It reads `records.json` and draws your four columns. **It installs nothing and it does not call Claude**, which is exactly why it is the piece that goes up first: a build that installs nothing cannot fail to install something.

Try it on your own machine first:

```bash
python serve.py
```

Open http://localhost:8000. It will say *"Nothing captured yet"*. **That is a pass.** Stop it with Ctrl-C.

Now put it on the internet:

```bash
railway init
```

```bash
railway up
```

```bash
railway domain
```

That last one prints your public URL.

**✅ Checkpoint:** You open that URL **on your phone**, on mobile data, and see your page. It says "Nothing captured yet" — **that is the point.** It is live, and it is empty, and empty is easy to fix this afternoon.

**⚠️ If it doesn't work:**
- *Build failing?* Railway builds in the cloud, so you do **not** need Docker locally. `railway logs` shows you why. Nothing in this project needs installing, so a failure here is configuration, not code — put your hand up.
- *Page loads but says nothing?* That is correct. Come back at Step 7b.
- *Not live by 12:35 pm?* **Stop and raise your hand.** Do not spend lunch on this alone. There is a working repo an organiser can give you — taking it costs you a distinction, not your certificate.

**Next: Step 5 — your skill file.**

---

## Step 5 — Write your skill file

**25 min · Step 5 of 12 · LEVEL 2**

**Why:** This is where your extraction rules live, and it is most of your mark. A skill file means you change the agent's behaviour by editing a Markdown file — not by editing code. That is the whole argument for skill files, and now you use it for real.

**File: `.claude/skills/worklog/SKILL.md`**

It already exists, with starter rules. **Open it and make it yours.** What earns marks:

- **Your own vocabulary.** A coach might add *"an observation counts as a task only if a school is named."*
- **What to always ignore.** Attendance chatter? Four-line greetings?
- **A worked example.** Paste one real line from your own work and the exact record you want back. This is the single most effective thing you can add.

**✅ Checkpoint:** Prove the file really is driving the agent. Add this line temporarily at the bottom:

```markdown
ALWAYS prefix every title with the word ZEBRA.
```

Then:

```bash
python run_once.py --demo
```

Every title should come back starting with ZEBRA. **Now delete that line.** You have just proved your skill file is live.

**⚠️ If it doesn't work:** If nothing says ZEBRA, the job is not finding your file. Check it sits at exactly `.claude/skills/worklog/SKILL.md`.

**Next: Step 6 — real input.**

---

## Step 6 — Teach it to read your actual work

**30 min · Step 6 of 12**

**Why:** Sample data proves the pipeline. Your own words prove the product.

There are three ways in, and **all three run the same pipeline**:

```bash
python run_once.py
```

```bash
python run_once.py --drop
```

```bash
python run_once.py --demo
```

- plain `run_once.py` reads your **real mailbox** — first `cp .env.example .env` and fill in the mailbox section (it tells you where to get a Gmail app password), then you need Step 0 check 6 **and** a `SUBJECT_FILTER` line in that `.env` — without one it refuses to run, so that it can never read your personal or HR mail by accident)
- `--drop` reads any `.txt` file you save into the **`drop/` folder**
- `--demo` reads the sample transcript

**✅ Checkpoint:** Your own words — a real transcript, or a message you wrote — went in, and a record came out.

**⚠️ If it doesn't work:** **Email being difficult? Use `--drop` and move on.** Save your transcript as a `.txt` in `drop/` and the job reads it on the next run. No email, no app password, no waiting. Losing an hour to IMAP is the easiest way to fail today, and it is completely avoidable.

**Next: Step 7 — the part that actually earns marks.**

---

## Step 7 — Make it decide well

**50 min · Step 7 of 12 · LEVEL 1 · THE BIG ONE**

**Why:** Getting text back from Claude is easy. **Deciding correctly is the job**, and this is where most of your marks are.

Your agent has to get four things right. Work on them in your `SKILL.md`, and test after each change.

**1 · Is this a task, a decision, a blocker — or just chatter?**
Most of a meeting is noise. Someone says the tea has arrived. Extracting that is as wrong as missing a real task.

**2 · Who owns it, and by when?**
*"Ali will look at it next week"* is owner `Ali` and a real calendar date — not the words "next week". **Dates are the most error-prone field there is.** When we tested this, the model was told "push it to Friday" and produced a Wednesday. Put a date case in your evals.

**3 · Is this already open, or is it new?**
If ten people report the same problem, that is **one** item, not ten. This is the hardest of the four, and the one that separates a good build from an average one.

**4 · Do you know enough to act?**
When it genuinely cannot tell, it must **ask** — write the question into the `ask` field — rather than guess. **Guessing an owner is worse than asking.** A system that quietly invents an owner is worse than useless, because people believe it.

**And never trust the shape.** When we tested this, the model was told `confidence` must be `"high"` or `"low"` and it returned `"medium"`. Look at `validate()` in `run_once.py` — that is why it exists. Extend it for any field you add.

**✅ Checkpoint:** Run the same transcript twice — the second run adds **0**. Then run a *different* transcript that mentions one of the same things. It should recognise it, not duplicate it.

**⚠️ If it doesn't work:** *Duplicates appearing?* Before you rewrite your prompt, check you have not deleted the lock in `run_once.py`. If a run takes longer than 5 minutes the next starts on top of it and writes everything twice — that looks exactly like broken de-duplication, but it is not.

---

## Step 7b — Make it run by itself

**10 min · Step 7b of 12 · LEVEL 1 · THIS IS A GATE**

**Why:** "It runs when I run it" is a script. "It runs when nobody is watching" is a product. This is gate 1, and it takes ten minutes.

**Do this only now, not this morning.** A job on a loop with a bad prompt just writes rubbish every five minutes and burns your Claude usage. Get Step 7 right first — that is why this step is here and not at 12:30.

Open a **second terminal window**, in the same folder, and leave it open:

```bash
python schedule.py --drop
```

Every 5 minutes it wakes up, does one pass, and sleeps again. You can watch it tick:

```
Watching your drop folder. One pass every 300s.
Leave this window open. Ctrl-C to stop.

[15:02:11] pass 1
Reading: monday-sync.txt
  4 item(s) read, 4 new.
  [15:02:58] page updated (4 record(s))
  [15:02:58] sleeping 300s
```

**To make your live page show them**, pick any long random string and put it in **both** places — your `.env` and Railway:

```bash
railway variables --set SYNC_TOKEN=pick-something-long-and-random
```

```bash
railway domain
```

If you have not made your settings file yet:

```bash
cp .env.example .env
```

Open it — it explains every setting and where to get each value. Then fill in these two, using the URL that printed:

```
SYNC_URL=https://your-app.up.railway.app
SYNC_TOKEN=pick-something-long-and-random
```

Restart `schedule.py` and it will push each pass up to your page.

**✅ Checkpoint:** With `schedule.py` running and **nobody touching the keyboard**, save a `.txt` into `drop/`, wait, and watch the record appear on your live URL. That is gate 1 and gate 3, proved together, and it is exactly what an assessor will ask you to do at 16:10.

**⚠️ If it doesn't work:**
- *`could not update the page: HTTP 403`?* Your `SYNC_TOKEN` in `.env` does not match the one on Railway. They must be identical.
- *Page still empty?* Open `your-url/records.json` in a browser. If that is empty too, the push is not arriving. If it has your records, refresh the page.
- *Nothing happening at all?* The loop only reads **new** files. Save a fresh `.txt` into `drop/`.
- *Laptop went to sleep over lunch?* The loop stops. Start it again before you demo — and check the window is still ticking before an assessor walks over.

**Next: Step 8 — MCP.**

---

## Step 8 — Send your records to Notion through MCP

**20 min · Step 8 of 12 · LEVEL 2**

**Why:** A JSON file on a server is not somewhere your colleagues can look. MCP is how your agent reaches a real tool — and it is what you learned it for.

**File: `.mcp.json`** — copy `.mcp.json.example` and put your own Notion token in it.

> **That file now holds a live credential.** It is already in `.gitignore` and the hook will block it, but check for yourself before you push — a token in git history is not fixed by deleting the file afterwards:
>
> ```bash
> git status
> ```
>
> If `.mcp.json` appears in that list, stop and put your hand up.

Then point the helper at it:

```python
from claude_helper import ask_json

items = ask_json(prompt, mcp_config=".mcp.json", allow_tools="mcp__notion")
```

**✅ Checkpoint:** A record your agent created is visible in **your own Notion**, and you can refresh the page and still see it.

**⚠️ If it doesn't work:**
- *Claude says it cannot do anything?* You left out `allow_tools`. Without it, every tool stays blocked.
- *Running out of time?* **`records.json` still counts as your store.** Get the MCP connection working even if only for one field — a working connection beats a perfect one you never finished.

**Next: Step 9 — your hook.**

---

## Step 9 — Add your safety hook

**15 min · Step 9 of 12 · LEVEL 2**

**Why:** Your own course audit found the number one problem across every project was hardcoded credentials. A hook stops that happening to you automatically, instead of you remembering not to.

**File: `.claude/settings.json`** — already wired to a hook at `.claude/hooks/block-env-commit.py`. It watches every bash command and refuses a `git commit` when a secret is staged.

**✅ Checkpoint:** Prove it fires. Run all three lines — **including the last one**:

```bash
echo "NOT_A_REAL_SECRET=test" > .env.test
git add -f .env.test
git restore --staged .env.test
rm .env.test
```

Between the second and third line, ask Claude to commit. **It must be refused.** The last two lines put things back; do not skip them.

> Note it says `.env.test`, not `.env`. **Do not test this on your real `.env`** — `>` overwrites the file, and you would wipe the settings you added at Step 7b without noticing. The hook treats both the same.

**It also checks inside your files.** Paste a fake token into a `.py` file and try to commit that — it is refused too. That matters more than the filename check, because your own course audit found hardcoded credentials were the number one problem.

> **What it does not cover, so you know:** this is a Claude Code hook, so it fires when *Claude* commits. `python preflight.py` also installs a real git hook, which covers commits you make from the VS Code sidebar or your own terminal. Run preflight once and you are covered both ways. Until you do — commit through Claude Code.

**⚠️ If it doesn't work:** Hooks load when the session starts. Restart Claude Code and try again.

**For full marks, make it yours:** change what it protects, or add a second hook that does something useful for your own project.

**Next: Step 10 — evals.**

---

## Step 10 — Run your evals

**15 min · Step 10 of 12 · FINAL BOSS**

**Why:** "It seemed to work" is not evidence. An eval is how you say *how well* it works, with a number you are willing to defend.

**File: `evals/results.md`**

```bash
cp evals/results.template.md evals/results.md
```

The template has the table already drawn and **five ready-made hard cases** sitting in `evals/cases/` — chatter only, a vague date, the same task said three times, mixed Urdu and English, and one with no owner at all. Run one like this:

```bash
cp evals/cases/02-vague-date.txt drop/
python run_once.py --drop
```

Then look at `records.json` and write down **what you actually got**, not what you hoped for. Use your own transcripts too — at least one should be yours.

**✅ Checkpoint:** Your results file has at least 5 cases, real counts, and **at least one honest FAIL with a note on why**.

**⚠️ If it doesn't work:**
- *Everything passed?* Your cases are too easy, and an assessor will pick a harder one live. Add a messy one — mixed Urdu and English, a vague deadline, two people mentioning the same task.
- A results file reading `PASS: 0, FAIL: 0, PENDING: 3` is not an eval. We have seen that one before.

**Next: Step 11 — freeze.**

---

## Step 11 — Freeze. Make your README true

**10 min · Step 11 of 12 · LEVEL 1**

**Why:** One false claim in a README fails the whole submission. That is not harshness — a README describing software that does not exist is worse than no README, because someone will rely on it.

**File: `README.md`**

```bash
cp README.template.md README.md
```

Stop adding features. Go through the template and write down **only what actually works**, and add:

> **What I cut and why** — at least one real entry. Someone who cut nothing did not plan.

**✅ Checkpoint:** Read your README line by line. For every claim ask: *"can I show this on the live URL right now?"* If no — delete the line, or fix the feature.

**⚠️ If it doesn't work:** An honest small README beats an impressive false one, every single time.

**Next: Step 12 — show us.**

---

## Step 12 — Demo

**20 min · Step 12 of 12 · FINAL BOSS**

**Why:** Shipping includes showing.

Three rooms running in parallel. You get a few minutes. **Send a real message live and let the job pick it up** — no pre-loaded database.

Then three questions about your own build. They are never *"explain this code"* — they are about failure:

- *"Show me where you handle Claude returning something that isn't valid JSON. What if it happens twice?"*
- *"Two people mentioned the same task in one meeting. Walk me through what your code does."*
- *"Your job fails at 3am. What is the first thing you check?"*
- *"Why is this a task and not a decision? Show me where that is in your skill file."*

**✅ Checkpoint:** You demoed on the live URL, and you answered your questions.

---

# HOW YOU ARE JUDGED

**First, the gates. All of them, or no certificate — points do not rescue a missing one.**

- ☐ **It runs by itself.** `schedule.py` ticking in its own window. An assessor watches it pick up a live message with nobody touching the keyboard.
- ☐ **It is on GitHub** with `taleemabad-university` as a collaborator.
- ☐ **It is deployed** and opens on the assessor's laptop — the page on the internet, showing your records.
- ☐ **Your skill file is real** and drives the behaviour.
- ☐ **An MCP connection works.**
- ☐ **A hook fires.**
- ☐ **Your README is true.** One false claim fails it.
- ☐ **Evals recorded**, with at least one honest failure.
- ☐ **You answered your questions.**

**Then, out of 100:**

| Pts | |
|---:|---|
| **30** | **Is it useful?** Would you genuinely use this next week, and how much time does it save? A colleague has to agree with your number. |
| **25** | **Does it actually decide?** The four decisions in Step 7. Blind extraction scores low. |
| **15** | **Your harness.** Skill file, MCP and hook — doing real work, or decoration? |
| **15** | **Evals and honesty.** A real case set, a failure you can name and explain. |
| **10** | **Does it survive?** Empty mailbox, malformed message, a restart. |
| **5** | **Craft.** No secrets in the repo. README matches reality. |

**Certified = every gate + 60 or more.**

---

## What does not matter

- **How pretty it looks.** Nobody is marking your CSS.
- **How much code you wrote.** A short working thing beats a large broken one.
- **Whether your idea is original.** It is meant to be useful, not novel.
- **Whether you finished everything.** Level 1 done properly beats all three levels half-done.
- **Whether you needed help.** Ask. Say who helped you. That is not cheating, it is working.

---

## What you may and may not do

| ✓ You may | ✗ You may not |
|---|---|
| Use Claude for all of it — that is the point | Hand your code to someone else, or take theirs |
| Reuse anything from your course project | Commit secrets (your hook will stop you) |
| Copy from the starter kit freely | Send messages to real teachers or colleagues |
| Ask organisers and each other for help | Demo from localhost, a screenshot or a recording |
| Change the record shape to suit your job | Pre-load your database before the demo |
| Cut scope — and say so in your README | Add features after 4:00 pm |

**R-01** Work on your own. Ask for help freely, and say who helped you.
**R-02** Commit under your own GitHub account, through the day — not one dump at 4pm.
**R-03** Everything outbound is drafted for a human. Never auto-sent to a real person.
**R-04** At 4:00 pm you stop adding features.

---

## If you miss something

You get **72 hours** to fix it and show it again. You will be certified. You will not be eligible for a distinction. That is said now, so nobody is negotiating it at 4pm.

---

## Remember

You have already built harder things than this. You spent three months on it — deployed apps, wrote MCP servers, set up CI, shipped to real users.

Today is not about proving you can learn something new. **It is about finishing one thing properly, in one day, and being straight about what it does.**

That is a rarer skill than any of the ones you already have.

**Good luck. Ship it.**
