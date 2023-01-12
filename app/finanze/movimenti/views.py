from django.shortcuts import render as srender
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, F
from .models import Movement, Category, Subcategory, AssetBalance
from django.contrib.auth.models import User
from tradinglog.models import Order
from .forms import NewMovementForm, NewAssetsBalanceForm
from urllib.parse import unquote, urlparse, parse_qs
from json import loads as jloads
from django.http import JsonResponse
from datetime import date, datetime
from django.utils.translation import gettext as _
from . import logger
from django.apps import apps
from . import app_name
from django.urls import reverse
import re

def render(request, path, context):
    request.current_app = apps.get_app_config(app_name).verbose_name
    context['base_app_path'] = reverse("index", current_app=app_name)
    return srender(request, path, context)


@login_required
def index(request):
    return HttpResponseRedirect('/movimenti/list')


def _filterMovements(user, filterParams):
    filterdict = {"user": user}
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
    logger.debug("Filter dict: {}".format(filterdict))
    retmovements = Movement.objects.filter(**filterdict)
    
    return retmovements.order_by('-date')


@login_required
def list(request):
    params = request.GET
    movement_list = _filterMovements(request.user, params.getlist('filter'))
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
            newmovement = form.save(commit=False)
            newmovement.user = request.user
            newmovement.save()
            form.save_m2m() # useful if any many2many relation is defined
            # redirect to a new URL:
            redirect = '/movimenti/list'
            if needmore == '1':
                redirect = '/movimenti/new'
            return HttpResponseRedirect(redirect)
        else:
            errors.append("Form not valid (tbd)")


    emptySubcat = Subcategory.objects.get(subcategory="")
    form = NewMovementForm(initial={'subcategory': emptySubcat.id})
    form.fields["category"].empty_label = _("Select category")
    form.fields["category"].queryset = User.objects.get(username=request.user.username).category_set.all()
    return render(request, 'movimenti/newmovement.html', {'form': form, 'errors': errors})


@login_required
def summary(request):
    years = Movement.objects.filter(user=request.user).dates('date', 'year', order='DESC')
    # create a list of months, indicating the selected one
    months = []
    today = Movement.objects.order_by('date').last().date
    for midx in range(1, 13):
        # year is not important here
        iterdate = date(today.year, midx, 1)
        mname = _(iterdate.strftime("%B"))
        isCurrent = today.month == midx
        months.append({"idx": midx, "name": mname, "isCurrent": isCurrent})
    context = {
        'availableYears': years,
        'months': months
    }
    return render(request, 'movimenti/summary_ajax.html', context)


@login_required
def summaryXHR(request):
    params = request.GET
    logger.debug("[summaryXHR] Raw params: %s" % str(params))
    dateFrom = datetime.fromisoformat(params['dateFrom'])
    dateTo = datetime.fromisoformat(params['dateTo'])
    logger.debug("Requested summary from %s to %s" % (dateFrom, dateTo))
    results = []
    totals = {'ins': {'amount': 0}, 'outs': {'amount': 0}}
    start = None
    end = None
    for cat in Category.objects.all():
        start, end, outs = cat.movementsInDatesRange(request.user, Category.OUTCOME, dateFrom, dateTo)
        start, end, ins = cat.movementsInDatesRange(request.user, Category.INCOME, dateFrom, dateTo)
        results.append({"cat": {"id": cat.id, "cat": cat.category}, "outs": outs, "ins": ins})
        totals['ins']['amount'] += ins['amount']
        totals['outs']['amount'] += outs['amount']
    outdata = {
        'results': results,
        'totals': totals,
        'start': start,
        'end': end
    }
    if request.path.find("/fetch") > 0:
        return render(request, 'movimenti/summary/table.html', outdata)
    else:
        return JsonResponse(outdata)


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
            period = Movement.objects.netAmountInPeriod(request.user, rec_from['date'], rec_to['date'])
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

@login_required
def newcategory(request):
    errors = []
    if request.method != 'POST':
        errors.append("invalid request")
    else:
        params = request.POST
        catname = params.get('category', '')
        catdir = params.get('direction')
        if int(catdir) not in [Category.INCOME, Category.OUTCOME]:
            errors.append("invalid direction value")
        elif len(catname) == 0:
            errors.append("category name cannot be empty")
        else:
            newcat = Category.objects.create(category=catname, direction=int(catdir))
            newcat.save()
            newcat.user.add(request.user)
            newcat.save()
    return JsonResponse({"errors": errors})
    
@login_required
def categories(request):
    if request.method == 'POST':
        params = request.POST
        cats = params.getlist('category', [])
        vals = params.getlist('checked', [])
        errors = []
        if len(cats) == 0 or len(cats) != len(vals):
            errors.append("Input arrays error")
        else:
            logger.debug("Categories %s" % str(cats))
        for cat, checked in zip(cats,vals):
            category = Category.objects.get(id=cat)
            if checked == "true":
                logger.debug("Adding user %s to category %s" % (str(request.user), category.category))
                category.user.add(request.user)
            else:
                logger.debug("Removing user %s from category %s" %
                             (str(request.user), category.category))
                category.user.remove(request.user)
            category.save()
        return JsonResponse({"result": "ok", "errors": errors})
    else:
        cats = Category.objects.all()
        context = {'cats': []}
        for cat in cats:
            if cat.user.filter(username=request.user.username).first() is not None:
                cat.__setattr__("has_user", True)
            else:
                cat.__setattr__("has_user", False)
            context['cats'].append(cat)
        return render(request, 'movimenti/categories.html', context)
