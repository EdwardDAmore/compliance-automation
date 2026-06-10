# compliance-automation

> Automated compliance workflow reminders for a FinCEN-registered stablecoin issuer — built with GitHub Actions and Python.

**Status: Live and running.** Two scheduled jobs are actively delivering compliance workflow prompts to my inbox every week and every month.

A scheduled automation system that delivers compliance workflow prompts directly to my inbox on a recurring schedule, so running weekly regulatory reviews and monthly InfoSec audits is reduced to a single click.

---

## The Problem It Solves

Running a licensed money transmitter means recurring compliance work that cannot slip: weekly regulatory monitoring, monthly InfoSec reviews, and more. With a team of 2–5 people, there's no dedicated compliance staff to own these reminders. The workflows exist; the friction was remembering to run them.

This system eliminates that friction by automatically sending an email containing the exact prompt to paste into Claude, with a direct link to the relevant Claude Project — so running a compliance workflow takes one click, not "remember, find, copy, navigate."

---

## How It Works

```
GitHub's scheduler (cron)
        │
        ▼
GitHub Actions runner (free Ubuntu VM)
        │  reads from GitHub Secrets vault
        ▼
Python script (scripts/send_email.py)
        │  builds email body with prompt + Claude link
        ▼
Gmail SMTP → Eddie's inbox
```

1. GitHub's built-in scheduler fires at the configured time (cron schedule)
2. GitHub spins up a free Ubuntu virtual machine
3. The VM runs `scripts/send_email.py`, pulling credentials from GitHub Secrets
4. The script sends a plain-text email via Gmail SMTP containing the compliance prompt and a direct link to the relevant Claude Project
5. Eddie clicks the link, pastes the prompt, runs the workflow

---

## Scheduled Jobs

| Job | Schedule | Purpose |
|---|---|---|
| Weekly Regulatory Update | Every Monday at ~3am ET | Regulatory monitoring prompt + Claude link |
| Monthly InfoSec Newsletter | 27th of every month at ~3am ET | InfoSec review prompt + Claude link |

Both jobs run at 3am ET (07:00 UTC) — scheduled early to give GitHub's queue time to process so emails land in the inbox before the workday starts.

Both jobs use the same Python script (`scripts/send_email.py`) with different configuration passed via environment variables.

---

## Project Structure

```
compliance-automation/
├── .github/
│   └── workflows/
│       ├── weekly_regulatory.yml   ← Job 1 schedule and config
│       └── monthly_infosec.yml     ← Job 2 schedule and config
├── scripts/
│   └── send_email.py               ← Shared email engine
├── tests/
│   └── test_send_email.py          ← Automated tests (TDD)
├── docs/
│   └── superpowers/
│       ├── specs/                  ← Design specification
│       └── plans/                  ← Implementation plan
├── .gitignore
├── requirements.txt
├── README.md
└── learn.md
```

---

## Tech Stack

- **Python 3.12** — standard library only (`smtplib`, `email.mime`) — no external dependencies for the runtime script
- **GitHub Actions** — free scheduled job runner; cron syntax for scheduling
- **Gmail SMTP** — email delivery via App Password authentication
- **pytest** — local test runner (TDD)
- **GitHub Secrets** — encrypted storage for credentials; nothing sensitive in code

---

## Adding a New Compliance Job

1. Copy `.github/workflows/weekly_regulatory.yml` to a new file (e.g. `quarterly_bsa_review.yml`)
2. Update the `cron` schedule, `EMAIL_SUBJECT`, `JOB_NAME`, `JOB_SCHEDULE_DESC`, and `PROMPT_TEXT`
3. Add a new GitHub Secret for the Claude Project URL (e.g. `BSA_CLAUDE_URL`) and reference it in the new workflow
4. Push to GitHub — the new job is live

No changes to `scripts/send_email.py` required.

---

## Security

- **No secrets in code:** All credentials (Gmail address, App Password, recipient email, Claude Project URLs) are stored in GitHub's encrypted Secrets vault and injected at runtime
- **Public repo safe:** The repo is intentionally public as a portfolio piece; `.gitignore` prevents accidental credential exposure via local `.env` files
- **App Password scoped:** The Gmail App Password is specific to this automation — revoking it has no effect on the Gmail account itself
- **Minimal surface area:** The runtime script has no external dependencies, reducing supply-chain risk

---

## Local Development Setup

```bash
# Clone the repo
git clone https://github.com/EdwardDAmore/compliance-automation.git
cd compliance-automation

# Install test dependencies
python3 -m pip install -r requirements.txt

# Run the tests
python3 -m pytest tests/ -v
```

---

## Status

| Job | Status | Last Verified |
|---|---|---|
| Weekly Regulatory Update | ✅ Live | May 2026 |
| Monthly InfoSec Newsletter | ✅ Live | May 2026 |

Both jobs have been manually tested end-to-end and confirmed delivering emails with real compliance prompts and Claude Project links.

---

## About

Built by [Edward D'Amore](https://github.com/EdwardDAmore) — operator of a FinCEN-registered fiat-backed stablecoin issuer licensed as a money transmitter in 16+ US states.
