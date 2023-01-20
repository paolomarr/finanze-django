from django.shortcuts import render as srender
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.http import JsonResponse

from .models import Order, Stock, StockQuote
from .lib import yahoo_finance
import logging
import re
from datetime import datetime
from .forms import NewOrderForm
from urllib.parse import unquote
from django.apps import apps
from . import app_name
from django.urls import reverse


logger = logging.getLogger(__name__)


def render(request, path, context):
    request.current_app = apps.get_app_config(app_name).verbose_name
    context['base_app_path'] = reverse("index", current_app=app_name)
    return srender(request, path, context)


def index(request):
    return HttpResponseRedirect("/tradinglog/orders")


def filterOrders(filterParams):
    filterdict = {}
    logging.debug("Filter parameters: {}".format(filterParams))
    for rawitem in filterParams:
        item = unquote(rawitem)
        col = item.split("=")[0]
        val = item.split("=")[1]
        if col == 'datefrom':
            filterdict['date__gte'] = val
        if col == 'dateto':
            filterdict['date__lt'] = val
        if col in ['stock', 'operation']:
            filterdict = {"{}_id".format(col): val}
    if len(filterdict) > 0:
        logging.debug("Filter dict: {}".format(filterdict))
        retOrders = Order.objects.filter(**filterdict)
    else:
        retOrders = Order.objects.all()

    return retOrders.order_by('-date')


def orders(request):
    params = request.GET
    orders = filterOrders(params.getlist('filter'))
    context = {'orders': orders}
    content = request.content_type
    logger.info("[VIEWS][orderlist] Requested content type: {}\
".format(content))
    return render(request, 'tradinglog/orderlist.html', context)


def neworder(request):
    # create a form instance and populate it with data from the request:
    if request.method == 'GET':
        form = NewOrderForm()
        return render(request, 'tradinglog/neworder.html', {'form': form})
    elif request.method == 'POST':
        # parse the form and add new item
        form = NewOrderForm(request.POST)
        if form.is_valid():
            form.save()
            # redirect to a new URL:
            return index(request)


def updateCurrentPrice(request):
    symbols = request.GET.getlist('symbol')
    results = []
    for symid in symbols:
        stock = Stock.objects.get(id=symid)
        if stock is None:
            logger.info("No stocks for symbol ID '%s'" % symid)
            results.append({"symbol": symid, "error": "not found"})
            continue
        sym = stock.symbol
        symdata = yahoo_finance.getLatestQuoteForSymbol(sym)
        # check for errors
        if symdata.get('error', None) is not None:
            # return error
            results.append({"id": symid, "symbol": sym, "error": symdata['error']})

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
            logger.info("[VIEWS][updateCurrentPrice] Updating existing quote {}: \
closeval {} at {}".format(sym, cval, ctime))
            existing_quotes.update(
                close_val=cval,
                close_timestamp=ctime)
            results.append({"id": symid, "symbol": sym, "res": "updated existing"})
        else:
            # insert anew
            logger.info("[VIEWS][updateCurrentPrice] Inserting new quote {}: \
closeval {} at {}".format(sym, cval, ctime))
            newqoute = StockQuote(
                stock=stock,
                close_val=cval,
                close_timestamp=ctime)
            newqoute.save()
            results.append({"id": symid, "symbol": sym, "res": "inserted new"})
    logger.debug("[updateCurrentPrice] Results: %s" % str(results))
    return JsonResponse({"results": results})


def tradingStats(request):
    tradedStocks = Stock.objects.annotate(
        quantity=Sum('order__quantity')
    ).order_by('symbol')
    # logger.debug([x.buys for x in tradedStocks])
    totalone = 0
    totaltwo = 0
    totalthree = 0
    totalfour = 0
    for stock in tradedStocks:
        totalone += stock.amountOrdered
        totaltwo += stock.currentAsset
        totalthree += stock.currentGrossGain
        totalfour += stock.currentNetGain
    context = {'tradedStocks': tradedStocks,
               'totalone': totalone, 'totaltwo': totaltwo,
               'totalthree': totalthree, 'totalfour': totalfour,
               'gain': totaltwo - totalone}
    return render(request, "tradinglog/tradingstats.html", context)
