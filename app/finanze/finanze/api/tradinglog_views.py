from datetime import datetime
import stat
from requests import post
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from tradinglog.lib.yahoo_finance import getLatestQuoteForSymbol
from tradinglog.models import Currency, Order, Stock, OrderOperation, StockQuote
from finanze.api.tradinglog_serializers import OrderSerializer, StockSerializer, OrderOperationSerializer, CurrencySerializer, StockQuoteSerializer
from finanze.permissions import IsOwnerOrDeny

from finanze import logger

class OrderListCreate(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-date")

    # def perform_create(self, serializer):
    #     return serializer.save(user=[self.request.user])

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            logger.debug(f"New order data validated: {request.data}")
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errstr = " - ".join(serializer.errors)
        logger.error(f"Serialization of new order failed: {errstr}. Data was: {request.data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser|IsOwnerOrDeny]


class StocksListCreate(generics.ListCreateAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        return Stock.objects.all()
    

class StocksRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser|IsOwnerOrDeny]
    serializer_class = StockSerializer


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