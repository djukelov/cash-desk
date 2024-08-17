from django.contrib import admin
from .models import CashDesk,CashOperations,Users

@admin.register(CashDesk)
class CashDeskAdmin(admin.ModelAdmin):
    list_display = ('id', 'bgn_balance', 'eur_balance','bgn_10' ,'bgn_50', 'eur_10', 'eur_20','eur_50')

@admin.register(CashOperations)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('operation_type', 'transaction_number', 'transaction_date', 'bgn_amount', 'eur_amount','bgn_10','bgn_50','eur_10','eur_20','eur_50','cash_desk_id')

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id','username','first_name','last_name')
