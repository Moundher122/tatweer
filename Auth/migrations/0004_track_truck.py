# Generated by Django 5.0.6 on 2025-02-07 23:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0003_alter_transport_price_per_day_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='truck',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='Auth.truck'),
        ),
    ]
