# Compliance Automation System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub Actions system that sends scheduled emails containing compliance prompts and Claude Project links to Eddie's inbox.

**Architecture:** One shared Python script (`scripts/send_email.py`) reads configuration from environment variables and sends plain-text email via Gmail SMTP. Two separate GitHub Actions workflow files (one per job) define the schedule and pass configuration (subject, prompt, Claude URL) to the shared script via environment variables sourced from GitHub Secrets.

**Tech Stack:** Python 3.12 (stdlib only: `smtplib`, `email.mime`), GitHub Actions (YAML workflows), Gmail SMTP with App Password, pytest for local testing.

---

## File Map

Files to create (all new — project skeleton exists with only `docs/` folder):

| File | Purpose |
|---|---|
| `scripts/send_email.py` | Shared email engine — reads env vars, builds body, sends via Gmail SMTP |
| `tests/test_send_email.py` | Unit tests for the email builder and SMTP sender |
| `.github/workflows/weekly_regulatory.yml` | Schedules Job 1 every Monday at 12:00 UTC |
| `.github/workflows/monthly_infosec.yml` | Schedules Job 2 on the 27th of every month at 12:00 UTC |
| `.gitignore` | Prevents secrets and junk files from being uploaded to GitHub |
| `requirements.txt` | Lists pytest as the only dependency (for local testing) |
| `README.md` | Portfolio-quality project description |
| `learn.md` | Plain-English explanation of the whole project for Eddie's learning |

---

## Task 1: Install pip and initialize the git repository

**Files:** No files created — this is environment setup.

> **Plain English:** Before we can write any code, we need to set up two things: (1) pip, which is Python's package manager (like an app store for Python add-ons), and (2) git, which tracks all changes to our code so we can upload it to GitHub. Git is already installed; we just need to tell it this folder is a project.

- [ ] **Step 1: Install pip**

```bash
sudo apt-get install -y python3-pip
```

Expected output (last lines):
```
Setting up python3-pip ...
Processing triggers for ...
```

- [ ] **Step 2: Verify pip works**

```bash
python3 -m pip --version
```

Expected output (exact version may differ):
```
pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
```

- [ ] **Step 3: Initialize git in the project folder**

> This creates a hidden `.git` folder that tracks all your file changes. Think of it as turning on a security camera for your code.

```bash
cd /home/eddie/claude/compliance-automation && git init && git checkout -b main
```

Expected output:
```
Initialized empty Git repository in /home/eddie/claude/compliance-automation/.git/
Switched to a new branch 'main'
```

- [ ] **Step 4: Connect this folder to your GitHub repository**

> This tells git "when I push code, send it to THIS GitHub repo."

```bash
git remote add origin https://github.com/EdwardDAmore/compliance-automation.git
```

No output is expected — silence means success.

- [ ] **Step 5: Verify the remote was added**

```bash
git remote -v
```

Expected output:
```
origin  https://github.com/EdwardDAmore/compliance-automation.git (fetch)
origin  https://github.com/EdwardDAmore/compliance-automation.git (push)
```

---

## Task 2: Create project folder skeleton

**Files:** Creates the folder structure only — no code yet.

> **Plain English:** GitHub Actions requires a very specific folder name (`.github/workflows`) to find your scheduled jobs. We're creating that structure now, plus a `scripts/` folder for the Python code and a `tests/` folder for the test files.

- [ ] **Step 1: Create all required folders**

```bash
mkdir -p /home/eddie/claude/compliance-automation/.github/workflows
mkdir -p /home/eddie/claude/compliance-automation/scripts
mkdir -p /home/eddie/claude/compliance-automation/tests
```

No output expected.

- [ ] **Step 2: Verify the structure looks correct**

```bash
find /home/eddie/claude/compliance-automation -type d | sort
```

Expected output:
```
/home/eddie/claude/compliance-automation
/home/eddie/claude/compliance-automation/.github
/home/eddie/claude/compliance-automation/.github/workflows
/home/eddie/claude/compliance-automation/docs
/home/eddie/claude/compliance-automation/docs/superpowers
/home/eddie/claude/compliance-automation/docs/superpowers/plans
/home/eddie/claude/compliance-automation/docs/superpowers/specs
/home/eddie/claude/compliance-automation/scripts
/home/eddie/claude/compliance-automation/tests
```

---

## Task 3: Write .gitignore and requirements.txt

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`

> **Plain English:** `.gitignore` is a list of files git should NEVER upload to GitHub. This is our security net — if we ever accidentally create a file with a real password in it, `.gitignore` stops it from being uploaded. `requirements.txt` lists the Python tools we need (just `pytest` for running tests locally).

- [ ] **Step 1: Write .gitignore**

Create `/home/eddie/claude/compliance-automation/.gitignore` with this exact content:

```
# Local environment files — NEVER commit these (they contain real passwords)
.env
*.env
.env.*
.env.local

# Python compiled files — auto-generated when Python runs, not needed in the repo
__pycache__/
*.pyc
*.pyo
*.pyd

# Python test and coverage cache files — auto-generated by pytest
.pytest_cache/
.coverage
htmlcov/

# macOS auto-generated files (irrelevant to the project)
.DS_Store

# IDE/editor configuration files (personal to each developer, not project files)
.vscode/
.idea/
*.swp
*.swo
```

- [ ] **Step 2: Write requirements.txt**

Create `/home/eddie/claude/compliance-automation/requirements.txt` with this exact content:

```
# pytest is a tool for running automated tests locally.
# It is NOT needed on GitHub Actions (the workflow runs the script directly).
# Install with: python3 -m pip install -r requirements.txt
pytest
```

- [ ] **Step 3: Install pytest locally**

```bash
cd /home/eddie/claude/compliance-automation && python3 -m pip install -r requirements.txt
```

Expected output (last lines):
```
Successfully installed pytest-...
```

- [ ] **Step 4: Verify pytest is available**

```bash
python3 -m pytest --version
```

Expected output:
```
pytest 8.x.x
```

- [ ] **Step 5: Commit**

```bash
cd /home/eddie/claude/compliance-automation && git add .gitignore requirements.txt && git commit -m "chore: add gitignore and requirements"
```

Expected output:
```
[main (root-commit) xxxxxxx] chore: add gitignore and requirements
 2 files changed, ...
```

---

## Task 4: Write failing tests for send_email.py (TDD — tests first)

**Files:**
- Create: `tests/test_send_email.py`

> **Plain English:** In professional software development, you write your tests BEFORE you write the code. This sounds backwards, but it's brilliant — it forces you to think clearly about exactly what your code should do before you write it. We'll write tests that currently fail (because `send_email.py` doesn't exist yet), then write the code to make them pass. This technique is called Test-Driven Development (TDD).

- [ ] **Step 1: Write the test file**

Create `/home/eddie/claude/compliance-automation/tests/test_send_email.py` with this exact content:

```python
# tests/test_send_email.py
#
# These are automated tests for send_email.py.
# Run them with: python3 -m pytest tests/ -v
#
# We test two things:
#   1. build_email_body() — does it produce the right email content?
#   2. send_email()       — does it connect to Gmail correctly?
#
# For the Gmail tests, we use "mocking" — we pretend to be Gmail's server
# so we don't actually send real emails every time we run tests.

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Tell Python where to find our send_email module.
# sys.path is Python's list of folders to search when importing code.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from send_email import build_email_body, send_email


class TestBuildEmailBody(unittest.TestCase):
    """Tests for the function that builds the email body text."""

    def setUp(self):
        """
        setUp() runs before every test in this class.
        We define reusable test data here so we don't repeat ourselves.
        """
        self.prompt = "Review all FinCEN guidance published this week."
        self.claude_url = "https://claude.ai/project/proj_test123"
        self.job_name = "Weekly Regulatory Update"
        self.schedule = "Every Monday at ~8am ET"

    def test_prompt_appears_in_body(self):
        """The email body must contain the full prompt text so Eddie can copy it."""
        body = build_email_body(self.prompt, self.claude_url, self.job_name, self.schedule)
        self.assertIn(self.prompt, body)

    def test_claude_url_appears_in_body(self):
        """The email body must contain the Claude Project link for one-click access."""
        body = build_email_body(self.prompt, self.claude_url, self.job_name, self.schedule)
        self.assertIn(self.claude_url, body)

    def test_job_name_appears_in_body(self):
        """The email body must include the job name so Eddie knows which workflow this is."""
        body = build_email_body(self.prompt, self.claude_url, self.job_name, self.schedule)
        self.assertIn(self.job_name, body)

    def test_schedule_appears_in_body(self):
        """The email footer must show the schedule so Eddie knows when this runs."""
        body = build_email_body(self.prompt, self.claude_url, self.job_name, self.schedule)
        self.assertIn(self.schedule, body)

    def test_greeting_in_body(self):
        """The email must start with a personal greeting."""
        body = build_email_body(self.prompt, self.claude_url, self.job_name, self.schedule)
        self.assertIn("Hi Eddie", body)

    def test_returns_a_string(self):
        """build_email_body must return a string (not None or some other type)."""
        body = build_email_body(self.prompt, self.claude_url, self.job_name, self.schedule)
        self.assertIsInstance(body, str)


class TestSendEmailFunction(unittest.TestCase):
    """
    Tests for the function that connects to Gmail and sends the email.

    We use @patch to replace smtplib.SMTP with a fake (mock) version.
    This means no real email is sent during tests — we just check that
    our code calls Gmail's server in the right way.
    """

    @patch('send_email.smtplib.SMTP')
    def test_connects_to_gmail_smtp_server(self, mock_smtp_class):
        """Must connect to Gmail's SMTP server at smtp.gmail.com on port 587."""
        # Set up the fake Gmail server
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        # Verify we connected to the right server and port
        mock_smtp_class.assert_called_once_with('smtp.gmail.com', 587)

    @patch('send_email.smtplib.SMTP')
    def test_uses_starttls_encryption(self, mock_smtp_class):
        """Must call starttls() to encrypt the connection before sending passwords."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        # starttls() upgrades the connection to encrypted (TLS) — must be called
        mock_server.starttls.assert_called_once()

    @patch('send_email.smtplib.SMTP')
    def test_logs_in_with_sender_and_app_password(self, mock_smtp_class):
        """Must authenticate with the sender address and app password."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        # Must log in with the bot's Gmail address and the app password
        mock_server.login.assert_called_once_with("bot@gmail.com", "apppassword123")

    @patch('send_email.smtplib.SMTP')
    def test_sends_to_correct_recipient(self, mock_smtp_class):
        """Must send the email to the correct recipient address."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        # sendmail() is the call that actually delivers the email
        call_args = mock_server.sendmail.call_args
        # The second argument to sendmail() is the recipient
        self.assertEqual(call_args[0][1], "eddie@gmail.com")


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm they FAIL**

> These tests should fail right now because `send_email.py` doesn't exist yet. A failure here is correct and expected — it proves our tests are actually checking something real.

```bash
cd /home/eddie/claude/compliance-automation && python3 -m pytest tests/ -v
```

Expected output (something like):
```
ERRORS
tests/test_send_email.py - ModuleNotFoundError: No module named 'send_email'
```

If you see an error about `send_email` not being found — that's exactly right. Move to Task 5.

- [ ] **Step 3: Commit the failing tests**

```bash
cd /home/eddie/claude/compliance-automation && git add tests/test_send_email.py && git commit -m "test: add failing tests for send_email (TDD)"
```

---

## Task 5: Write send_email.py to make the tests pass

**Files:**
- Create: `scripts/send_email.py`

> **Plain English:** Now we write the actual code that makes our tests pass. `send_email.py` is the engine of the whole system — it's the one file that knows how to actually send an email. It reads its configuration from environment variables (like reading settings from a secure vault) so no secrets ever live in the code itself.

- [ ] **Step 1: Write send_email.py**

Create `/home/eddie/claude/compliance-automation/scripts/send_email.py` with this exact content:

```python
# scripts/send_email.py
#
# This is the shared email-sending engine for the compliance automation system.
# It is called by GitHub Actions workflows (weekly_regulatory.yml and monthly_infosec.yml).
#
# How it works:
#   1. Reads configuration (email addresses, passwords, prompt text) from environment variables
#   2. Builds a plain-text email body containing the prompt and Claude Project link
#   3. Connects to Gmail's mail server (SMTP) and sends the email
#
# Security: All sensitive values (passwords, URLs) come from environment variables
# that GitHub Actions sets from encrypted GitHub Secrets — nothing is hardcoded here.

import smtplib
import os
from email.mime.text import MIMEText  # MIMEText formats plain-text email messages


def build_email_body(prompt_text, claude_url, job_name, schedule_desc):
    """
    Builds the plain-text email body.

    Think of this function as filling out a form letter template.
    It takes four pieces of information and assembles them into
    a formatted email body that Eddie can read and act on.

    Parameters:
        prompt_text   - the compliance prompt to copy into Claude
        claude_url    - the direct link to the Claude Project
        job_name      - human-readable name (e.g. "Weekly Regulatory Update")
        schedule_desc - human-readable schedule (e.g. "Every Monday at ~8am ET")

    Returns:
        A formatted string ready to be used as an email body.
    """
    # Visual divider line used to separate sections of the email
    divider = "─" * 40  # Unicode horizontal line character, repeated 40 times

    return f"""Hi Eddie,

Your {job_name} is ready. Copy the prompt below and paste it into your Claude Project:

{divider}
{prompt_text}
{divider}

Open your Claude Project here:
{claude_url}

{divider}
Sent automatically | compliance-automation system
Scheduled: {schedule_desc}
{divider}"""


def send_email(sender, app_password, recipient, subject, body):
    """
    Sends an email via Gmail's SMTP server.

    SMTP (Simple Mail Transfer Protocol) is the standard protocol that email
    programs use to send mail — think of it as the postal van that carries your letter.

    Port 587 is the standard secure port for outgoing email (called "submission" port).
    STARTTLS upgrades the connection to encrypted BEFORE we send our password,
    so the password is never transmitted in plain text.

    Parameters:
        sender       - the Gmail address sending the email (e.g. bot@gmail.com)
        app_password - Gmail App Password (a special password just for this automation)
        recipient    - where to send the email (e.g. ee71715@gmail.com)
        subject      - the email subject line
        body         - the plain-text email body (from build_email_body)
    """
    # MIMEText creates a properly formatted email message object.
    # 'plain' means plain text — no HTML, no formatting.
    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Open a connection to Gmail's SMTP server.
    # The 'with' block automatically closes the connection when done,
    # even if something goes wrong — like a try/finally block.
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()      # "Hello" — introduces our computer to Gmail's server
        server.starttls()  # Upgrades connection to encrypted (TLS/SSL)
        server.login(sender, app_password)  # Authenticate with Gmail
        server.sendmail(sender, recipient, msg.as_string())  # Send the email


def main():
    """
    Main entry point — called when GitHub Actions runs this script.

    Reads all configuration from environment variables, then calls
    build_email_body() and send_email() to do the actual work.

    Environment variables are set by the GitHub Actions workflow file,
    which reads them from GitHub Secrets. This keeps all sensitive values
    out of the code and in an encrypted vault.
    """
    # Read all required configuration from environment variables.
    # If any variable is missing, Python raises a KeyError, which stops
    # the job and shows an error in GitHub Actions — useful for debugging.
    sender = os.environ['GMAIL_SENDER']
    app_password = os.environ['GMAIL_APP_PASSWORD']
    recipient = os.environ['RECIPIENT_EMAIL']
    subject = os.environ['EMAIL_SUBJECT']
    prompt_text = os.environ['PROMPT_TEXT']
    claude_url = os.environ['CLAUDE_PROJECT_URL']
    job_name = os.environ['JOB_NAME']
    schedule_desc = os.environ['JOB_SCHEDULE_DESC']

    # Build the email body using the template function
    body = build_email_body(prompt_text, claude_url, job_name, schedule_desc)

    # Send the email
    send_email(sender, app_password, recipient, subject, body)

    # Print a success message visible in the GitHub Actions log
    print(f"Email sent successfully to {recipient}")


# This block only runs when the script is executed directly (e.g. python3 send_email.py).
# It does NOT run when the script is imported by the test file.
if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the tests and confirm they all PASS**

```bash
cd /home/eddie/claude/compliance-automation && python3 -m pytest tests/ -v
```

Expected output:
```
tests/test_send_email.py::TestBuildEmailBody::test_greeting_in_body PASSED
tests/test_send_email.py::TestBuildEmailBody::test_job_name_appears_in_body PASSED
tests/test_send_email.py::TestBuildEmailBody::test_claude_url_appears_in_body PASSED
tests/test_send_email.py::TestBuildEmailBody::test_prompt_appears_in_body PASSED
tests/test_send_email.py::TestBuildEmailBody::test_returns_a_string PASSED
tests/test_send_email.py::TestBuildEmailBody::test_schedule_appears_in_body PASSED
tests/test_send_email.py::TestSendEmailFunction::test_connects_to_gmail_smtp_server PASSED
tests/test_send_email.py::TestSendEmailFunction::test_logs_in_with_sender_and_app_password PASSED
tests/test_send_email.py::TestSendEmailFunction::test_sends_to_correct_recipient PASSED
tests/test_send_email.py::TestSendEmailFunction::test_uses_starttls_encryption PASSED

10 passed in 0.xxs
```

If any test fails, read the error message carefully — it will tell you exactly which assertion failed and why.

- [ ] **Step 3: Commit**

```bash
cd /home/eddie/claude/compliance-automation && git add scripts/send_email.py && git commit -m "feat: add shared email sender script"
```

---

## Task 6: Write the weekly regulatory workflow

**Files:**
- Create: `.github/workflows/weekly_regulatory.yml`

> **Plain English:** A YAML file is a configuration file written in a format GitHub understands. This particular file tells GitHub: "Every Monday at 12:00 UTC, spin up a free computer, install Python, and run our email script with these specific settings." The `${{ secrets.NAME }}` syntax is how GitHub pulls values out of its encrypted Secrets vault at runtime.

- [ ] **Step 1: Write the workflow file**

Create `/home/eddie/claude/compliance-automation/.github/workflows/weekly_regulatory.yml` with this exact content:

```yaml
# .github/workflows/weekly_regulatory.yml
#
# GitHub Actions workflow for Job 1: Weekly Regulatory Update
#
# This file tells GitHub WHEN to run the job and WHAT settings to use.
# The actual email-sending logic lives in scripts/send_email.py.
#
# To trigger this manually (for testing):
#   Go to GitHub repo → Actions tab → "Weekly Regulatory Update" → "Run workflow"

name: Weekly Regulatory Update

# WHEN to run this workflow
on:
  schedule:
    # Cron format: minute  hour  day-of-month  month  day-of-week
    #                 0      12       *            *        1
    # Translation: At 12:00 UTC every Monday
    # (~8am ET in summer/EDT, ~7am ET in winter/EST)
    - cron: '0 12 * * 1'

  # workflow_dispatch lets you trigger this manually from GitHub's website.
  # This is essential for testing — you don't want to wait until Monday!
  workflow_dispatch:

jobs:
  send-regulatory-email:
    # GitHub provides free Ubuntu Linux virtual machines for running jobs
    runs-on: ubuntu-latest

    steps:
      # Step 1: Download this repository's code onto the virtual machine
      # (The VM starts empty — it needs to fetch our script first)
      - name: Check out repository
        uses: actions/checkout@v4

      # Step 2: Install Python 3.12 on the virtual machine
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # Step 3: Run the email script with all required configuration
      - name: Send weekly regulatory update email
        # env: sets environment variables that scripts/send_email.py will read.
        # ${{ secrets.NAME }} pulls the value from GitHub's encrypted Secrets vault.
        # The secrets must be set up in: GitHub repo → Settings → Secrets → Actions
        env:
          # Authentication secrets (stored in GitHub Secrets — never hardcoded)
          GMAIL_SENDER: ${{ secrets.GMAIL_SENDER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
          CLAUDE_PROJECT_URL: ${{ secrets.REGULATORY_CLAUDE_URL }}

          # Job-specific configuration (not secret — lives here in the YAML)
          EMAIL_SUBJECT: "[COMPLIANCE] Weekly Regulatory Update — Ready to Run"
          JOB_NAME: "Weekly Regulatory Update"
          JOB_SCHEDULE_DESC: "Every Monday at ~8am ET"

          # REPLACE THIS with your actual regulatory update prompt.
          # The | symbol below means "multi-line text follows, preserve line breaks."
          # Indent the prompt text with exactly 12 spaces (to match the YAML indentation).
          PROMPT_TEXT: |
            [PLACEHOLDER — Replace this entire block with your actual regulatory update prompt]

            Example of what this might look like:
            You are a compliance assistant for a FinCEN-registered fiat-backed stablecoin
            issuer licensed as a money transmitter in 16+ states. Please review this week's
            regulatory landscape and provide a structured summary covering:
            1. New FinCEN guidance or advisories published this week
            2. State money transmitter license updates across our 16+ states
            3. OFAC/SDN list updates and sanctions developments
            4. Upcoming compliance deadlines in the next 30 days
            5. Relevant enforcement actions in the crypto/stablecoin space

            [End placeholder — delete everything above and paste your real prompt here]

        # Run the shared email script
        run: python scripts/send_email.py
```

- [ ] **Step 2: Commit**

```bash
cd /home/eddie/claude/compliance-automation && git add .github/workflows/weekly_regulatory.yml && git commit -m "feat: add weekly regulatory update workflow"
```

---

## Task 7: Write the monthly InfoSec workflow

**Files:**
- Create: `.github/workflows/monthly_infosec.yml`

> **Plain English:** This is the same structure as the weekly workflow, but with a different schedule (27th of every month instead of every Monday) and different email content (InfoSec newsletter instead of regulatory update). The two jobs are completely independent — neither one knows the other exists.

- [ ] **Step 1: Write the workflow file**

Create `/home/eddie/claude/compliance-automation/.github/workflows/monthly_infosec.yml` with this exact content:

```yaml
# .github/workflows/monthly_infosec.yml
#
# GitHub Actions workflow for Job 2: Monthly InfoSec Newsletter
#
# Runs on the 27th of every month — chosen as a fixed approximation of
# "3 days before end of month" (cron cannot express variable month lengths).
#
# To trigger this manually (for testing):
#   Go to GitHub repo → Actions tab → "Monthly InfoSec Newsletter" → "Run workflow"

name: Monthly InfoSec Newsletter

# WHEN to run this workflow
on:
  schedule:
    # Cron format: minute  hour  day-of-month  month  day-of-week
    #                 0      12       27          *        *
    # Translation: At 12:00 UTC on the 27th of every month
    # (~8am ET in summer/EDT, ~7am ET in winter/EST)
    - cron: '0 12 27 * *'

  # workflow_dispatch lets you trigger this manually from GitHub's website for testing
  workflow_dispatch:

jobs:
  send-infosec-email:
    runs-on: ubuntu-latest

    steps:
      # Download this repository's code onto the virtual machine
      - name: Check out repository
        uses: actions/checkout@v4

      # Install Python 3.12 on the virtual machine
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # Run the email script with InfoSec-specific configuration
      - name: Send monthly InfoSec newsletter email
        env:
          # Authentication secrets (stored in GitHub Secrets — never hardcoded)
          GMAIL_SENDER: ${{ secrets.GMAIL_SENDER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
          CLAUDE_PROJECT_URL: ${{ secrets.INFOSEC_CLAUDE_URL }}

          # Job-specific configuration (not secret — lives here in the YAML)
          EMAIL_SUBJECT: "[COMPLIANCE] Monthly InfoSec Newsletter — Ready to Run"
          JOB_NAME: "Monthly InfoSec Newsletter"
          JOB_SCHEDULE_DESC: "27th of every month at ~8am ET"

          # REPLACE THIS with your actual InfoSec newsletter prompt.
          PROMPT_TEXT: |
            [PLACEHOLDER — Replace this entire block with your actual InfoSec newsletter prompt]

            Example of what this might look like:
            You are an information security advisor for a FinCEN-registered fiat-backed
            stablecoin issuer. Please compile this month's InfoSec newsletter covering:
            1. Major data breaches or security incidents in the financial/crypto sector
            2. New vulnerabilities relevant to our technology stack
            3. Updates to security frameworks (NIST, ISO 27001, SOC 2, etc.)
            4. Recommended security patches or actions we should prioritize
            5. Emerging threats targeting money service businesses or crypto companies

            Format this as a brief newsletter I can share with the team.

            [End placeholder — delete everything above and paste your real prompt here]

        run: python scripts/send_email.py
```

- [ ] **Step 2: Commit**

```bash
cd /home/eddie/claude/compliance-automation && git add .github/workflows/monthly_infosec.yml && git commit -m "feat: add monthly InfoSec newsletter workflow"
```

---

## Task 8: Write README.md

**Files:**
- Create: `README.md`

> **Plain English:** The README is the first thing anyone sees when they visit your GitHub repo. Since this is a portfolio project, it needs to clearly explain what the project does, why it's interesting, and how it's built — in language that's impressive to a technical reader but understandable to a non-technical one.

- [ ] **Step 1: Write README.md**

Create `/home/eddie/claude/compliance-automation/README.md` with this exact content:

```markdown
# compliance-automation

> Automated compliance workflow reminders for a FinCEN-registered stablecoin issuer — built with GitHub Actions and Python.

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
| Weekly Regulatory Update | Every Monday at ~8am ET | Regulatory monitoring prompt + Claude link |
| Monthly InfoSec Newsletter | 27th of every month at ~8am ET | InfoSec review prompt + Claude link |

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

## About

Built by [Edward D'Amore](https://github.com/EdwardDAmore) — operator of a FinCEN-registered fiat-backed stablecoin issuer licensed as a money transmitter in 16+ US states.
```

- [ ] **Step 2: Commit**

```bash
cd /home/eddie/claude/compliance-automation && git add README.md && git commit -m "docs: add portfolio README"
```

---

## Task 9: Write learn.md

**Files:**
- Create: `learn.md`

> **Plain English:** This is Eddie's personal learning document — a plain-English explanation of everything in the project, why we made the decisions we did, and lessons to carry forward. Per CLAUDE.md, it should be engaging and use analogies and anecdotes, not dry documentation.

- [ ] **Step 1: Write learn.md**

Create `/home/eddie/claude/compliance-automation/learn.md` with this exact content:

```markdown
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
0 12 * * 1    → Every Monday at 12:00 UTC
0 12 27 * *   → 27th of every month at 12:00 UTC
* * * * *     → Every minute (useful for testing, terrible for production)
```

The `*` means "every value" for that field. So `* * * * 1` means "every minute of every hour of every day that is a Monday" — probably not what you want.

---

## Potential Pitfalls and How to Avoid Them

**Gmail App Password gotcha:** Gmail requires you to enable "2-Step Verification" before you can create App Passwords. If the script fails to authenticate, check that 2FA is enabled on the bot Gmail account first.

**GitHub Actions cron delay:** GitHub's free cron scheduler can run up to 15 minutes late when GitHub is busy. This is documented behavior. If the email arrives at 8:17am instead of 8:00am, that's normal — not a bug.

**YAML indentation is not forgiving:** YAML uses indentation (spaces, not tabs) to define structure. If the YAML file has a tab character instead of spaces, or misaligned indentation, GitHub Actions will fail with a cryptic error. If a workflow fails immediately with a parse error, indentation is the first thing to check.

**The UTC vs. local time gotcha:** GitHub Actions has no concept of Daylight Saving Time. If the email arrives an hour early in winter, it's because the cron is set to a UTC time that's 4 hours behind ET in summer but 5 hours in winter. The fix is to decide which is worse — arriving at 7am in winter or 9am in summer — and set UTC accordingly.

**What happens if the email fails to send?** Currently, GitHub Actions will mark the job as failed and send an email notification to the repo owner. A future improvement would be to add retry logic to the Python script.

---

## What Good Engineers Think About That I'm Learning

**Separation of concerns:** `send_email.py` only knows how to send email. The workflow YAML only knows the schedule and configuration. Neither one bleeds into the other's territory. This makes each piece easier to test, debug, and change.

**Reproducibility:** Because all configuration is in version-controlled files and all secrets are in a vault, this system could be reproduced from scratch in 20 minutes. Nothing exists only in someone's head or on a particular machine.

**The cheapest test is one that doesn't touch the network:** The `@patch` decorator in our tests replaces the real Gmail server with a fake. This means tests run instantly, work offline, and never fail because of network issues. Mock what you don't control; test what you own.

**Small, focused files:** `send_email.py` does exactly one thing: send an email. If we later need to send Slack messages instead, we write `send_slack.py` — we don't modify the email file. This is the Single Responsibility Principle, and it makes maintenance dramatically easier.
```

- [ ] **Step 2: Commit**

```bash
cd /home/eddie/claude/compliance-automation && git add learn.md && git commit -m "docs: add plain-English learning guide"
```

---

## Task 10: Commit remaining files and push everything to GitHub

**Files:** No new files — commits the design spec, plans, and pushes to GitHub.

> **Plain English:** Everything is written. Now we package it all up and send it to GitHub. Because GitHub's repo already has a placeholder README (created when you set up the repo), we need to tell git "our version wins if there's a conflict." Then we push, and your code goes live on GitHub.

- [ ] **Step 1: Stage the docs folder (design spec and plan)**

```bash
cd /home/eddie/claude/compliance-automation && git add docs/ && git commit -m "docs: add design spec and implementation plan"
```

- [ ] **Step 2: Verify all files are committed (nothing left unstaged)**

```bash
cd /home/eddie/claude/compliance-automation && git status
```

Expected output:
```
On branch main
nothing to commit, working tree clean
```

If you see any untracked or modified files, stage and commit them before continuing.

- [ ] **Step 3: Pull GitHub's existing content (the placeholder README) and merge**

> GitHub's repo has a placeholder README from when you created it. We need to bring that history into our local repo so git can merge them. The `--allow-unrelated-histories` flag handles the fact that our local commits and GitHub's commits started from different points. The `-X ours` flag means "if any file conflicts, keep our version."

```bash
cd /home/eddie/claude/compliance-automation && git pull origin main --allow-unrelated-histories -X ours
```

You may be prompted to enter a username and password. For GitHub, use:
- Username: `EdwardDAmore`
- Password: your GitHub Personal Access Token (NOT your GitHub account password — see note below)

> **Note on GitHub authentication:** GitHub no longer accepts plain passwords for git operations. You need a Personal Access Token. To create one: GitHub → Settings (top right avatar) → Developer settings → Personal access tokens → Tokens (classic) → Generate new token. Give it `repo` scope and copy it. Use it as your password when git prompts you.

- [ ] **Step 4: Push all code to GitHub**

```bash
cd /home/eddie/claude/compliance-automation && git push origin main
```

Expected output:
```
Enumerating objects: xx, done.
...
To https://github.com/EdwardDAmore/compliance-automation.git
   xxxxxxx..xxxxxxx  main -> main
```

- [ ] **Step 5: Verify on GitHub**

Open `https://github.com/EdwardDAmore/compliance-automation` in your browser. You should see all the files in the repo with your README displayed below.

---

## Task 11: Set up GitHub Secrets

> **Plain English:** GitHub Secrets is an encrypted vault built into every GitHub repository. Values stored here are never shown in logs or code — they're injected into your workflows at runtime like a secure key exchange. You need to create 5 secrets.

- [ ] **Step 1: Create your dedicated Gmail account**

1. Go to [gmail.com](https://gmail.com) and click "Create account"
2. Choose a name like `compliance.bot.edamore@gmail.com` (or similar — the exact address doesn't matter)
3. Follow the setup steps, including adding a phone number for verification
4. **Important:** Enable 2-Step Verification (required before creating App Passwords):
   - In Gmail, click your profile photo → "Manage your Google Account"
   - Click "Security" in the left menu
   - Find "2-Step Verification" and turn it on
   - Follow the prompts (use your phone for verification)

- [ ] **Step 2: Create a Gmail App Password**

> An App Password is a 16-character password Google generates specifically for automated tools. It's separate from your real password — if this automation ever gets compromised, you revoke just this App Password and your account stays safe.

1. In Google Account → Security → find "App passwords" (only visible after enabling 2-Step Verification)
2. Click "App passwords"
3. Give it a name: `compliance-automation`
4. Click "Create"
5. Google will show a 16-character code like `abcd efgh ijkl mnop` — **copy this immediately**, it will never be shown again
6. Store it somewhere safe (like a password manager) before pasting it into GitHub

- [ ] **Step 3: Add all 5 secrets to GitHub**

For each secret below, follow this process:
1. Go to `https://github.com/EdwardDAmore/compliance-automation`
2. Click "Settings" (top menu of the repo — not your profile settings)
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Enter the Name and Value, click "Add secret"

| Secret Name | Value to Enter |
|---|---|
| `GMAIL_SENDER` | Your new bot Gmail address (e.g. `compliance.bot.edamore@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character App Password from Step 2 (no spaces) |
| `RECIPIENT_EMAIL` | `ee71715@gmail.com` |
| `REGULATORY_CLAUDE_URL` | `https://claude.ai` (placeholder until you create the Claude Project) |
| `INFOSEC_CLAUDE_URL` | `https://claude.ai` (placeholder until you create the Claude Project) |

- [ ] **Step 4: Verify all 5 secrets appear in the list**

After adding all secrets, the "Actions secrets" page should show 5 entries (names only — values are hidden). If any are missing, add them.

---

## Task 12: Test the system with a manual trigger

> **Plain English:** We don't want to wait until Monday to find out something is broken. GitHub Actions has a "Run workflow" button that lets us trigger a job manually right now. We'll use this to do a live end-to-end test.

- [ ] **Step 1: Trigger the weekly regulatory workflow manually**

1. Go to `https://github.com/EdwardDAmore/compliance-automation`
2. Click the "Actions" tab
3. In the left sidebar, click "Weekly Regulatory Update"
4. Click the "Run workflow" button (top right of the workflow list)
5. Leave "Branch: main" selected and click the green "Run workflow" button

- [ ] **Step 2: Watch the job run**

1. A new row will appear in the workflow runs list — click on it
2. Click on "send-regulatory-email" to expand the job
3. Watch each step complete. A green checkmark means it succeeded.
4. If any step fails, click on it to see the error log

- [ ] **Step 3: Check your inbox**

Within 1–2 minutes of the job completing, an email should arrive at `ee71715@gmail.com` from your bot Gmail account with:
- Subject: `[COMPLIANCE] Weekly Regulatory Update — Ready to Run`
- Body containing the placeholder prompt text
- A link to `https://claude.ai` (the placeholder Claude URL)

- [ ] **Step 4: Trigger the monthly InfoSec workflow and verify**

Repeat Steps 1–3 for the "Monthly InfoSec Newsletter" workflow.

- [ ] **Step 5: Confirm both jobs are working**

Both workflows should show green checkmarks in the Actions tab, and two emails should have arrived in your inbox. The system is live.

---

## Post-Setup: Replacing Placeholder Prompts

When you're ready to add your real compliance prompts:

1. Open `.github/workflows/weekly_regulatory.yml` in a text editor
2. Find the `PROMPT_TEXT:` section
3. Delete the placeholder text and paste your real prompt, keeping the `|` character and indentation
4. Commit and push the change:
   ```bash
   cd /home/eddie/claude/compliance-automation
   git add .github/workflows/weekly_regulatory.yml
   git commit -m "chore: replace placeholder with real regulatory prompt"
   git push origin main
   ```
5. Repeat for `monthly_infosec.yml`

When you create your Claude Projects, update `REGULATORY_CLAUDE_URL` and `INFOSEC_CLAUDE_URL` in GitHub Secrets with the real URLs — no code change needed.
```
