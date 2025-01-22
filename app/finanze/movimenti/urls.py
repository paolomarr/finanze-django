from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.MovementList.as_view()),
    path('<int:pk>', views.MovementDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('user/', views.LoggedInUserDetail.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('categories/', views.CategoryListCreate.as_view()),
    path('categories/<int:pk>', views.CategoryDetail.as_view()),
    path('subcategories/', views.SubcategoryListCreate.as_view()),
    path('subcategories/<int:pk>', views.SubcategoryDetail.as_view()),
    path('balances/', views.BalanceMovementList.as_view()),
]
