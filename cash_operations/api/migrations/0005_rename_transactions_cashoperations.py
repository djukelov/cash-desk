# Generated by Django 5.0.3 on 2024-08-17 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_users_remove_cashdesk_transaction_date_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Transactions',
            new_name='CashOperations',
        ),
    ]
