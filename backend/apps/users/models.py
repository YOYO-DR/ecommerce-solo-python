from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models
from .managers import UserAccountManager

class User(AbstractBaseUser, PermissionsMixin):

  email = models.EmailField(max_length=255, unique=True)
  first_name = models.CharField(max_length=255, blank=True)
  last_name = models.CharField(max_length=255, blank=True)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  objects = UserAccountManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ['first_name', 'last_name']

  def get_full_name(self) -> str:
    return f"{self.first_name} {self.last_name}"
  
  def get_short_name(self) -> str:
    return self.first_name
  
  def __str__(self) -> str:
    return self.email

  class Meta:
    verbose_name = _("User")
    verbose_name_plural = _("Users")
    indexes = [
        models.Index(fields=['email']),
        models.Index(fields=['is_active']),
    ]
