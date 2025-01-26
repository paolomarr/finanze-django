"""finanze URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import re_path
from rest_framework import permissions
from rest_framework.authtoken import views as rf_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

api_info = openapi.Info(
    title="Finanze API",
    default_version='v1',
    description="Handle your financial movements and trading operations",
    #   terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="paolo.marcehtti.it@gmail.com"),
    license=openapi.License(name="BSD License"),
)
   
schema_view = get_schema_view(
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path('tradinglog/', include('tradinglog.urls')),
    # path('movimenti/', include('movimenti.urls')),
    path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordChangeView.as_view(), name='password_reset'),
    path('i18n/', include('django.conf.urls.i18n')),
    # authentication
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', rf_views.obtain_auth_token),
    # user
    path('users/', views.UserList.as_view()),
    path('user/', views.LoggedInUserDetail.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    # scan-receipt
    path('scan-receipt', views.ScanReceipt.as_view()),
    # API
    path('movements/', include('movimenti.urls')),
    path('tradinglog/', include('tradinglog.urls')),
    re_path(r'^playground/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
