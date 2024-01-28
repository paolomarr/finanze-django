from ast import Or
from django.shortcuts import render as srender
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext as _

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

@login_required
def index(request):
    return HttpResponseRedirect("/tradinglog/orders")


def filterOrders(request):
    params = request.GET
    filterParams = params.getlist('filter')
    filterdict = {"user": request.user}
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

@login_required
def orders(request):
    params = request.GET
    orders = filterOrders(request)
    context = {'orders': orders}
    content = request.content_type
    logger.info("[VIEWS][orderlist] Requested content type: {}\
".format(content))
    return render(request, 'tradinglog/orderlist.html', context)

@login_required
def neworder(request):
    # create a form instance and populate it with data from the request:
    if request.method == 'GET':
        form = NewOrderForm()
        return render(request, 'tradinglog/neworder.html', {'form': form})
    elif request.method == 'POST':
        # parse the form and add new item
        form = NewOrderForm(request.POST)
        if form.is_valid():
            neworder: Order = form.save(commit=False)
            neworder.user = request.user
            neworder.save() 
            # redirect to a new URL:
            return index(request)

@login_required
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

@login_required
def tradingStats(request):
    allorders = Order.objects.filter(user=request.user).values("id", "stock__id", "stock__symbol").annotate(quantity=Sum('quantity'))

    traded_stocks = []
    parsed_symbols = set()
    totalone = 0
    totaltwo = 0
    totalthree = 0
    totalfour = 0
    for order in allorders:
        symbol = order["stock__symbol"]
        if symbol in parsed_symbols:
            continue
        else:
            parsed_symbols.add(symbol)
            stock = Stock.objects.get(id=order["stock__id"])
            traded_stocks.append(stock)
            totalone += stock.amountOwned
            totaltwo += stock.currentAssetMarketValue
            totalthree += stock.currentGrossGain
            totalfour += stock.currentNetGain

    context = {'tradedStocks': traded_stocks,
               'totalone': totalone, 'totaltwo': totaltwo,
               'totalthree': totalthree, 'totalfour': totalfour,
               'gain': totaltwo - totalone}
    return render(request, "tradinglog/tradingstats.html", context)

@login_required
def tradingHistory(request):
    params = request.GET
    # fetch the last assets record before request's start time, if any. Take baseline value 0 if none
    rawFrom = params.get('dateFrom', None)
    if rawFrom is None:
        dateFrom = Order.objects.all().order_by('date').first().date
    else:
        # need to make it TZ aware
        dateFrom = datetime.fromisoformat(rawFrom).astimezone(timezone.get_default_timezone())
    rawTo = params.get('dateTo', None)
    if rawTo is None:
        dateTo = timezone.now()
    else:
        dateTo = datetime.fromisoformat(rawTo).astimezone(timezone.get_default_timezone())

    allOrderDatesInRange = Order.objects.order_by("date")
    results = [[_("Date"), _("Total ordered"), _("Countervalue")]]
    dateset = set()
    for order in allOrderDatesInRange:
        ordDate = datetime(order.date.year, order.date.month, order.date.day)
        # get the amount ordered to ordDate
        ordAmount = Order.objects.amountOrderedInPeriod(request.user, stocks=None, start=None, end=ordDate)
        if ordDate in dateset:
            continue
        # get the countervalue of the selected owned stocks at date
        countervalue = StockQuote.objects.CountervalueAtDate(ordDate)
        results.append([ordDate, ordAmount, countervalue])
    context = {"data": results}
    # return render(request, "tradinglog/tradinghistory.html", context)
    return JsonResponse(context)