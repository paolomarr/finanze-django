from rest_framework import serializers
from tradinglog.models import Order, Stock, OrderOperation, Currency, StockQuote

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Order` instance, given the validated data.
        """
        return Order.objects.create(**validated_data)

class OrderOperatioSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderOperation
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Stock
        fields = '__all__'


class OrderOperationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderOperation
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = '__all__'


class StockQuoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockQuote
        fields = '__all__'