from requests import post
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
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

    def post(self, request, *args, **kwargs):
        '''
        User does not actually create a quote but asks for quotes update
        '''
        pass