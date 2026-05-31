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
