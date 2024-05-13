from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as rf_views
from . import views

urlpatterns = [
    path('movements/', views.MovementList.as_view()),
    path('movements/<int:pk>', views.MovementDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('user/', views.LoggedInUserDetail.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('categories/', views.CategoryListCreate.as_view()),
    path('categories/<int:pk>', views.CategoryDetail.as_view()),
    path('subcategories/', views.SubcategoryListCreate.as_view()),
    path('subcategories/<int:pk>', views.SubcategoryDetail.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', rf_views.obtain_auth_token),
    path('balances/', views.BalanceMovementList.as_view()),
    # path('balance/<int:pk>', views.AssetBalanceRetrieveUpdateDestroy.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)