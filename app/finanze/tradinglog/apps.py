from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TradinglogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tradinglog'
    verbose_name = _("Trading log")
