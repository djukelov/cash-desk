from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CashDesk,CashOperations,Users
from .serializers import CashOperationsSerializer,CashDeskSerializer
from django.http import JsonResponse
from django.views import View
from rest_framework.permissions import IsAuthenticated
import datetime
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta


class CashOperationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        #data validation from request
        operation_choices = ['withdraw', 'deposit']
        currency_choices = ['BGN','EUR']
        serializer = CashOperationsSerializer(data=request.data)
        if serializer.is_valid():
            cash_desk = CashDesk.objects.get(id=request.data.get('cash_desk_id'))
            cash_desk_serializer = CashDeskSerializer(cash_desk)
            now = timezone.now()
            start_of_day = timezone.make_aware(datetime.combine(now.date(), datetime.min.time()))
            end_of_day = start_of_day + timedelta(days=1) 

            #CHECK FOR CORRECT OPERATION 
            if request.data.get('operation_type') not in operation_choices:
                return Response({"error": "Incorect Operation type."},status=status.HTTP_404_NOT_FOUND)
            #CHECK FOR CORRECT CURRENCY
            if request.data.get('operation_currency') not in currency_choices:
                return Response({"error": "Incorect currency."},status=status.HTTP_404_NOT_FOUND)

            #CHECK IF AMOUNT IS EQUAL TO DOMINATIONS
            if request.data.get('operation_currency') == 'BGN':
                sum_denom = Decimal(request.data.get('bgn_10')) * 10 + Decimal(request.data.get('bgn_50')) * 50
                if request.data.get('bgn_amount') !=  sum_denom:
                        return Response({"error": "The total BGN amount does not match the sum of its denominations."},status=status.HTTP_404_NOT_FOUND)
                #IF OPERATION IS WITHDRAW check if amount isn`t more than balance in Cash desk for today
                if (request.data.get('operation_type') == 'withdraw'):
                    bgn_start_balance = cash_desk_serializer.data['bgn_balance']
                    bgn_deposits = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day), operation_type='deposit'
                            ).aggregate(total_deposits = Sum('bgn_amount'))['total_deposits'] or 0
                    bgn_withdrawals = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(total_withdrawals = Sum('bgn_amount'))['total_withdrawals'] or 0
                    bgn_desk_balance = bgn_deposits - bgn_withdrawals
                    if(Decimal(request.data.get('bgn_amount')) > (Decimal(bgn_start_balance) + bgn_desk_balance)):
                        return Response({"error": "Insufficient BGN balance in the cash desk to complete the operation."},status=status.HTTP_404_NOT_FOUND)
            
            #CHECK IF AMOUNT IS EQUAL TO DOMINATIONS
            if (request.data.get('operation_currency') == 'EUR'):
                sum_denom = Decimal(request.data.get('eur_10')) * 10 + Decimal(request.data.get('eur_20')) * 20  + Decimal(request.data.get('eur_50')) * 50
                if(request.data.get('eur_amount') !=  sum_denom):
                        return Response({"error": "The total EUR amount does not match the sum of its denominations."},status=status.HTTP_404_NOT_FOUND)
                #IF OPERATION IS WITHDRAW check if amount isn`t more than balance in Cash desk
                if (request.data.get('operation_type') == 'withdraw'):
                    eur_start_balance = cash_desk_serializer.data['eur_balance']
                    eur_deposits = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day), operation_type='deposit'
                            ).aggregate(total_deposits = Sum('eur_amount'))['total_deposits'] or 0
                    eur_withdrawals = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(total_withdrawals = Sum('eur_amount'))['total_withdrawals'] or 0
                    eur_desk_balance = eur_deposits - eur_withdrawals
                    if(Decimal(request.data.get('eur_amount')) > Decimal(eur_start_balance) + eur_desk_balance):
                        return Response({"error": "Insufficient EUR balance in the cash desk to complete the operation."},status=status.HTTP_404_NOT_FOUND)

            saved_instance = serializer.save()

             # Log transaction
            try:
                #GET USERNAME FROM ID 
                user = Users.objects.get(pk=request.data.get('user_id')).username
                transaction_id =  saved_instance.transaction_number

                now = datetime.now()
                formatted_date = now.strftime('%d/%m/%Y %H:%M:%S')

                with open('transaction_history.txt', 'a') as f:
                    if (request.data.get('operation_currency') == 'BGN'):
                        f.write(f"{formatted_date} - ID:{transaction_id}, Operation:{request.data.get('operation_type').upper()}, Currency:{request.data.get('operation_currency')}, User:{user.upper()}\n")
                    if (request.data.get('operation_currency') == 'EUR'):
                        f.write(f"{formatted_date} - ID:{transaction_id}, Operation:{request.data.get('operation_type').upper()}, Currency:{request.data.get('operation_currency')}, Amount:{request.data.get('eur_amount')}, User:{user.upper()}\n")
            except IOError as e:
                print(f"An error occurred while writing to transaction_history.txt: {e}")
                # Update balance file
            try:
                with open('cash_balance.txt', 'a') as f:
                        f.write(f"TRANSACTION NUMBER:{transaction_id} FROM DATE:{formatted_date} \n")
                        f.write(f"BGN Balance:{request.data.get('bgn_amount')}\n")
                        f.write(f"{request.data.get('bgn_10')}x10BGN \n")
                        f.write(f"{request.data.get('bgn_50')}x50BGN\n")
                        f.write(f"EUR Balance:{request.data.get('eur_amount')}\n")
                        f.write(f"{request.data.get('eur_10')}x10EUR \n")
                        f.write(f"{request.data.get('eur_20')}x20EUR \n")
                        f.write(f"{request.data.get('eur_50')}x50EUR \n")
                        f.write(f"-----------------------------------------------------------\n")


            except IOError as e:
                print(f"An error occurred while writing to cash_balance.txt: {e}")

            return Response({"message": "Operation completed successfully!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    


class CashDeskBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cash_desk_data = []
        now = timezone.now()
        start_of_day = timezone.make_aware(datetime.combine(now.date(), datetime.min.time()))
        end_of_day = start_of_day + timedelta(days=1) 

       #CHECK VALID CASH DESK REQUEST
        try: 
            user = Users.objects.get(pk=request.data.get('user_id')).username
        except Exception as e:
            return Response({"error": "Invalid user."},status=status.HTTP_404_NOT_FOUND)
    
         #CHECK VALID USER REQUEST
        try: 
            cash_desk = CashDesk.objects.get(id=request.data.get('cash_desk_id'))
        except Exception as e:
            return Response({"error": "Invalid cash desk."},status=status.HTTP_404_NOT_FOUND)
        
        #The Desk Balance can be returned only if they are more than 2 deposits and 2 withdrawals

        # Count the number of deposits
        deposits_count = CashOperations.objects.filter(
            transaction_date__range=(start_of_day, end_of_day),
            operation_type='deposit'
        ).count()

        # Count the number of withdrawals
        withdrawals_count = CashOperations.objects.filter(
            transaction_date__range=(start_of_day, end_of_day),
            operation_type='withdraw'
        ).count()

        if deposits_count < 2 :
            return Response({"error": "You need to make atleast 2 deposits to view the cash desk balance."},status=status.HTTP_404_NOT_FOUND)
        
        if withdrawals_count < 2 :
            return Response({"error": "You need to make atleast 2 withdrawals to view the cash desk balance."},status=status.HTTP_404_NOT_FOUND)


        #GET DEPOSIT & WITHDRAWALS DATA FROM THE OPERATIONS
        ###BGN
        bgn_sum_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day), operation_type='deposit'
                            ).aggregate(bgn_sum_deposit = Sum('bgn_amount'))['bgn_sum_deposit'] or 0
        bgn_sum_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(bgn_sum_withdraw = Sum('bgn_amount'))['bgn_sum_withdraw'] or 0
        bgn_balance = bgn_sum_deposit - bgn_sum_withdraw

        bgn_10_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='deposit'
                            ).aggregate(bgn_10_deposit = Sum('bgn_10'))['bgn_10_deposit'] or 0
        bgn_10_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(bgn_10_withdraw = Sum('bgn_10'))['bgn_10_withdraw'] or 0
        bgn_10_balance = bgn_10_deposit - bgn_10_withdraw

        bgn_50_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='deposit'
                            ).aggregate(bgn_50_deposit = Sum('bgn_50'))['bgn_50_deposit'] or 0
        bgn_50_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(bgn_50_withdraw = Sum('bgn_50'))['bgn_50_withdraw'] or 0
        bgn_50_balance = bgn_50_deposit - bgn_50_withdraw

        ###EUR
        eur_sum_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day), operation_type='deposit'
                            ).aggregate(eur_sum_deposit = Sum('eur_amount'))['eur_sum_deposit'] or 0
        eur_sum_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(eur_sum_withdraw = Sum('eur_amount'))['eur_sum_withdraw'] or 0
        eur_balance = eur_sum_deposit - eur_sum_withdraw

        
        eur_10_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='deposit'
                            ).aggregate(eur_10_deposit = Sum('eur_10'))['eur_10_deposit'] or 0
        eur_10_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(eur_10_withdraw = Sum('eur_10'))['eur_10_withdraw'] or 0
        eur_10_balance = eur_10_deposit - eur_10_withdraw


        eur_20_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='deposit'
                            ).aggregate(eur_20_deposit = Sum('eur_20'))['eur_20_deposit'] or 0
        eur_20_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(eur_20_withdraw = Sum('eur_20'))['eur_20_withdraw'] or 0
        eur_20_balance = eur_20_deposit - eur_20_withdraw

        eur_50_deposit = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='deposit'
                            ).aggregate(eur_50_deposit = Sum('eur_50'))['eur_50_deposit'] or 0
        eur_50_withdraw = CashOperations.objects.filter(transaction_date__range=(start_of_day, end_of_day),operation_type='withdraw'
                            ).aggregate(eur_50_withdraw = Sum('eur_50'))['eur_50_withdraw'] or 0
        eur_50_balance = eur_50_deposit - eur_50_withdraw

        #GET DESK START BALANCE(SB) & DENOMINATIONS 
        cash_desk_serializer = CashDeskSerializer(cash_desk)

        bgn_sum_sb = Decimal(cash_desk_serializer.data['bgn_balance'])
        bgn_10_sb = cash_desk_serializer.data['bgn_10']
        bgn_50_sb = cash_desk_serializer.data['bgn_50']
        eur_sum_sb = Decimal(cash_desk_serializer.data['eur_balance'])
        eur_10_sb = cash_desk_serializer.data['eur_10']
        eur_20_sb = cash_desk_serializer.data['eur_20']
        eur_50_sb = cash_desk_serializer.data['eur_50']

        #TOTAL CALCULATION BETWEEN START BALANCE AND OPERATION BALANCE
        bgn_total_balance = bgn_sum_sb + bgn_balance
        bgn_10_total_balance = bgn_10_sb + bgn_10_balance
        bgn_50_total_balance = bgn_50_sb + bgn_50_balance
        eur_total_balance = eur_sum_sb + eur_balance
        eur_10_total_balance = eur_10_sb + eur_10_balance
        eur_20_total_balance = eur_20_sb + eur_20_balance
        eur_50_total_balance = eur_50_sb + eur_50_balance

        cash_desk_data.append({
                'cash_desk_id': request.data.get('cash_desk_id'),
                'bgn_amount': bgn_total_balance,
                'bgn_10': bgn_10_total_balance,
                'bgn_50': bgn_50_total_balance,
                'eur_amount': eur_total_balance,
                'eur_10': eur_10_total_balance,
                'eur_20': eur_20_total_balance,
                'eur_50': eur_50_total_balance,
                'user_id': request.data.get('user_id')
            })

        # Return the data
        return Response(cash_desk_data)