---
name: worklog
description: Turn a meeting transcript or a work message into structured work records - tasks, decisions and blockers - with an owner, a due date and the exact words it came from. Use when reading a sync transcript, a voice note or a status message.
---

# Worklog — reading work out of a conversation

**This file is your prompt. `run_once.py` reads it every time it runs.**

Change a rule here, save, run the job again, and the behaviour changes — without
touching a single line of Python. That is the whole point of a skill file.

> **⬇ THIS IS YOUR MAIN DELIVERABLE.** Most of your mark comes from what is
> written below. Make it yours.

---

## What you are reading

A work conversation from a Pakistani education organisation. It may mix English,
Urdu and Roman Urdu in the same sentence. Extract only **real work items**.
Ignore greetings, small talk, and chatter about tea.

## What to pull out

Return a JSON array. Every element has exactly these fields:

| Field | Value |
|---|---|
| `type` | `"task"` · `"decision"` · `"blocker"` |
| `title` | Short, English, specific. Someone who was not in the room should understand it. |
| `owner` | The person's name, or `null` if genuinely unclear |
| `due` | `"YYYY-MM-DD"`, or `null` if no deadline was stated |
| `quote` | The exact words this came from |
| `confidence` | `"high"` or `"low"` — **only these two words** |
| `ask` | The one question you would put to a human, or `null` |

## The four rules

**1 · Decide what it is.** A *task* is something someone will do. A *decision* is
something the group settled. A *blocker* is something stopping work. If it is
none of these, it is chatter — leave it out. Extracting the tea order is as wrong
as missing a real task.

**2 · Resolve the owner and the date.** "Ali will look at it next week" is owner
`Ali` and a real calendar date — not the words "next week". Count from today's
date, which is given to you at the top of the prompt. **Check the weekday before
you answer**; "Friday" is a different date depending on when you are reading.

**3 · Do not create something that already exists.** You are given the list of
items already open. If the conversation refers to one of them, reuse its exact
title so it is recognised as the same item. Ten people reporting one problem is
**one** item, not ten.

**4 · Ask rather than guess.** If ownership or a date is vague, set the field to
`null`, set `confidence` to `"low"`, and write the question in `ask`.
**Guessing an owner is worse than asking.** A system that quietly invents an
owner is worse than useless, because people believe it.

---

## A worked example

This is the most useful thing in this file, and it is the thing you should
copy the shape of. One real line in, one exact record out.

**In** — a line from `sample_transcript.txt`:

```
[10:07] Rifat: haan theek hai, we'll push it to Friday. Sabeen ko main bata dungi.
```

**Out** — exactly this, assuming today is Tuesday 15 September 2026:

```json
{
  "type": "task",
  "title": "Tell Sabeen the LP review deadline moved to Friday",
  "owner": "Rifat",
  "due": "2026-09-18",
  "quote": "we'll push it to Friday. Sabeen ko main bata dungi.",
  "confidence": "high",
  "ask": null
}
```

Read what that example is actually teaching:

- the **title is English and specific** — "push it to Friday" would mean nothing
  in a report three weeks from now
- the **owner is Rifat**, the person who said *"main bata dungi"* — not Sabeen,
  who is being told
- the **due date is a real Friday**, counted forward from today. `2026-09-15` is
  a Tuesday and would be wrong. **This is the field that goes wrong most often —
  check the weekday before you answer.**
- the **quote keeps the original words**, Roman Urdu and all. Never translate the
  quote; it is the evidence.

Now add your own. One line from your own work, and the record you want back.

---

## Make this yours

The rules above are a starting point. Your job is different from everyone else's,
so your rules should be too. Things worth adding:

- **Your own vocabulary.** A coach might add: *"an observation counts as a task
  only if a school is named."* An RM might add: *"treat any teacher-name list as a
  roster correction, not a task."*
- **What to always ignore.** Attendance chatter? Greetings that run four lines?
- **Your own item type.** Nothing stops you adding `"risk"` or `"request"` — just
  remember to allow it in `validate()` too, or it will be dropped.
- **A worked example.** Paste in one real line from your own work and the exact
  record you want back. This is the single most effective thing you can add.
