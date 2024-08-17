# cashier/urls.py
from django.urls import path
from .views import CashOperationsView,CashDeskBalanceView

urlpatterns = [
    path('v1/cash-operation', CashOperationsView.as_view(), name='cash-operation'),
    path('v1/cash-balance', CashDeskBalanceView.as_view(), name='cash-balance'),

]