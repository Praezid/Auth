from django.db import models
from django.contrib.auth.models import (PermissionsMixin, AbstractBaseUser, UserManager)
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField, validate_international_phonenumber
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import jwt
from django.conf import settings
from datetime import datetime, timedelta


class MyUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    only_letters = RegexValidator(r'^[a-zA-Z]*$', 'Only letters are allowed.')

    first_name = models.CharField(_('first name'), max_length=150, blank=False, validators=[only_letters])
    last_name = models.CharField(_('last name'), max_length=150, blank=True, validators=[only_letters])
    email = models.EmailField(_('email address'), blank=False, unique=True)
    phone = PhoneNumberField(blank=True, validators=[validate_international_phonenumber])
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    email_verified = models.BooleanField(
        _('email_verified'),
        default=True,
        help_text=_(
            'Designates whether this users email is verified. '
        ),
    )
    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    @property
    def token(self):
        token = jwt.encode(
            {
                'email': self.email,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            settings.SECRET_KEY,
            algorithm='HS256'
        )

        return token
