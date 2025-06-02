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
from rest_framework.authtoken import views as rf_views

urlpatterns = [
    # path('tradinglog/', include('tradinglog.urls')),
    # path('movimenti/', include('movimenti.urls')),
    path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordChangeView.as_view(), name='password_reset'),
    path('i18n/', include('django.conf.urls.i18n')),
    # user
    path('users/', views.UserList.as_view()),
    path('user/', views.LoggedInUserDetail.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    # scan-receipt
    path('scan-receipt', views.ScanReceipt.as_view()),
    # API
    ## authentication
    path('api/api-auth/', include('rest_framework.urls')),
    path('api/api-token-auth/', rf_views.obtain_auth_token),
    # endpoints
    path('api/movements/', include('movimenti.urls')),
    path('api/tradinglog/', include('tradinglog.urls')),
]
