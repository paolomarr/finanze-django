from django.urls import path
from django.utils.translation import gettext as _

from . import views

app_name = 'movimenti'

urlpatterns = [
    path('', views.index, name='index'),
    path('list', views.list, {'menu': _('Movements')}, name='list'),
    path('new', views.newmovement, {'menu': _('Insert new')}, name='newmovement'),
    path('summary', views.summary, {'menu': _('Summary')}, name='summary'),
    path('assets', views.assets, {'menu': _('Assets')}, name='assets'),
    path('summary/json', views.summaryXHR, name='summaryxhr'),
]
