from django.forms import ModelForm
from .models import Order


class NewOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'code',
            'date',
            'account',
            'operation',
            'stock',
            'quantity',
            'price',
            'transaction_cost'
        ]
