# Evals — does it actually work?

**Copy this file to `evals/results.md` and fill it in.** That is the graded one.

```
cp evals/results.template.md evals/results.md
```

You need **at least 5 cases, real counts, and at least one honest FAIL with a
reason.** A file reading `PASS: 0, FAIL: 0, PENDING: 3` is not an eval and
scores nothing. A real failure you can explain scores well — that is the point
of the exercise.

Five ready-made cases are in `evals/cases/`. Run one like this:

```
cp evals/cases/02-vague-date.txt drop/
python run_once.py --drop
```

Then look at `records.json` and write down what you actually got — not what you
hoped for.

---

**Run by:** ______________________  **Date:** ______________________
**Model:** haiku  **Skill file version:** the one committed at ______________

| # | Case | What I expected | What I got | PASS / FAIL |
|---|---|---|---|---|
| 1 | `01-chatter-only` | 0 records. Tea, traffic and greetings are not work. | | |
| 2 | `02-vague-date` | "push it to Friday" → a real date, the correct Friday. | | |
| 3 | `03-same-task-twice` | **1** record for Sihala, not 3. | | |
| 4 | `04-mixed-language` | English titles, Urdu/Roman-Urdu preserved in `quote`. | | |
| 5 | `05-no-owner` | `owner: null`, `confidence: "low"`, a question in `ask`. No invented name. | | |
| 6 | *(your own real transcript)* | | | |

**Totals — PASS: ___  FAIL: ___**

---

## The failure I am not hiding

> Every build has one. Naming it scores better than pretending it isn't there.
> Here is a real one from the starter kit, as an example of the level of detail
> we want. **Replace it with your own.**

**Case 2 — vague date. FAIL.**

Input was *"push it to Friday"*, spoken on Tuesday 15 September 2026.
Expected `due: 2026-09-18`. Got `due: 2026-09-15` — today's date, a Tuesday.

**Why it happens:** the prompt hands the model today's date and asks it to
resolve a weekday, which is arithmetic, and the model is not reliably doing the
arithmetic. It anchored on the date it was given instead of counting forward to
the named weekday.

**What I would do about it:** either resolve weekday words in Python before the
record is saved — the weekday list is short and the maths is exact — or make
`validate()` reject a `due` that falls on the wrong weekday when the quote names
one, and push it into `ask` instead of saving a wrong date. **A wrong date is
worse than no date**, because a wrong one gets believed.

**What I actually did today, and why:** ______________________________________

---

## Notes

- Anything that surprised me: ______________________________________
- What I would test next if I had another hour: ______________________________
