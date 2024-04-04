from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Expression
from django.db.models.functions import Coalesce

from django.utils import timezone
from datetime import date
from hashlib import md5


class Subcategory(models.Model):
    subcategory = models.CharField(max_length=50)
    user = models.ManyToManyField(User)

    def __str__(self):
        return self.subcategory


class Category(models.Model):
    INCOME = 1.0
    OUTCOME = -1.0
    DIRECTIONS = [
        (INCOME, 'Income'),
        (OUTCOME, 'Outcome')
    ]
    category = models.CharField(max_length=50)
    direction = models.FloatField(choices=DIRECTIONS)
    user = models.ManyToManyField(User)

    class Meta:
        constraints = [
            models.UniqueConstraint(name='category_unique_idx', fields=['category', 'direction'])
        ]

    def __str__(self):
        return self.category

    def movementsInPeriod(self, user, direction, year=None, month=0):
        if not year:
            year = date.today().year
        else:
            year = int(year)
        if not month:
            month = date.today().month
        else:
            month = int(month)
        allmovements = self.movement_set.all()
        if month > 0:
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, month + 1, 1)
        else: # if no month give, take the whole year
            start = date(year, 1, 1)
            end = date(year, 12, 1)
        return self.movementsInDatesRange(user, direction, start, end)
        
    def movementsInDatesRange(self, user, direction: float, dateFrom: date, dateTo: date=date.today()):
        if not dateTo > dateFrom:
            return (dateFrom, dateTo, [])
        else:
            allmovements = self.movement_set.all()
            filtered = allmovements.filter(
                user=user,
                date__range=(dateFrom, dateTo),
                category__direction=direction).aggregate(
                amount=Coalesce(Sum('abs_amount', default=0.0), 0.0))
            return (dateFrom, dateTo, filtered)
        
class MovementManager(models.Manager):
    def netAmountInPeriod(self, user, fromDate=None, toDate=None):
        amount = 0
        filterDict = {"user": user}
        if fromDate is not None:
            filterDict['date__gte'] = fromDate
        if toDate is not None:
            filterDict['date__lt'] = toDate
        for movement in self.filter(**filterDict):
            amount += movement.amount
        return amount


class Movement(models.Model):
    objects = MovementManager()

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    date = models.DateTimeField()
    description = models.CharField(max_length=1024)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    abs_amount = models.FloatField()
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        subcatstr = ""
        if self.subcategory and len(self.subcategory.subcategory) > 0:
            subcatstr = " | (%s)" % self.subcategory.subcategory
        username = "-"
        if self.user is not None:
            username = self.user.get_username()
        return "[{}] {} | {} ({}) | {}€{}\
".format(
            username,
            self.date,
            self.description,
            self.category,
            self.amount,
            subcatstr)

    @property
    def amount(self):
        return self.category.direction * self.abs_amount
    
    @property
    def is_future(self):
        return self.date > timezone.now()


class AssetBalanceManager(models.Manager):
    def balance_to_date(self, user: User, date: date) -> tuple[date, float]:
        outbalance = 0.0
        refdate = None
        for entry in self.filter(user=user, date__lte=date).order_by("-date"):
            if not refdate:
                refdate = entry.date
            elif entry.date != refdate:
                break
            else:
                outbalance += entry.balance
        return (refdate, outbalance)

    def initial_balance(self, user: User) -> tuple[date, float]:
        outbalance = 0.0
        refdate = None
        for entry in self.filter(user=user).order_by("date"):
            if not refdate:
                refdate = entry.date
            elif entry.date != refdate:
                break
            else:
                outbalance += entry.balance
        return (refdate, outbalance)    

        
class AssetBalance(models.Model):
    """
    each instance of this model represents
    a snapshot of own's total assets' value
    """
    objects = AssetBalanceManager()
    date = models.DateTimeField(default=timezone.now)    
    balance = models.FloatField()
    notes = models.CharField(blank=True, max_length=256)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    
    def __str__(self):
        return f"[{self.id}] {self.user.get_username()} - {self.date.strftime('%x %X')} | {self.notes} | {self.balance}"

    @property
    def submission_id(self):
        timestamp = str(int(self.date.timestamp()))
        return md5(timestamp.encode()).hexdigest()