from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as rf_views

from app.finanze.finanze.api.scanreceipt_views import scan_receipt
from . import movimenti_views, tradinglog_views

urlpatterns = [
    # movimenti
    path('movements/', movimenti_views.MovementList.as_view()),
    path('movements/<int:pk>', movimenti_views.MovementDetail.as_view()),
    path('users/', movimenti_views.UserList.as_view()),
    path('user/', movimenti_views.LoggedInUserDetail.as_view()),
    path('users/<int:pk>/', movimenti_views.UserDetail.as_view()),
    path('categories/', movimenti_views.CategoryListCreate.as_view()),
    path('categories/<int:pk>', movimenti_views.CategoryDetail.as_view()),
    path('subcategories/', movimenti_views.SubcategoryListCreate.as_view()),
    path('subcategories/<int:pk>', movimenti_views.SubcategoryDetail.as_view()),
    path('balances/', movimenti_views.BalanceMovementList.as_view()),
    # tradinglog
    path('orders/', tradinglog_views.OrderListCreate.as_view()),
    path('orders/<int:pk>', tradinglog_views.RetrieveUpdateDestroy.as_view()),
    path('stocks/', tradinglog_views.StocksListCreate.as_view()),
    path('stock/<int:pk>', tradinglog_views.StocksRetrieveUpdateDestroy.as_view()),
    path('quotes/', tradinglog_views.StockQuoteListCreate.as_view()),
    path('operations/', tradinglog_views.OrderOperationList.as_view()),
    path('currencies/', tradinglog_views.CurrencyList.as_view()),
    # authentication
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', rf_views.obtain_auth_token),
    path('scan_receipt', scan_receipt)
]

urlpatterns = format_suffix_patterns(urlpatterns)