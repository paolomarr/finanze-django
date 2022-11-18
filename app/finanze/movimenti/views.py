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
from json import loads as jloads
from django.http import JsonResponse
from datetime import date

logger = logging.getLogger(__name__)


@login_required
def index(request):
    return HttpResponseRedirect('/movimenti/list')


def _filterMovements(filterParams):
    filterdict = {}
    logger.debug("Filter parameters: {}".format(filterParams))
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
        logger.debug("Filter dict: {}".format(filterdict))
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
    errors = []
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
        else:
            errors.append("Form not valid (tbd)")


    emptySubcat = Subcategory.objects.get(subcategory="")
    form = NewMovementForm(initial={'subcategory': emptySubcat.id})
    return render(request, 'movimenti/newmovement.html', {'form': form, 'errors': errors})


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

    years = Movement.objects.dates('date', 'year', order='DESC')
    # create a list of months, indicating the selected one
    months = []
    for midx in range(1,13):
        # year is not important here
        iterdate = date(start.year, midx, 1)
        mname = iterdate.strftime("%B")
        isCurrent = start.month == midx
        months.append({"idx": midx, "name": mname, "isCurrent": isCurrent})
    context = {
        'availableYears': years,
        'results': results,
        'start': start,
        'end': end,
        'totals': totals,
        'months': months
    }
    return render(request, 'movimenti/summary.html', context)

@login_required
def assets(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            jres = {'errors': []}
            try:
                deser = jloads(request.body)
            except Exception as ex:
                jres['errors'].append("Error parsing input data as JSON string: {}\
".format(ex.message))
            else:
                logger.debug("asset data: {}".format(str(deser)))
                items = deser.get('assetItems', [])
                # todo: sanitise/check input
                if len(items) == 0:
                    jres['errors'].append("empty data")
                else:
                    logger.debug("Received {} asset items to record".format(len(items)))
                    for item in items:
                        ab = AssetBalance()
                        ab.date = item['date']
                        ab.balance = item['balance']
                        ab.notes = item['notes']
                        try:
                            ab.save()
                        except Exception as ex:
                            jres['errors'].append("Error parsing input data as JSON string: {}\
".format(ex.message))
            response = JsonResponse(jres)
            return response
        else:
            return HttpResponseRedirect('/movimenti/assets')
    else:
        form = NewAssetsBalanceForm()
        allrecords = AssetBalance.objects.all().order_by('-date')
        latestpostdate = allrecords[0].date
        latests = []
        for rec in allrecords:
            if rec.date == latestpostdate:
                latests.append(rec)
            else:
                break
        groupByDateAndTotalBalance = AssetBalance.objects.values('date').annotate(totbalance=Sum('balance')).order_by('-date')
        for idx in range(0, len(groupByDateAndTotalBalance) - 1):
            rec_to = groupByDateAndTotalBalance[idx]
            rec_from = groupByDateAndTotalBalance[idx+1]
            truebalance = rec_to['totbalance'] - rec_from['totbalance']
            period = Movement.objects.netAmountInPeriod(rec_from['date'], rec_to['date'])
            groupByDateAndTotalBalance[idx]['accounted'] = period
            groupByDateAndTotalBalance[idx]['truebalance'] = truebalance
            groupByDateAndTotalBalance[idx]['error'] = truebalance - period

        # Insert finance assets total by default
        financeassets = 0
        for buy in Order.objects.filter(operation__operation='BUY'):
            financeassets += buy.amount
        for buy in Order.objects.filter(operation__operation='SELL'):
            financeassets -= buy.amount
        response = render(request, 'movimenti/assetbalance.html',
            {'form': form, 'assets': groupByDateAndTotalBalance, 'latests': latests, 'financeassets': financeassets})
        response.set_cookie("user", request.user, path=request.path)
        return response