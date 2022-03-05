from django.db import models
from django.db.models import Sum, ExpressionWrapper, F, FloatField
from datetime import datetime, timedelta

TAX_RATE = 0.26
INFLATION_YEAR_RATE = 0.02


class OrderOperation(models.Model):
    operation = models.CharField(max_length=20)

    def __str__(self):
        return self.operation


class Market(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Currency(models.Model):
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol


class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    regular_market_price = models.FloatField(default=0.0)
    regular_market_time = models.DateTimeField()
    last_price_update = models.DateTimeField(auto_now=False)

    @property
    def amountOrdered(self):
        return self.order_set.aggregate(value=Sum(
            ExpressionWrapper(F('price') * F('quantity'),
                              output_field=FloatField())))['value']

    @property
    def currentAsset(self):
        return self.regular_market_price * self.order_set.aggregate(qty=Sum('quantity'))['qty']

    @property
    def currentGrossGain(self):
        gain = 0
        for order in Order.objects.filter(stock=self):
            gain += order.gross_gain
        return gain

    @property
    def currentNetGain(self):
        gain = 0
        for order in Order.objects.filter(stock=self):
            gain += order.net_gain
        return gain

    def __str__(self):
        return "{sym} - {name}".format(sym=self.symbol, name=self.name)


class StockQuote(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    close_val = models.FloatField()
    close_timestamp = models.DateTimeField()


class Order(models.Model):
    """docstring for TradingLog"""
    date = models.DateField()
    code = models.CharField(max_length=100)
    account = models.CharField(max_length=100)
    operation = models.ForeignKey(OrderOperation, on_delete=models.PROTECT)
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    transaction_cost = models.FloatField(default=2.0)

    @property
    def amount(self):
        return self.price * self.quantity

    @property
    def currentval(self):
        return self.quantity * self.stock.regular_market_price

    @property
    def gross_gain(self):
        return self.currentval - self.amount

    @property
    def net_gain(self):
        "gross_gain after taxes, inflation and transaction costs"
        if self.gross_gain <= 0:
            return self.gross_gain
        elapsedYears = (datetime.today().date() - self.date) / timedelta(days=360)
        return self.gross_gain * (
            1 - TAX_RATE) * (
            1 - INFLATION_YEAR_RATE)**elapsedYears - self.transaction_cost

    def __str__(self):
        return "{date} {sym} {prc:.2f} x{qty} {tot:.2f} {cur}\
".format(
            date=self.date,
            sym=self.stock.symbol,
            qty=self.quantity,
            prc=self.price,
            tot=self.quantity * self.price,
            cur=self.stock.currency)
