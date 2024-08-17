from rest_framework import serializers
from .models import CashDesk,CashOperations

class CashDeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashDesk
        fields = '__all__'

class CashOperationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CashOperations
        fields = '__all__'


