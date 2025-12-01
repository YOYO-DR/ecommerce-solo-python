
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for backend.
    If adding fields that need to be filled at user signup,
    asegurate de actualizar el formulario publico de registro correspondiente.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = CharField(_("First name"), blank=True, max_length=150)
    last_name = CharField(_("Last name"), blank=True, max_length=150)
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
    
    def __str__(self) -> str:
        """String representation of the user.

        Returns:
            str: String representation of the user.

        """
        return self.email or self.name or str(self.id)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]