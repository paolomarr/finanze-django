from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, F
from .models import Movement, Category, Subcategory, AssetBalance
from tradinglog.models import Order
from .forms import NewMovementForm, NewAssetsBalanceForm
import logging
from urllib.parse import unquote, urlparse, parse_qs
from django.views.generic import CreateView


@login_required
def index(request):
    return HttpResponseRedirect('/movimenti/list')


def _filterMovements(filterParams):
    filterdict = {}
    logging.debug("Filter parameters: {}".format(filterParams))
    for rawitem in filterParams:
        item = unquote(rawitem)
        col = item.split("=")[0]
        val = item.split("=")[1]
        if col == 'description':
            filterdict['description__icontains'] = val
        if col == 'datefrom':
            filterdict['date__gte'] = val
        if col == 'dateto':
            filterdict['date__lt'] = val
        if col in ['category', 'subcategory']:
            filterdict = {"{}_id".format(col): val}
    if len(filterdict) > 0:
        logging.debug("Filter dict: {}".format(filterdict))
        retmovements = Movement.objects.filter(**filterdict)
    else:
        retmovements = Movement.objects.all()

    return retmovements.order_by('-date')


@login_required
def list(request):
    params = request.GET
    movement_list = _filterMovements(params.getlist('filter'))
    cats = Category.objects.all()
    subcats = Subcategory.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(movement_list, 50)  # Show 25 contacts per page.
    page_obj = paginator.get_page(page)

    return render(request,
                  'movimenti/list.html',
                  {'page_obj': page_obj,
                   'movements': movement_list,
                   'categories': cats, 'subcategories': subcats})


@login_required
def newmovement(request):
    if request.method == 'POST':
        needmore = request.POST.get('another', False)
        # parse the form and add new item
        form = NewMovementForm(request.POST)
        if form.is_valid():
            form.save()
            # redirect to a new URL:
            redirect = '/movimenti/list'
            if needmore == '1':
                redirect = '/movimenti/new'
            return HttpResponseRedirect(redirect)
        return

    emptySubcat = Subcategory.objects.get(subcategory="")
    form = NewMovementForm(initial={'subcategory': emptySubcat.id})
    return render(request, 'movimenti/newmovement.html', {'form': form})


@login_required
def summary(request):
    params = request.GET
    year = params.get('year', None)
    month = params.get('month', None)

    results = []
    totals = {'ins': 0, 'outs': 0}
    start = None
    end = None
    for cat in Category.objects.all():
        start, end, outs = cat.movementsInPeriod(Category.OUTCOME, year, month)
        start, end, ins = cat.movementsInPeriod(Category.INCOME, year, month)
        results.append({"cat": cat, "outs": outs, "ins": ins})
        totals['ins'] += ins['amount']
        totals['outs'] += outs['amount']

    # years = Movement.objects.distinct(Extract('date', 'year'))
    years = Movement.objects.dates('date', 'year', order='DESC')
    context = {
        'availableYears': years,
        'results': results,
        'start': start,
        'end': end,
        'totals': totals
    }
    return render(request, 'movimenti/summary.html', context)

@login_required
def assets(request):
    if request.method == 'POST':
        form = NewAssetsBalanceForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/movimenti/assets')
    else:
        form = NewAssetsBalanceForm()
        allrecords = AssetBalance.objects.all().order_by('-date')
        for idx in range(0, len(allrecords) - 1):
            rec_to = allrecords[idx]
            rec_from = allrecords[idx+1]
            truebalance = rec_to.balance - rec_from.balance
            period = Movement.objects.netAmountInPeriod(rec_from.date, rec_to.date)
            setattr(allrecords[idx], 'accounted', period)
            setattr(allrecords[idx], 'truebalance', truebalance)
            setattr(allrecords[idx], 'error', truebalance - period)

        # Insert finance assets total by default
        financeassets = 0
        for buy in Order.objects.filter(operation__operation='BUY'):
            financeassets += buy.amount
        for buy in Order.objects.filter(operation__operation='SELL'):
            financeassets -= buy.amount
        return render(request, 'movimenti/assetbalance.html',
            {'form': form, 'assets': allrecords, 'financeassets': financeassets})
