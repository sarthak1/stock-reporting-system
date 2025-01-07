from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from .models import StockMaster, StockTransaction, DailyStockSummary
from datetime import timedelta
from django.db.models import Sum, F
import json


@csrf_exempt
def record_transaction(request):
    """
    Records a stock transaction.
    """
    if request.method == 'POST':
        try:
            # Parse and validate input data
            data = json.loads(request.body)
            stock = get_object_or_404(StockMaster, id=data.get('stock_id'))
            transaction_date = parse_date(data.get('transaction_date'))
            transaction_type = data.get('transaction_type')
            quantity = int(data.get('quantity', 0))
            remarks = data.get('remarks', '')

            if transaction_type not in ['INBOUND', 'OUTBOUND'] or quantity <= 0:
                return JsonResponse({'error': 'Invalid transaction data'}, status=400)

            # Create the transaction
            StockTransaction.objects.create(
                stock=stock,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                quantity=quantity,
                remarks=remarks
            )
            return JsonResponse({'message': 'Transaction recorded successfully'})
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid input: {e}'}, status=400)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@csrf_exempt
def calculate_and_save_daily_summary(request):
    """
    Calculates and saves the daily stock summary.
    """
    if request.method == 'POST':
        try:
            # Parse and validate input data
            data = json.loads(request.body)
            date_str = data.get('date')
            date = parse_date(date_str)
            if not date:
                return JsonResponse({'error': 'Invalid or missing date'}, status=400)

            # Get the previous day's date
            previous_date = date - timedelta(days=1)

            # Fetch stocks and aggregate transaction data
            stocks = StockMaster.objects.all()
            transactions = StockTransaction.objects.filter(transaction_date=date).values(
                'stock_id', 'transaction_type'
            ).annotate(total_quantity=Sum('quantity'))

            # Preprocess transaction data for faster lookup
            transaction_data = {}
            for t in transactions:
                stock_id = t['stock_id']
                transaction_type = t['transaction_type']
                transaction_data.setdefault(stock_id, {'INBOUND': 0, 'OUTBOUND': 0})
                transaction_data[stock_id][transaction_type] = t['total_quantity']

            # Calculate and save daily summaries
            summaries = []
            for stock in stocks:
                # Calculate opening quantity
                previous_summary = DailyStockSummary.objects.filter(stock=stock, date=previous_date).first()
                opening_quantity = previous_summary.closing_quantity if previous_summary else stock.initial_stock

                # Calculate inbound and outbound quantities
                inbound_quantity = transaction_data.get(stock.id, {}).get('INBOUND', 0)
                outbound_quantity = transaction_data.get(stock.id, {}).get('OUTBOUND', 0)

                # Calculate closing quantity
                closing_quantity = opening_quantity + inbound_quantity - outbound_quantity

                # Prepare the summary for bulk update/create
                summaries.append(DailyStockSummary(
                    stock=stock,
                    date=date,
                    opening_quantity=opening_quantity,
                    inbound_quantity=inbound_quantity,
                    outbound_quantity=outbound_quantity,
                    closing_quantity=closing_quantity
                ))

            # Use bulk operations for better performance
            DailyStockSummary.objects.filter(date=date).delete()  # Remove existing summaries for the date
            DailyStockSummary.objects.bulk_create(summaries)

            return JsonResponse({'message': 'Daily summary calculated and saved successfully'})
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid input: {e}'}, status=400)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
