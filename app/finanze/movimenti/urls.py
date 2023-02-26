from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movement/<int:id>', views.movement, name='movement'),
    path('list', views.list, name='list'),
    path('new', views.newmovement, name='newmovement'),
    path('summary', views.summary, name='summary'),
    path('assets', views.assets, name='assets'),
    path('categories', views.categories, name='categories'),
    path('categories/new', views.newcategory, name='categories.new'),
    path('summary/json', views.summaryXHR, name='summaryxhjson'),
    path('summary/fetch', views.summaryXHR, name='summaryxhr'),
]
