from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name=(_('Email Address')))

    USER_TYPE_CHOICES = (
        ('admin','Admin'),
        ('customer','Customer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer', verbose_name=_('User Type'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone Number'))
    is_email_verifed = models.BooleanField(default=False, verbose_name=('Email Verified'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created Art'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Usuarios')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email