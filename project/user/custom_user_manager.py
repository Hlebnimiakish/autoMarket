from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from root.common.model_manager import ActiveOnlyManager


class CustomUserManager(BaseUserManager, ActiveOnlyManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('You must set a username'))
        if not email:
            raise ValueError(_('You must set an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        user = self.create_user(email=self.normalize_email(email),
                                username=username,
                                password=password,
                                **extra_fields)
        user.save()
        return user
