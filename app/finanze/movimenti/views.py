from datetime import date, datetime, timedelta
from json import loads as jloads
from urllib.parse import parse_qs, unquote, urlparse

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Max, Min, Q, Sum, FloatField
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render as srender
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from tradinglog.models import Order
from . import app_name, logger
from .forms import NewAssetsBalanceForm, NewMovementForm
from .models import AssetBalance, Category, Movement, Subcategory


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
            filterdict["{}_id".format(col)] = val
    # if no date range was specified, pick the last three months only
    if "date__gte" not in filterdict and "date__lt" not in filterdict:
        dateto = datetime.now() 
        datefrom = dateto - timedelta(90)
        filterdict["date__gte"] = datefrom
        filterdict["date__lt"] = dateto
    logger.debug("Filter dict: {}".format(filterdict))
    retmovements = Movement.objects.filter(**filterdict)
    
    return retmovements.order_by('-date')


@login_required
def movement(request, id: int):
    if request.method == 'GET':
        movements = []
        for mov in Movement.objects.filter(id=id):
            movementDict = {}
            movementDict['id'] = mov.id
            movementDict['date'] = mov.date
            movementDict['amount'] = mov.amount
            movementDict['description'] = mov.description
            movementDict['category'] = {'category': mov.category.category, 'id': mov.category.id}
            movementDict['subcategory'] = {'subcategory': mov.subcategory.subcategory, 'id': mov.subcategory.id}
            movements.append(movementDict)
        return JsonResponse({"movements": movements})
    elif request.method == 'POST':
        params = request.POST
        res = {"updated": True, "message": _("Updated")}
        validfields = ['date', 'abs_amount',
                       'description', 'category', 'subcategory', ]
        # BEWARE: QueryDict.items transforms list values into their last, single element
        filterparams = { k:v for (k,v) in params.items() if k in validfields}
        logger.debug("[movement][UPDATE] parameters: %s" % str(filterparams))
        Movement.objects.filter(id=id).update(**filterparams)
        return JsonResponse(res)
    else:
        return JsonResponse({"message": _("Invalid request")})

@login_required
def deleteMovement(request):
    if request.method == 'POST':
        params = request.POST
        movId = params.get("id")
        # return JsonResponse({"deleted": True, "message": f"No deletion actually occurred. Selected item: {movId}"})
        totdeleted, deletedDetails = Movement.objects.get(id=movId).delete()
        if totdeleted < 1:
            return JsonResponse({"deleted": False, "message": _(f"No entry with id {movId}")})
        else:
            return JsonResponse({"deleted": True})
    else:
        return JsonResponse({"message": _("Invalid request"), "deleted": False})

@login_required
def list(request):
    params = request.GET
    movement_list = _filterMovements(request.user, params.getlist('filter'))
    qSumOut = Sum('abs_amount', filter=Q(category__direction=Category.OUTCOME), output_field=FloatField())
    qSumIn = Sum('abs_amount', filter=Q(category__direction=Category.INCOME), output_field=FloatField())
    cats = Category.objects.all()
    subcats = Subcategory.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(movement_list, 50)  # Show 50 items per page.
    page_obj = paginator.get_page(page)

    return render(request,
                  'movimenti/list.html',
                  {'page_obj': page_obj,
                   'movements': movement_list,
                   'summary': movement_list.aggregate(count=Count('id'), incomes=qSumIn, expenses=qSumOut, savingrate=(qSumIn - qSumOut)/qSumIn * 100, datefrom=Min('date'), dateto=Max('date')),
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
            errors = form.errors
            return render(request, 'movimenti/newmovement.html', {'form': form, 'errors': errors})

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
    latest = Movement.objects.filter(
        user=request.user,date__lte=datetime.today()).order_by('date').last().date
    for midx in range(1, 13):
        # year is not important here
        iterdate = date(latest.year, midx, 1)
        mname = _(iterdate.strftime("%B"))
        isCurrent = latest.month == midx
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
    totals = {'ins': {'amount': 0}, 'outs': {'amount': 0}, 'days': (dateTo-dateFrom).days}
    start = None
    end = None
    for cat in Category.objects.filter(user=request.user):
        start, end, outs = cat.movementsInDatesRange(request.user, Category.OUTCOME, dateFrom, dateTo)
        start, end, ins = cat.movementsInDatesRange(request.user, Category.INCOME, dateFrom, dateTo)
        empty = (outs.get("amount", 0) == 0 and ins.get("amount", 0) == 0)
        results.append({"cat": {"id": cat.id, "cat": cat.category}, "outs": outs, "ins": ins, "empty": empty})
        totals['ins']['amount'] += ins['amount']
        totals['outs']['amount'] += outs['amount']
    totals['net'] = {'amount': totals['ins']['amount'] - totals['outs']['amount']}
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

def _group_assets_by_date_and_total_balance(requestUser):
    groupByDateAndTotalBalance = AssetBalance.objects.filter(user__id=requestUser.id).values(
        'date').annotate(totbalance=Sum('balance')).order_by('-date')
    for idx in range(0, len(groupByDateAndTotalBalance) - 1):
        rec_to = groupByDateAndTotalBalance[idx]
        rec_from = groupByDateAndTotalBalance[idx+1]
        truebalance = rec_to['totbalance'] - rec_from['totbalance']
        period = Movement.objects.netAmountInPeriod(
            requestUser, rec_from['date'], rec_to['date'])
        groupByDateAndTotalBalance[idx]['accounted'] = period
        groupByDateAndTotalBalance[idx]['truebalance'] = truebalance
        groupByDateAndTotalBalance[idx]['error'] = truebalance - period
    return groupByDateAndTotalBalance

@login_required
def assets(request):
    if request.method == 'POST':
        jres = {"errors": [], "warnings": []}
        deser = request.POST
        date = deser.get('date')
        asset_labels = deser.getlist('balance_item_key')
        asset_vals = deser.getlist('balance_item_val')
        if date is None or asset_labels is None or asset_vals is None:
            jres['errors'].append("Missing input.")
        elif len(asset_labels) != len(asset_vals):
            jres['errors'].append("Invalid input.")
        else:
            # logger.debug("asset data: {}".format(str(deser)))
            index = -1
            for key, val in zip(asset_labels, asset_vals):
                index = 0
                if len(val) == 0:
                    val = "0"
                try:
                    fval = float(val)
                except ValueError:
                    jres['warnings'].append("Invalid value for item %d: %s" % (index, val))
                    continue
                ab = AssetBalance()
                ab.date = date
                ab.balance = fval
                ab.notes = key
                ab.user = request.user
                try:
                    ab.save()
                except Exception as ex:
                    jres['errors'].append("Error saving item %d: %s" % (index, str(ex)))
                    continue
        response = JsonResponse(jres)
        return response
    else:
        form = NewAssetsBalanceForm()
        allrecords = AssetBalance.objects.filter(user__id=request.user.id).order_by('-date')
        groupByDateAndTotalBalance = _group_assets_by_date_and_total_balance(
            request.user)
        if request.path.find("/json") >= 0:
            # send json data
            data = []
            for val in groupByDateAndTotalBalance.reverse():
                val['date'] = int(val['date'].timestamp() * 1000)
                data.append(val)
            return JsonResponse({
                "chartdata": {
                    "data": data, 
                    "title": _("Assets time series"),
                    "xTitle": _("Date"),
                    "yTitle": _("Total assets"),
                    }
                })
        latests = []
        latsum = 0
        if len(allrecords) > 0:
            latestpostdate = allrecords[0].date
            for rec in allrecords:
                if rec.date == latestpostdate:
                    latests.append(rec)
                    latsum += rec.balance
                else:
                    break
        else:
            logger.debug("[assets] no records found for user %s" % str(request.user))
        # Insert finance assets total by default
        financeassets = 0
        for buy in Order.objects.all():
            financeassets += buy.amount
        response = render(request, 'movimenti/assetbalance.html',
            {'form': form, 'assets': groupByDateAndTotalBalance, 'latests': latests, 'financeassets': financeassets, 'totalassets': latsum})
        response.set_cookie("user", request.user, path=request.path)
        return response

@login_required
def time_series(request):
    params = request.GET
    filterdict = {"user__id": request.user.id}
    # fetch the last assets record before request's start time, if any. Take baseline value 0 if none
    rawFrom = params.get('datefrom', None)
    minDate = Movement.objects.all().order_by('date').first().date
    maxDate = Movement.objects.all().order_by('-date').first().date
    if rawFrom is None:
        dateFrom = minDate
    else:
        # need to make it TZ aware
        dateFrom = datetime.fromisoformat(rawFrom).astimezone(timezone.get_default_timezone())
    filterdict["date__gte"] = dateFrom
    rawTo = params.get('dateto', None)
    if rawTo is None:
        dateTo = timezone.now()
    else:
        dateTo = datetime.fromisoformat(rawTo).astimezone(timezone.get_default_timezone())
        # dateTo.tzinfo = timezone.get_default_timezone()
    filterdict["date__lt"] = dateTo
    lastAsset = AssetBalance.objects.filter(
        user__id=request.user.id, date__lte=dateFrom).order_by('-date').values(
            'date').annotate(sum=Sum('balance')).first()
    if lastAsset is None:
        logger.debug("[time_series] no asset records found prior to date %s. Baseline set to 0." % dateFrom.isoformat())
        baseline = 0
    else:
        baseline = lastAsset['sum']
        filterdict["date__gte"] = lastAsset['date']
        logger.debug("[time_series] Baseline set to the last asset record before date %s: %f." % (dateFrom.isoformat(), baseline))

    # smear factor
    nMovementsInRange = Movement.objects.filter(**filterdict).count()
    MAX_POINTS_REF = 100
    reduce_factor = max(int(nMovementsInRange/MAX_POINTS_REF), 1)
    if reduce_factor > 1:
        logger.debug(f"[time_series] Will reduce movement series points from {nMovementsInRange} to {int(nMovementsInRange/reduce_factor)}")
    running_balance = baseline # Movement.objects.netAmountInPeriod(user=request.user, toDate=dateFrom) # starting point
    minVal = running_balance
    maxVal = running_balance
    loop_filter_dict = {"user__id": request.user.id}
    results = [[_("Date"), _("Balance"), _("Assets")]]
    # results.append([dateFrom.date(), running_balance, baseline])
    movement_count = 1
    for movement in Movement.objects.filter(**filterdict).order_by("date"):
        running_balance += movement.amount
        minVal = min(minVal, running_balance)
        maxVal = max(maxVal, running_balance)
        if movement_count % reduce_factor == 0:
            refdate = movement.date
            if refdate > dateFrom:
                loop_filter_dict["date__lt"] = refdate
                latestAsset = AssetBalance.objects.filter(**loop_filter_dict).order_by("-date").values("date").annotate(totbalance=Sum("balance")).first()
                results.append([movement.date, running_balance, latestAsset["totbalance"]])
        movement_count += 1

    return JsonResponse({
        "data": results, 
        "metadata": {
            "chart": {
                "title": _("Movements time series"),
                "xTitle": _("Date"),
                "yTltle": _("Balance"),
            },
            "minDate": minDate,
            "maxDate": maxDate,
            "minVal": minVal,
            "maxVal": maxVal,
            "dateFrom": dateFrom,
            "dateTo": dateTo,
        }})
    

@login_required
def newcategory(request):
    errors = []
    if request.method != 'POST':
        errors.append(_("invalid request"))
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
