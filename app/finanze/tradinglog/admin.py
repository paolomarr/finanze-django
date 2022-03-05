from django.contrib import admin

from .models import Currency, Market, Order, Stock, OrderOperation, StockQuote
# Register your models here.

admin.site.register(Currency)
admin.site.register(Market)
admin.site.register(Order)
admin.site.register(Stock)
admin.site.register(OrderOperation)
admin.site.register(StockQuote)
