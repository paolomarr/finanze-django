from django.urls import path

from . import views as tradinglog_views


urlpatterns = [
    path('orders/', tradinglog_views.OrderListCreate.as_view()),
    path('orders/<int:pk>', tradinglog_views.OrderDetail.as_view()),
    path('stocks/search/', tradinglog_views.StockSearch.as_view()),
    path('stocks/', tradinglog_views.StocksListCreate.as_view()),
    path('stock/<int:pk>', tradinglog_views.StocksDetail.as_view()),
    path('quotes/', tradinglog_views.StockQuoteListCreate.as_view()),
    path('operations/', tradinglog_views.OrderOperationList.as_view()),
    path('currencies/', tradinglog_views.CurrencyList.as_view()),
]
