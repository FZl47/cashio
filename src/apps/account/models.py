from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.urls import reverse_lazy
from django.db import models

from apps.core.models import BaseModel, BaseModelObjectRelation
from apps.core.utils.validators import PhonenumberValidator
from apps.accounting.models import PettyCashHolder


class CustomUserManager(BaseUserManager):

    def _create_holder_for_user(self, user):
        return PettyCashHolder.objects.create(user=user)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if user.role == 'common_user':
            self._create_holder_for_user(user)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractUser, PermissionsMixin):
    ROLE_TYPES = (
        ('admin_user', _('Admin_user')),
        ('common_user', _('Common User')),
    )

    first_name = models.CharField("first name", max_length=150, blank=True, default=_('No name'))
    last_name = models.CharField("last name", max_length=150, blank=True, default='')
    email = models.EmailField(_("email address"), unique=True, validators=[AbstractUser.username_validator])
    phonenumber = models.CharField(_("phonenumber"), null=True, blank=True, max_length=20,
                                   validators=[PhonenumberValidator()])
    role = models.CharField(max_length=15, choices=ROLE_TYPES, default='common_user')

    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def profile_is_completed(self):
        if self.is_superuser:
            return True

        if self.first_name and self.last_name and self.email and self.phonenumber:
            return True
        return False

    @property
    def is_admin(self):
        return True if self.role == 'admin_user' or self.is_superuser else False

    @property
    def is_common_user(self):
        return True if self.role == 'common_user' else False

    @property
    def holder(self):
        return self.pettycashholder

    def get_absolute_url(self):
        return reverse_lazy('account:user__detail', args=(self.id,))

    def get_login_activities(self):
        return self.userloginactivity_set.all()

    def get_notifications(self):
        return self.notificationuser_set.all()

    def get_unread_notifications(self):
        return self.get_notifications().filter(is_visited=False)


class UserLoginActivity(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.CharField(max_length=24)
    agent = models.TextField(null=True)

    def __str__(self):
        return f'{self.user} | {self.ip}'
