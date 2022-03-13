from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone


class Subcategory(models.Model):
    subcategory = models.CharField(max_length=50)

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

    def __str__(self):
        return self.category

    def movementsInPeriod(self, direction, year=None, month=0):
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
        else:
            start = date(year, 1, 1)
            end = date(year, 12, 1)
        filtered = allmovements.filter(
            date__range=(start, end),
            category__direction=direction).aggregate(
                amount=Coalesce(Sum('abs_amount', default=0.0), 0.0))
        return (start, end, filtered)


class Movement(models.Model):
    date = models.DateTimeField()
    description = models.CharField(max_length=1024)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    abs_amount = models.FloatField()
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT)

    def __str__(self):
        subcatstr = ""
        if len(self.subcategory.subcategory) > 0:
            subcatstr = " | (%s)" % self.subcategory.subcategory
        return "{} | {} ({}) | {}€{}\
".format(
            self.date,
            self.description,
            self.category,
            self.amount,
            subcatstr)

    @property
    def amount(self):
        return self.category.direction * self.abs_amount


class AssetBalance(models.Model):
    """
    each instance of this model represents
    a snapshot of own's total assets' value
    """
    date = models.DateTimeField(default=timezone.now)    
    balance = models.FloatField()
    notes = models.TextField()

