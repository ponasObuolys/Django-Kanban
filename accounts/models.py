from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    notification_preferences = models.JSONField(
        default=dict,
        help_text=_('User notification preferences')
    )
    
    def __str__(self):
        return self.username
        
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
