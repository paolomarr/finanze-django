from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('orders', views.orders, name='orders'),
    path('orders/new', views.neworder, name='neworder'),
    path('updatecurrentprice', views.updateCurrentPrice, name='updatePrice'),
    path('tradingstats', views.tradingStats, name='tradingStats'),
    path('tradinghistory', views.tradingHistory, name='tradingHistory'),
]
