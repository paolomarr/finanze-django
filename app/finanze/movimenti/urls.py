from django.urls import path
from django.utils.translation import gettext as _

from . import views

app_name = 'movimenti'

urlpatterns = [
    path('', views.index, name='index'),
    path('list', views.list, name='list'),
    path('new', views.newmovement, name='newmovement'),
    path('summary', views.summary, name='summary'),
    path('assets', views.assets, name='assets'),
    path('summary/json', views.summaryXHR, name='summaryxhr'),
]
