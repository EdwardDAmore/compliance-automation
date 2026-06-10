# What I Built and What I Learned: compliance-automation

This document is my personal plain-English breakdown of the compliance-automation project —
what it does, how it works under the hood, why I made the decisions I made, and the lessons
I'll carry into future projects.

---

## The Big Picture: What Problem Did I Actually Solve?

Before this, running a compliance workflow meant: remember it's Monday, remember where the prompt is, open Claude, navigate to the right Project, paste the prompt. Four steps, each one a chance to forget or skip it.

Now it's: see email arrive, click link, paste. Done.

This is the real engineering lesson embedded in this project: **the best automation doesn't replace human judgment — it removes the friction around exercising it.** I still run the compliance workflows. I still review the output. But the system ensures I never miss the trigger.

---

## The Technical Architecture: How It Actually Works

Think of this system as a **relay race with four runners**:

1. **GitHub's internal clock (the starter gun)** — GitHub has a built-in scheduler that fires at exact times using a format called "cron." Cron is a Unix standard from the 1970s — it's been scheduling computer tasks longer than most of us have been alive. It looks cryptic (`0 12 * * 1`) but just means "minute 0, hour 12, any day, any month, Monday."

2. **GitHub Actions (the first runner)** — When the cron fires, GitHub spins up a free Ubuntu Linux virtual machine. Think of this as GitHub handing you a brand-new laptop, fully set up, just for this task. It reads a YAML configuration file (`.github/workflows/weekly_regulatory.yml`) that says "install Python, then run this script with these settings."

3. **Python's SMTP library (the second runner)** — The script (`scripts/send_email.py`) takes the baton. SMTP (Simple Mail Transfer Protocol) is the postal system of the internet — the standard protocol that every email server uses to accept and route messages. Python has SMTP built in; no third-party tools needed. The script connects to Gmail's SMTP server on port 587, encrypts the connection using STARTTLS (think of this as putting your letter in a sealed envelope before handing it to the postal worker), logs in with an App Password, and sends the email.

4. **Gmail (the finish line)** — The email arrives in Eddie's inbox with the prompt and a one-click link to the right Claude Project.

---

## The Files: What Each One Does

**`scripts/send_email.py`** — The engine. This is the only file that actually "does" something at runtime. It contains three functions:
- `build_email_body()` — assembles the email text from the inputs, like filling out a form letter
- `send_email()` — handles the SMTP connection and delivery
- `main()` — the entry point that reads environment variables and orchestrates the two functions above

**`.github/workflows/weekly_regulatory.yml`** and **`monthly_infosec.yml`** — The instruction sheets. These are YAML files (Yet Another Markup Language — a configuration format designed to be human-readable). GitHub reads these automatically. They define *when* to run (the cron schedule), *what* to install (Python 3.12), and *what settings to pass* to the script (subject line, prompt text, Claude URL). The `${{ secrets.NAME }}` syntax pulls values from GitHub's encrypted vault.

**`tests/test_send_email.py`** — The quality checker. Written *before* the script itself (TDD), these tests verify that `build_email_body()` returns text containing the right content, and that `send_email()` connects to the right server. We use "mocking" for the Gmail tests — we replace the real Gmail server with a fake that records what our code does, so we can check it without actually sending emails.

**`.gitignore`** — The bouncer. Git uploads everything it sees unless you tell it not to. This file is a blocklist: `.env` files (which might contain real passwords during local testing), `__pycache__` (Python's compiled file cache, which changes constantly and would clutter the commit history), and IDE files.

---

## Why These Technical Decisions?

**Why GitHub Actions and not a local cron job?**
A local cron job would require my computer to be running and connected 24/7. GitHub Actions runs on GitHub's infrastructure for free, doesn't depend on my machine, and has a built-in UI for checking whether jobs ran successfully. It's the right tool for this specific problem.

**Why plain text email and not HTML?**
HTML emails look slicker but introduce real problems: spam filters are more aggressive with HTML, rendering varies across email clients, and maintenance is harder. Since these emails are going to one person (me) and the content is text I'll copy-paste anyway, plain text is strictly better. This is an example of the engineering principle: *choose the simplest solution that fully solves the problem.*

**Why a shared script instead of separate scripts per job?**
If I have separate scripts, I need to fix bugs in multiple places. If the email format changes, I edit one file and both jobs get the update. This is the DRY principle: Don't Repeat Yourself. Code that exists in one place has one bug count; code that exists in two places has at least two.

**Why no external Python libraries?**
`smtplib` and `email.mime` are built into Python — they ship with every Python installation. Adding an external library (like `sendgrid` or `boto3`) creates a dependency: something that can break, need updating, or disappear. YAGNI: You Ain't Gonna Need It. The built-in tools do everything we need.

**Why store the prompts in the YAML files instead of a database?**
The prompts are configuration, not data. They change rarely and are not secret. Keeping them in the YAML file means they're version-controlled in git (I can see exactly what changed and when), don't require a database, and are editable by anyone with access to the repo. When the prompts need updating, I edit the file directly.

---

## Secrets: The Most Important Concept in This Project

If you remember one thing from this project, let it be this: **never put passwords or sensitive values in code files that get uploaded to GitHub.**

GitHub repos can be public. Even private repos have been accidentally made public. Even if yours stays private, credentials in code are a bad habit that leads to data breaches.

The solution is a two-step pattern I'll use in every project:
1. Store sensitive values in a secure vault (here: GitHub Secrets)
2. Have your code read them from environment variables at runtime

An environment variable is a value that exists in the running process's memory but never in any file. The Python syntax is `os.environ['SECRET_NAME']` — "read this value from the environment." GitHub Actions sets these environment variables from the encrypted Secrets vault just before the script runs.

This is the same pattern used by every major tech company for secrets management. Learning it early is valuable.

---

## Cron Syntax: Demystified

Cron has five fields, each separated by a space:

```
┌───────────── minute (0–59)
│ ┌───────────── hour (0–23, UTC)
│ │ ┌───────────── day of month (1–31)
│ │ │ ┌───────────── month (1–12)
│ │ │ │ ┌───────────── day of week (0–7, where 0 and 7 both mean Sunday)
│ │ │ │ │
0 7 * * 1    → Every Monday at 07:00 UTC (~3am ET)
0 7 27 * *   → 27th of every month at 07:00 UTC (~3am ET)
* * * * *     → Every minute (useful for testing, terrible for production)
```

The `*` means "every value" for that field. So `* * * * 1` means "every minute of every hour of every day that is a Monday" — probably not what you want.

---

## What I Ran Into: Bugs and Surprises

**pip wasn't installed.** Python was installed on my WSL system, but pip (Python's package manager) wasn't included. This is a known quirk of Debian/Ubuntu systems — they ship Python but not pip, to avoid polluting system packages. We solved it by downloading pip directly from the Python Packaging Authority (pip's official source) and installing it to the user directory only, no system changes required.

**Virtual environments were also unavailable.** The `python3-venv` module (needed to create isolated Python environments) also wasn't installed. Since we only needed pytest for testing and all runtime libraries are built-in, we installed pytest to the user directory directly rather than into a virtual environment. Not the cleanest solution but appropriate for a personal development machine.

**sudo wasn't available interactively.** When trying to install system packages, sudo required an interactive terminal (a real password prompt), which wasn't available through the automated tool session. The lesson: always check what's installed before assuming standard tools are available.

**GitHub tokens need the `workflow` scope.** When pushing `.github/workflows/` files to GitHub, a Personal Access Token needs both `repo` AND `workflow` scopes checked. A token with only `repo` scope will fail with the error "refusing to allow a Personal Access Token to create or update workflow files." When generating tokens for projects that include GitHub Actions, always check both boxes.

**Git credential prompts don't work in non-interactive sessions.** When running git push through an automated tool session (like Claude Code), git can't show a password prompt. The solution is to embed the token directly in the remote URL: `https://USERNAME:TOKEN@github.com/REPO.git`. This stores the credentials in `.git/config` locally — safe because `.git/` is never uploaded to GitHub. Never paste your token into any tracked file.

**"Re-run all jobs" is not the same as "Run workflow."** Inside a GitHub Actions run, "Re-run all jobs" replays that specific run using the same code from when it originally ran. It will always produce the same output — including old placeholder prompts. To test updated code, you must go back to the workflow list and click "Run workflow" to create a brand new run from the latest commit.

**Old runs always show old content.** GitHub Actions logs are a historical record. If you updated a prompt and trigger a new test, make sure you're looking at the NEW run (at the top of the list), not an old one. Old runs are frozen snapshots and will always show whatever was in the workflow file at the time they ran.

**Bash can't source .env files with special characters or multi-line values.** The `source .env` command in bash treats every line as a shell command. If your .env file contains a long prompt with parentheses, dashes, colons, or multiple lines, bash will try to execute them and produce confusing errors. The fix is to use Python to read the .env file instead — Python treats it as plain text and handles any content safely. Long prompts also belong in their own plain text file (like `test_prompt.txt`) rather than crammed into a .env variable.

**A `.gitignore` pattern can be too broad.** The pattern `.env.*` (intended to block `.env.local`, `.env.production`, etc.) also accidentally matches `.env.example` — a file that's safe to commit because it contains no real values. The fix was to rename it to `env.example` (no leading dot). When writing gitignore patterns, test them carefully: `git check-ignore -v filename` will tell you which rule is blocking a file.

**Saving a file is not the same as committing it.** When you edit a file in any editor and save it, git sees the change but does nothing with it. Git only tracks changes you explicitly stage (`git add`) and commit (`git commit`). The mental model: saving = telling your editor "keep this," staging = telling git "watch this," committing = telling git "record this permanently." All three steps are needed before pushing.

---

## Potential Pitfalls and How to Avoid Them

**Gmail App Password gotcha:** Gmail requires you to enable "2-Step Verification" before you can create App Passwords. If the script fails to authenticate, check that 2FA is enabled on the bot Gmail account first.

**GitHub Actions cron delay:** GitHub's free cron scheduler can run significantly late when GitHub is busy — the official documentation says "up to 15 minutes," but in practice this project observed delays of 4–7 hours. This is because free-tier jobs sit in a shared queue behind paid customers, and during peak hours the backlog can be enormous. The fix was to schedule the cron for 3am ET (7:00 UTC) instead of 8am ET, so even with a several-hour delay, the email still lands in the inbox before the workday begins. The lesson: **if the delivery time matters, don't schedule for the exact time you need — schedule hours early and let the delays absorb into the buffer. Don't trust the documented maximum; test with your actual account tier.**

**YAML indentation is not forgiving:** YAML uses indentation (spaces, not tabs) to define structure. If the YAML file has a tab character instead of spaces, or misaligned indentation, GitHub Actions will fail with a cryptic error. If a workflow fails immediately with a parse error, indentation is the first thing to check.

**The UTC vs. local time gotcha:** GitHub Actions has no concept of Daylight Saving Time. If the email arrives an hour early in winter, it's because the cron is set to a UTC time that's 4 hours behind ET in summer but 5 hours in winter.

**What happens if the email fails to send?** GitHub Actions marks the job as failed and sends a notification email to the repo owner. A future improvement would be to add retry logic to the Python script.

---

## What Good Engineers Think About That I'm Learning

**Separation of concerns:** `send_email.py` only knows how to send email. The workflow YAML only knows the schedule and configuration. Neither one bleeds into the other's territory. This makes each piece easier to test, debug, and change independently.

**Reproducibility:** Because all configuration is in version-controlled files and all secrets are in a vault, this system could be reproduced from scratch in 20 minutes. Nothing exists only in someone's head or on a particular machine.

**The cheapest test is one that doesn't touch the network:** The `@patch` decorator in our tests replaces the real Gmail server with a fake. This means tests run instantly, work offline, and never fail because of network issues. Mock what you don't control; test what you own.

**Small, focused files:** `send_email.py` does exactly one thing: send an email. If we later need to send Slack messages instead, we write `send_slack.py` — we don't modify the email file. This is the Single Responsibility Principle, and it makes maintenance dramatically easier.

**TDD builds confidence:** Writing the tests first felt counterintuitive — how do you test something that doesn't exist? But it forced clear thinking about exactly what the code needed to do before writing a single line of it. When all 10 tests turned green after writing the script, there was genuine confidence that the code worked — not just a hope.
