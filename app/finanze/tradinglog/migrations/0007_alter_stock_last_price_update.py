# Generated by Django 3.2.7 on 2022-02-01 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradinglog', '0006_stock_last_price_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_price_update',
            field=models.DateTimeField(),
        ),
    ]