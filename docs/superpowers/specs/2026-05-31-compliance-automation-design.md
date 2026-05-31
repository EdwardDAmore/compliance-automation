# Compliance Automation System — Design Spec

**Date:** 2026-05-31  
**Author:** Eddie D'Amore  
**Status:** Approved  

---

## Overview

A GitHub Actions-based automation system that sends scheduled emails containing pre-written compliance prompts and direct links to Claude Projects. The goal is to reduce the friction of running recurring compliance workflows from "remember to do it and find the prompt" to a single click.

This is designed for a FinCEN-registered fiat-backed stablecoin issuer licensed as a money transmitter in 16+ states, operated by a small team of 2–5 people.

---

## Jobs

### Job 1: Weekly Regulatory Update
- **Purpose:** Reminds Eddie to run his standing regulatory update prompt every Monday morning.
- **Schedule:** Every Monday at 12:00 UTC (~8am ET in summer, ~7am ET in winter)
- **Sends to:** ee71715@gmail.com
- **Contains:** Placeholder regulatory compliance prompt + link to Claude Regulatory Project

### Job 2: Monthly InfoSec Newsletter
- **Purpose:** Reminds Eddie to run his monthly InfoSec review prompt on the 27th of each month (~3 days before end of month).
- **Schedule:** 27th of every month at 12:00 UTC
- **Sends to:** ee71715@gmail.com
- **Contains:** Placeholder InfoSec prompt + link to Claude InfoSec Project

---

## Architecture

### Approach Chosen: Shared Script + Separate Workflow Files

One Python script (`scripts/send_email.py`) handles all email sending logic. Each job has its own GitHub Actions workflow file that calls this shared script with different parameters (subject, prompt text, Claude Project link). This keeps the email logic in one place while making each job independently configurable.

**Why this over alternatives:**
- Easier to add new jobs in the future (copy a workflow file, fill in new values)
- Email logic is never duplicated
- Not as complex as GitHub matrix strategy
- Each workflow file is self-contained and readable on its own

---

## Folder Structure

```
compliance-automation/
├── .github/
│   └── workflows/
│       ├── weekly_regulatory.yml      ← GitHub Actions schedule for Job 1
│       └── monthly_infosec.yml        ← GitHub Actions schedule for Job 2
├── scripts/
│   └── send_email.py                  ← Shared email-sending engine
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-05-31-compliance-automation-design.md  ← This file
├── .gitignore                         ← Prevents accidental secret exposure
├── requirements.txt                   ← Python dependencies (minimal/empty)
├── README.md                          ← Portfolio-quality project description
└── learn.md                           ← Plain-English learning notes
```

---

## Data Flow

```
GitHub's internal clock
        │
        │  (cron schedule triggers)
        ▼
GitHub Actions runner
(free temporary virtual computer GitHub spins up)
        │
        │  reads values from GitHub Secrets vault
        ▼
.github/workflows/weekly_regulatory.yml
(or monthly_infosec.yml)
        │
        │  passes secrets as environment variables to Python
        ▼
scripts/send_email.py
        │
        │  composes plain-text email
        │  connects to Gmail via SMTP
        ▼
ee71715@gmail.com
```

---

## GitHub Secrets

All sensitive values are stored in GitHub's encrypted Secrets vault. Nothing is hardcoded in any file.

| Secret Name | Value Stored |
|---|---|
| `GMAIL_SENDER` | Bot Gmail address (e.g. compliance.bot@gmail.com) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not the real Gmail password) |
| `RECIPIENT_EMAIL` | ee71715@gmail.com |
| `REGULATORY_CLAUDE_URL` | Claude Project URL for regulatory job (placeholder until project is created) |
| `INFOSEC_CLAUDE_URL` | Claude Project URL for InfoSec job (placeholder until project is created) |

---

## Email Format

**Subject lines:**
- `[COMPLIANCE] Weekly Regulatory Update — Ready to Run`
- `[COMPLIANCE] Monthly InfoSec Newsletter — Ready to Run`

**Body structure (plain text):**
```
Hi Eddie,

Your [job name] is ready. Copy the prompt below and paste it into your Claude Project:

────────────────────────────────────────
[PLACEHOLDER PROMPT TEXT]
────────────────────────────────────────

Open your Claude Project here:
[CLAUDE PROJECT URL]

────────────────────────────────────────
Sent automatically | compliance-automation system
Scheduled: [schedule description]
────────────────────────────────────────
```

**Format decision:** Plain text (not HTML). More reliable across email clients, never triggers spam filters for formatting, simpler to maintain.

---

## Schedules (Cron Syntax)

| Job | Cron Expression | Explanation |
|---|---|---|
| Weekly Regulatory | `0 12 * * 1` | Minute 0, Hour 12 UTC, any day of month, any month, Monday (1) |
| Monthly InfoSec | `0 12 27 * *` | Minute 0, Hour 12 UTC, 27th day, any month, any day of week |

**UTC/ET note:** GitHub Actions runs in UTC. 12:00 UTC = ~8am ET in summer (EDT, UTC−4) and ~7am ET in winter (EST, UTC−5). This is acceptable — majority of the year is EDT.

**27th rationale:** Cron cannot express "3 days before end of month" natively since months have different lengths. The 27th is chosen as the closest fixed approximation: exactly 3 days before 30-day months, 4 days before 31-day months, and 1 day before February end.

---

## Python Script Design

**File:** `scripts/send_email.py`  
**Language:** Python 3.12+  
**Dependencies:** None external — uses only Python's built-in `smtplib` and `email` libraries  

**How it works:**
1. Reads all configuration from environment variables (set by the workflow from GitHub Secrets)
2. Composes a plain-text email with the prompt and Claude Project link
3. Connects to Gmail's SMTP server (`smtp.gmail.com`, port 587)
4. Authenticates using the Gmail App Password
5. Sends the email and exits

**Environment variables the script reads:**
- `GMAIL_SENDER` — the from address
- `GMAIL_APP_PASSWORD` — Gmail auth credential
- `RECIPIENT_EMAIL` — the to address
- `EMAIL_SUBJECT` — set by each workflow file
- `PROMPT_TEXT` — set by each workflow file
- `CLAUDE_PROJECT_URL` — set by each workflow file
- `JOB_SCHEDULE_DESC` — human-readable schedule description for email footer

---

## Security Considerations

- The repo is public on GitHub, so no secrets may appear in any file
- `.gitignore` will exclude any local `.env` test files
- GitHub Secrets are encrypted at rest and never exposed in logs
- Gmail App Password is scoped to this automation only — revoking it doesn't affect the real Gmail account

---

## Future Extensibility

Adding a new compliance job requires:
1. Creating a new workflow file in `.github/workflows/`
2. Adding any new Claude Project URL as a GitHub Secret
3. Zero changes to `send_email.py`

---

## Open Items

- [ ] Create dedicated Gmail account (e.g. `compliance.bot@gmail.com` or similar)
- [ ] Set up Gmail App Password after account creation
- [ ] Create two Claude Projects (Regulatory, InfoSec) and update `REGULATORY_CLAUDE_URL` and `INFOSEC_CLAUDE_URL` secrets when ready
- [ ] Replace placeholder prompts in workflow files with real compliance prompts
