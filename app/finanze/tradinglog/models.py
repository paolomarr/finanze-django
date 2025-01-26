from django.db import models
from django.contrib.auth.models import User
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
    def quantityOwned(self):
        quantity = 0
        for order in self.order_set.all():
            direction = 1
            if order.operation.operation == "SELL":
                direction = -1
            quantity += order.quantity * direction
        return quantity

    @property
    def amountOwned(self):
        '''
        negative sign means loss
        '''
        amount = 0
        for order in self.order_set.all():
            amount += order.amount # take into account sign depending on BUY/SELL
        return amount

    @property
    def currentAssetMarketValue(self):
        return self.regular_market_price * self.quantityOwned

    @property
    def currentGrossGain(self):
        return self.currentAssetMarketValue - self.amountOwned

    @property
    def currentNetGain(self):
        gain = 0
        for order in Order.objects.filter(stock=self):
            gain += order.net_gain
        return gain

    def __str__(self):
        return "{sym} - {name}".format(sym=self.symbol, name=self.name)


class StockQuoteManager(models.Manager):
    def CountervalueAtDate(self, todate: datetime = datetime.now(), symbols: list = None) -> float:
        retval = 0
        filterdict = {"close_timestamp__lt": todate}
        if symbols and len(symbols)>0:
            stocks = Stock.objects.filter(symbol__in=symbols)
        else:
            stocks = []
            for qstock in Stock.objects.all():
                stocks.append(qstock)
        for stock in stocks:
            filterdict["stock"] = stock
            latest = self.filter(**filterdict).order_by("-close_timestamp").first()
            if latest:
                # get the amount of titles of the stock owned at date
                ownedCount = 0
                for order in Order.objects.filter(stock=stock, date__lte=todate.date()):
                    if order.operation.operation == "BUY":
                        ownedCount += order.quantity
                    else:
                        ownedCount -= order.quantity
                retval += latest.close_val * ownedCount
        return retval
    

class StockQuote(models.Model):
    objects = StockQuoteManager()
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    close_val = models.FloatField()
    close_timestamp = models.DateTimeField()


class OrderManager(models.Manager):
    def amountOrderedInPeriod(self, user: User, stocks: list, start: datetime, end: datetime) -> float:
        filterdict = {"user": user}
        if start:
            filterdict["date__gte"] = start
        if end:
            filterdict["date__lt"] = end
        if stocks and len(stocks)>0:
            filterdict["stock__in"] = stocks
        amount = 0
        for order in self.filter(**filterdict):
            amount += order.amount
        return amount

class Order(models.Model):
    objects = OrderManager()
    
    """docstring for TradingLog"""
    date = models.DateField()
    code = models.CharField(max_length=100)
    account = models.CharField(max_length=100)
    operation = models.ForeignKey(OrderOperation, on_delete=models.PROTECT)
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    transaction_cost = models.FloatField(default=2.0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    @property
    def amount(self):
        absamount = self.price * self.quantity
        if self.operation.operation == "SELL":
            absamount *= -1.0
        return absamount

    @property
    def currentval(self):
        return self.quantity * self.stock.regular_market_price

    @property
    def gross_gain(self):
        if self.operation.operation == "BUY":
            return self.currentval - self.amount
        else:
            return 0

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
