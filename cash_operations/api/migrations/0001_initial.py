# Generated by Django 5.0.3 on 2024-08-16 12:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CashDesk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='MARTINA', max_length=100)),
                ('bgn_balance', models.DecimalField(decimal_places=2, default=1000.0, max_digits=100)),
                ('eur_balance', models.DecimalField(decimal_places=2, default=2000.0, max_digits=100)),
                ('bgn_10', models.IntegerField(default=0)),
                ('bgn_50', models.IntegerField(default=0)),
                ('eur_10', models.IntegerField(default=0)),
                ('eur_20', models.IntegerField(default=0)),
                ('eur_50', models.IntegerField(default=0)),
                ('transaction_date', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
    ]
