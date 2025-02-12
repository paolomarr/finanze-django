from django.urls import path

from . import views as tradinglog_views


urlpatterns = [
    path('orders/', views.OrderList.as_view()),
    path('orders/<int:pk>', views.OrderDetail.as_view()),
    path('stocks/', views.StocksList.as_view()),
    path('stocks/<int:pk>', views.StocksDetail.as_view()),
    path('quotes/', views.StockQuoteListCreate.as_view()),
    path('operations/', views.OrderOperationList.as_view()),
    path('currencies/', views.CurrencyList.as_view()),
]
