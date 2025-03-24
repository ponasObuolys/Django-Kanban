from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'docs'
    verbose_name = _('Documentation')
