from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MovimentiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movimenti'
    verbose_name = _("Movements")
