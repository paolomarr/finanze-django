from django.urls import path

from . import views as tradinglog_views


urlpatterns = [
    path('orders/', tradinglog_views.OrderListCreate.as_view()),
    path('orders/<int:pk>', tradinglog_views.RetrieveUpdateDestroy.as_view()),
    path('stocks/', tradinglog_views.StocksListCreate.as_view()),
    path('stock/<int:pk>', tradinglog_views.StocksRetrieveUpdateDestroy.as_view()),
    path('quotes/', tradinglog_views.StockQuoteListCreate.as_view()),
    path('operations/', tradinglog_views.OrderOperationList.as_view()),
    path('currencies/', tradinglog_views.CurrencyList.as_view()),
    # DEPRECATED
    # path('', views.index, name='index'),
    # path('orders', views.orders, name='orders'),
    # path('orders/new', views.neworder, name='neworder'),
    # path('updatecurrentprice', views.updateCurrentPrice, name='updatePrice'),
    # path('tradingstats', views.tradingStats, name='tradingStats'),
    # path('tradinghistory', views.tradingHistory, name='tradingHistory'),
]
