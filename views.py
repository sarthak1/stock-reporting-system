# views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .models import StockMaster, StockTransaction, DailyStockSummary
from datetime import timedelta


def record_transaction(request):
    if request.method == 'POST':
        data = request.POST
        stock = get_object_or_404(StockMaster, id=data['stock_id'])
        StockTransaction.objects.create(
            stock=stock,
            transaction_date=parse_date(data['transaction_date']),
            transaction_type=data['transaction_type'],
            quantity=data['quantity'],
            remarks=data.get('remarks', '')
        )
        return JsonResponse({'message': 'Transaction recorded successfully'})


def calculate_and_save_daily_summary(request):
    if request.method == 'POST':
        date_str = request.POST['date']
        date = parse_date(date_str)
        previous_date = date - timedelta(days=1)

        stocks = StockMaster.objects.all()

        for stock in stocks:
            previous_summary = DailyStockSummary.objects.filter(stock=stock, date=previous_date).first()
            opening_quantity = previous_summary.closing_quantity if previous_summary else stock.initial_stock

            transactions = StockTransaction.objects.filter(stock=stock, transaction_date=date)
            inbound_quantity = sum(t.quantity for t in transactions if t.transaction_type == 'INBOUND')
            outbound_quantity = sum(t.quantity for t in transactions if t.transaction_type == 'OUTBOUND')

            closing_quantity = opening_quantity + inbound_quantity - outbound_quantity

            DailyStockSummary.objects.update_or_create(
                stock=stock,
                date=date,
                defaults={
                    'opening_quantity': opening_quantity,
                    'inbound_quantity': inbound_quantity,
                    'outbound_quantity': outbound_quantity,
                    'closing_quantity': closing_quantity
                }
            )

        return JsonResponse({'message': 'Daily summary calculated and saved successfully'})

