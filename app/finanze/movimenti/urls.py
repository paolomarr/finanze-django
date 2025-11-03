from django.urls import include, path

from . import views

urlpatterns = [
    path('movements/', views.MovementList.as_view()),
    path('movements/<int:pk>', views.MovementDetail.as_view()),
    path('categories/', views.CategoryListCreate.as_view()),
    path('categories/<int:pk>', views.CategoryDetail.as_view()),
    path('subcategories/', views.SubcategoryListCreate.as_view()),
    path('subcategories/<int:pk>', views.SubcategoryDetail.as_view()),
    path('balances/', views.BalanceMovementList.as_view()),
    path('all-time/', views.AllTimeMovementsView.as_view()),
    path('balance-to-date/<int:year>/<int:month>/<int:day>', views.BalanceAtDateView.as_view()),
]
