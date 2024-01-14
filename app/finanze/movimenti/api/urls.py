from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as rf_views
from . import views

urlpatterns = [
    path('movements/', views.MovementList.as_view()),
    path('movements/<int:pk>', views.MovementDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('categories/', views.CategoryList.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', rf_views.obtain_auth_token),
]

urlpatterns = format_suffix_patterns(urlpatterns)