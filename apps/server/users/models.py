from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
        help_text=_("Required. Enter a valid email address."),
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
