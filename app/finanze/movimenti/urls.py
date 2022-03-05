from django.urls import path

from . import views

app_name = 'movimenti'

urlpatterns = [
    path('', views.index, name='index'),
    path('list', views.list, name='list'),
    path('new', views.newmovement, name='newmovement'),
    path('summary', views.summary, name='summary'),
]
