# Generated by Django 3.2.7 on 2022-02-01 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradinglog', '0005_alter_stock_regular_market_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='last_price_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]