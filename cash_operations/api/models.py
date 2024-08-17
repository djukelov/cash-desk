from django.db import models
import datetime
from django.db.models import Max


class CashDesk(models.Model):
    id = models.AutoField(primary_key=True)
    bgn_balance = models.DecimalField(max_digits=100,decimal_places=2, default=1000.00)
    eur_balance = models.DecimalField(max_digits=100,decimal_places=2, default=2000.00)
    #define all available bills and coins for the currency in this case we use only those which are given in the task
    #BGN
    bgn_10 = models.IntegerField(default=50)
    bgn_50 = models.IntegerField(default=10)
    #EUR
    eur_10 = models.IntegerField(default=100)
    eur_20 = models.IntegerField(default=0)
    eur_50 = models.IntegerField(default=20)

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, default='martina')
    first_name = models.CharField(max_length=100, default='MARTINA')
    last_name = models.CharField(max_length=100, default='MARTINA')

class CashOperations(models.Model):
    operation_type = models.CharField(max_length=100)
    operation_currency = models.CharField(max_length=100)
    transaction_number = models.PositiveIntegerField(unique=True, editable=False)
    transaction_date = models.DateTimeField(default=datetime.datetime.now,editable=False,blank=True)
    bgn_amount = models.DecimalField(max_digits=100,decimal_places=2,default=0)
    eur_amount = models.DecimalField(max_digits=100,decimal_places=2,default=0)
    #BGN
    bgn_10 = models.IntegerField(default=0)
    bgn_50 = models.IntegerField(default=0)
    #EUR
    eur_10 = models.IntegerField(default=0)
    eur_20 = models.IntegerField(default=0)
    eur_50 = models.IntegerField(default=0)
    cash_desk_id = models.ForeignKey(CashDesk, on_delete=models.CASCADE, related_name='transactions')
    #we use protect to prevent the deletion of users who have related transactions
    user_id = models.ForeignKey(Users, on_delete=models.PROTECT, related_name='transactions')

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            # Get the maximum transaction number so far and add 1
            max_number = CashOperations.objects.aggregate(max_number=Max('transaction_number'))['max_number']
            if max_number is None:
                max_number = 0
            self.transaction_number = max_number + 1
        super().save(*args, **kwargs)



