# Generated by Django 5.0.3 on 2024-08-17 10:04

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_cashdesk_transaction_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(default='martina', max_length=100)),
                ('first_name', models.CharField(default='MARTINA', max_length=100)),
                ('last_name', models.CharField(default='MARTINA', max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='cashdesk',
            name='transaction_date',
        ),
        migrations.RemoveField(
            model_name='cashdesk',
            name='transaction_number',
        ),
        migrations.RemoveField(
            model_name='cashdesk',
            name='username',
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_type', models.CharField(max_length=100)),
                ('transaction_number', models.PositiveIntegerField(editable=False, unique=True)),
                ('transaction_date', models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False)),
                ('bgn_amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('eur_amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('bgn_10', models.IntegerField(default=0)),
                ('bgn_50', models.IntegerField(default=0)),
                ('eur_10', models.IntegerField(default=0)),
                ('eur_20', models.IntegerField(default=0)),
                ('eur_50', models.IntegerField(default=0)),
                ('cash_desk_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='api.cashdesk')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='api.users')),
            ],
        ),
    ]
