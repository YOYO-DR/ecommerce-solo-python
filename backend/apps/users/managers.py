from django.contrib.auth.models import BaseUserManager

class UserAccountManager(BaseUserManager):
  def create_user(self, email: str, password: str | None = None, **extra_fields: object):
    if not email:
      raise ValueError("El email debe ser proporcionado")

    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save()

    return user

  def create_superuser(self, email: str, password: str | None = None, **extra_fields: object):
    user = self.create_user(email, password, **extra_fields)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user
