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

urlpatterns = [
    path('tradinglog/', include('tradinglog.urls')),
    path('movimenti/', include('movimenti.urls')),
    path('admin/', admin.site.urls),
    path('profile/', views.profile, name='profile'),
    path('profile/password-change', views.profile, name='password_change'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordChangeView.as_view(), name='password_reset'),
    path('', views.index, name='landing'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('finanze.api.urls')),
]
