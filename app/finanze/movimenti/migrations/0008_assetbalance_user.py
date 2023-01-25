# Generated by Django 4.1.4 on 2023-01-13 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movimenti', '0007_subcategory_user_category_category_unique_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetbalance',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]