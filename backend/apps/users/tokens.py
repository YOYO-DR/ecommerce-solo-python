"""Token generator for email verification."""
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for account activation via email."""

    def _make_hash_value(self, user, timestamp):  # type: ignore[no-untyped-def]
        """
        Hash the user's primary key, email, active status and timestamp.
        """
        return f"{user.pk}{user.email}{user.is_active}{timestamp}"


account_activation_token = AccountActivationTokenGenerator()
