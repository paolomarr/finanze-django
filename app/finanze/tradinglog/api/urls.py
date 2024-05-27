from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as rf_views
from . import views

urlpatterns = [
    path('orders/', views.OrderListCreate.as_view()),
    path('orders/<int:pk>', views.RetrieveUpdateDestroy.as_view()),
    path('stocks/', views.StocksListCreate.as_view()),
    path('stock/<int:pk>', views.StocksRetrieveUpdateDestroy.as_view()),
    path('quotes/', views.StockQuoteListCreate.as_view()),
    path('operations/', views.OrderOperationList.as_view()),
    path('currencies/', views.CurrencyList.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', rf_views.obtain_auth_token),
]

urlpatterns = format_suffix_patterns(urlpatterns)