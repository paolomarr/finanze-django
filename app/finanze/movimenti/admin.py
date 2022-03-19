from django.contrib import admin

from .models import Category, Subcategory, Movement, AssetBalance
# Register your models here.

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Movement)
admin.site.register(AssetBalance)
