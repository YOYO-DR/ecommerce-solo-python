import pytest
from celery.result import EagerResult
from unittest.mock import patch, MagicMock
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.users.tasks import get_users_count, send_activation_email
from apps.users.tests.factories import UserFactory
from apps.users.tokens import account_activation_token

pytestmark = pytest.mark.django_db


def test_user_count(settings):
    """A basic test to execute the get_users_count Celery task."""
    batch_size = 3
    UserFactory.create_batch(batch_size)
    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = get_users_count.delay()
    assert isinstance(task_result, EagerResult)
    assert task_result.result == batch_size


class TestSendActivationEmailTask:
    """Tests for the Celery task send_activation_email."""

    def test_send_activation_email_success(self):
        """Test successful email sending."""
        user = UserFactory(first_name="John", last_name="Doe")
        activation_link = "http://localhost:5173/activate-account?uid=MQ&token=abc123"

        result = send_activation_email(user.id, activation_link)

        # Verify return message
        assert f"Activation email sent successfully to {user.email}" in result

        # Verify email was sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == [user.email]
        assert "Activate your account" in email.subject
        assert activation_link in email.body

        # Verify HTML alternative exists
        assert len(email.alternatives) == 1
        html_content, mime_type = email.alternatives[0]
        assert mime_type == "text/html"
        assert activation_link in html_content
        assert "Activate My Account" in html_content

    def test_send_activation_email_user_not_found(self):
        """Test task fails when user doesn't exist."""
        non_existent_id = 99999
        activation_link = "http://localhost:5173/activate-account?uid=MQ&token=abc123"

        with pytest.raises(Exception) as exc_info:
            send_activation_email(non_existent_id, activation_link)

        assert f"User with ID {non_existent_id} does not exist" in str(exc_info.value)

    @patch("apps.users.tasks.EmailMultiAlternatives.send")
    def test_send_activation_email_smtp_error_retries(self, mock_send: MagicMock):
        """Test task retries on SMTP error."""
        user = UserFactory()
        activation_link = "http://localhost:5173/activate-account?uid=MQ&token=abc123"

        # Simulate SMTP error
        mock_send.side_effect = Exception("SMTP connection failed")

        # Create a mock task instance with retry method
        with patch("apps.users.tasks.send_activation_email.retry") as mock_retry:
            mock_retry.side_effect = Exception("Max retries exceeded")

            with pytest.raises(Exception):
                send_activation_email(user.id, activation_link)

            # Verify retry was called
            assert mock_retry.called

    def test_send_activation_email_html_content(self):
        """Test that HTML content is properly formatted."""
        user = UserFactory(first_name="Jane")
        activation_link = "http://localhost:5173/activate-account?uid=Mg&token=xyz789"

        send_activation_email(user.id, activation_link)

        email = mail.outbox[0]
        html_content, _ = email.alternatives[0]

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert f"Hello {user.first_name}" in html_content or f"Hi {user.first_name}" in html_content
        assert '<a href="' in html_content
        assert activation_link in html_content
        assert "AllNutrition" in html_content

    def test_send_activation_email_plain_text_fallback(self):
        """Test that plain text version is included."""
        user = UserFactory(first_name="Bob")
        activation_link = "http://localhost:5173/activate-account?uid=Mw&token=def456"

        send_activation_email(user.id, activation_link)

        email = mail.outbox[0]

        # Verify plain text body
        assert activation_link in email.body
        assert user.first_name in email.body or user.email in email.body

    def test_send_activation_email_correct_from_email(self):
        """Test that email uses correct FROM address."""
        from django.conf import settings

        user = UserFactory()
        activation_link = "http://localhost:5173/activate-account?uid=NA&token=ghi789"

        send_activation_email(user.id, activation_link)

        email = mail.outbox[0]
        assert email.from_email == settings.DEFAULT_FROM_EMAIL

    def test_celery_task_with_real_user(self):
        """Test Celery task with a real user scenario."""
        # Create inactive user
        user = UserFactory(is_active=False, first_name="Real", last_name="User")

        # Generate real activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"http://localhost:5173/activate-account?uid={uid}&token={token}"

        # Send email
        result = send_activation_email(user.id, activation_link)

        # Verify
        assert "successfully" in result.lower()
        assert len(mail.outbox) == 1

        # Verify link components are in email
        email = mail.outbox[0]
        assert uid in email.body
        assert token in email.body
