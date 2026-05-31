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
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        mock_smtp_class.assert_called_once_with('smtp.gmail.com', 587)

    @patch('send_email.smtplib.SMTP')
    def test_uses_starttls_encryption(self, mock_smtp_class):
        """Must call starttls() to encrypt the connection before sending passwords."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        mock_server.starttls.assert_called_once()

    @patch('send_email.smtplib.SMTP')
    def test_logs_in_with_sender_and_app_password(self, mock_smtp_class):
        """Must authenticate with the sender address and app password."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        mock_server.login.assert_called_once_with("bot@gmail.com", "apppassword123")

    @patch('send_email.smtplib.SMTP')
    def test_sends_to_correct_recipient(self, mock_smtp_class):
        """Must send the email to the correct recipient address."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_smtp_class.return_value.__exit__.return_value = False

        send_email("bot@gmail.com", "apppassword123", "eddie@gmail.com", "Subject", "Body")

        call_args = mock_server.sendmail.call_args
        self.assertEqual(call_args[0][1], "eddie@gmail.com")


if __name__ == '__main__':
    unittest.main()
