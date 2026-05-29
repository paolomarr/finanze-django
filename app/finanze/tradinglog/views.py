from datetime import datetime
from django.utils.timezone import now as tz_now
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from tradinglog.lib import finance_provider
from tradinglog.lib.providers.yahoo import get_latest_quote as getLatestQuoteForSymbol
from tradinglog.models import Currency, Market, Order, Stock, OrderOperation, StockQuote
from tradinglog.serializers import OrderSerializer, StockSerializer, OrderOperationSerializer, CurrencySerializer, StockQuoteSerializer
from finanze.permissions import IsOwnerOrDeny

from finanze import logger

class OrderListCreate(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-date")

    # def perform_create(self, serializer):
    #     return serializer.save(user=[self.request.user])

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        stock_payload = data.get("stock")
        if isinstance(stock_payload, dict):
            stock = _resolve_inline_stock(stock_payload)
            data["stock"] = stock.id
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            logger.debug(f"New order data validated: {data}")
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errstr = " - ".join(serializer.errors)
        logger.error(f"Serialization of new order failed: {errstr}. Data was: {data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _resolve_inline_stock(payload):
    """Get-or-create a Stock from a search-result-shaped payload.

    Best-effort quote refresh after creation: a brand-new Stock with no quote
    would render as 0€ in the portfolio chart until manually refreshed.
    """
    currency_sym = payload.get("currency") or "EUR"
    market_name = payload.get("market") or "UNKNOWN"
    currency, _ = Currency.objects.get_or_create(symbol=currency_sym)
    market, _ = Market.objects.get_or_create(name=market_name)
    stock, created = Stock.objects.get_or_create(
        symbol=payload["symbol"],
        defaults={
            "name": payload.get("name") or payload["symbol"],
            "currency": currency,
            "market": market,
            "regular_market_time": tz_now(),
            "last_price_update": tz_now(),
        },
    )
    if created:
        try:
            quote = finance_provider.get_latest_quote(stock.symbol)
            if quote and "regular_market_price" in quote:
                stock.regular_market_price = quote["regular_market_price"]
                stock.regular_market_time = datetime.fromtimestamp(quote["regular_market_time"])
                stock.last_price_update = tz_now()
                stock.save()
        except Exception as ex:
            logger.warning(f"Initial quote refresh for {stock.symbol} failed: {ex}")
    return stock
    

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser|IsOwnerOrDeny]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-date")


class StockSearch(APIView):
    """Search market-data provider for symbols matching a free-text query.

    Read-only; no DB writes. Stocks are persisted at order-create time via
    _resolve_inline_stock.
    """
    def get(self, request, *args, **kwargs):
        q = request.query_params.get("q", "").strip()
        if len(q) < 2:
            return Response([], status=status.HTTP_200_OK)
        try:
            results = finance_provider.search(q)
        except Exception as ex:
            logger.error(f"Stock search for q={q!r} failed: {ex}")
            return Response({"errors": [f"search failed: {str(ex)}"]},
                            status=status.HTTP_502_BAD_GATEWAY)
        return Response(results, status=status.HTTP_200_OK)


class StocksListCreate(generics.ListCreateAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        return Stock.objects.all()
    

class StocksDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = StockSerializer
    queryset = Stock.objects.all()

class OrderOperationList(generics.ListAPIView):
    serializer_class = OrderOperationSerializer

    def get_queryset(self):
        return OrderOperation.objects.all()


class CurrencyList(generics.ListAPIView):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        return Currency.objects.all()


class OrderOperationList(generics.ListAPIView):
    serializer_class = OrderOperationSerializer

    def get_queryset(self):
        return OrderOperation.objects.all()

    
class StockQuoteListCreate(generics.ListCreateAPIView):
    serializer_class = StockQuoteSerializer

    def get_queryset(self):
        base_queryset = StockQuote.objects.all()
        stock = self.request.query_params.get("stock")
        if stock:
            base_queryset = base_queryset.filter(stock=stock)
        return base_queryset

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''
        User does not actually create a quote but asks for quotes update
        '''
        if "symbols" in request.data:
            try:
                results = self._update_current_price(request.data.get("symbols"))

                return Response(results, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"errors": [f"server error: {str(ex)}"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"errors": ["invalid input: missing 'symbols' list"]}, status=status.HTTP_400_BAD_REQUEST)
        

    def _update_current_price(self, symbols):
        results = {
            "stocks": [],
            "quotes": [],
            "errors": [],
        }
        for symid in symbols:
            stock = Stock.objects.get(id=symid)
            if stock is None:
                logger.info("No stocks for symbol ID '%s'" % symid)
                results.errors.append({"symbol": symid, "error": "not found"})
                continue
            sym = stock.symbol
            symdata = getLatestQuoteForSymbol(sym)
            # check for errors
            if symdata.get('error', None) is not None:
                # return error
                results.errors.append({"stock": stock, "error": symdata['error']})

            # update current price
            rmp = symdata['regular_market_price']
            rmt = datetime.fromtimestamp(symdata['regular_market_time'])
            logger.info("[VIEWS][updateCurrentPrice] updating stock {}:\
    price {} at {}".format(sym, rmp, rmt))
            stock.regular_market_price = rmp
            stock.regular_market_time = rmt
            stock.last_price_update = datetime.now()
            stock.save()
            existing_quotes = StockQuote.objects.filter(
                stock__symbol=sym,
                close_timestamp__exact=datetime.fromtimestamp(
                    symdata['close_timestamp']))

            cval = symdata['close_val']
            ctime = datetime.fromtimestamp(symdata['close_timestamp'])
            if len(existing_quotes) > 0:
                # update?
                logger.info(f"[VIEWS][updateCurrentPrice] Updating existing quote {sym}: closeval {cval} at {ctime}")
                existing_quotes.update(
                    close_val=cval,
                    close_timestamp=ctime)
                for quote in existing_quotes:
                    results["quotes"].append(self.serializer_class(quote).data)
                results["stocks"].append(StockSerializer(stock).data)
            else:
                # insert anew
                logger.info(f"[VIEWS][updateCurrentPrice] Inserting new quote {sym}: closeval {cval} at {ctime}")
                newquote = StockQuote(
                    stock=stock,
                    close_val=cval,
                    close_timestamp=ctime)
                newquote.save()
                results["quotes"].append(self.serializer_class(newquote).data)
                results["stocks"].append(StockSerializer(stock).data)
        logger.debug("[updateCurrentPrice] Results: %s" % str(results))
        return results