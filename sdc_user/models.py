from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models


from django.utils.crypto import get_random_string


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not username:
            raise ValueError(_('Username/Abbreviation must be 3 characters long'))


        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)


def getUUID():
    return get_random_string(length=32)

NATIONS = (('D', _('Germany')), ('G', _('Greek')))

class CustomUser(AbstractUser):
    username = models.CharField(_('Abbreviation'), max_length=255, unique=True, blank=False,null=False)
    #phone = PhoneField(_('Contact phone number'), help_text=_('Phone number, only for emergency'), null=True, blank=False)

    # birth_date = models.DateField(_('Birthday'), null=True, blank=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'

    objects = CustomUserManager()

    agb = models.BooleanField(blank=False, default=False,null=False)



    def __str__(self):
        return self.username


