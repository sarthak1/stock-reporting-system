# models.py
from django.db import models

class StockMaster(models.Model):
    stock_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    unit_of_measure = models.CharField(max_length=50)
    initial_stock = models.IntegerField()

    def __str__(self):
        return self.stock_name


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('INBOUND', 'Inbound'),
        ('OUTBOUND', 'Outbound'),
    ]

    stock = models.ForeignKey(StockMaster, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    remarks = models.TextField(blank=True, null=True)


class DailyStockSummary(models.Model):
    stock = models.ForeignKey(StockMaster, on_delete=models.CASCADE)
    date = models.DateField()
    opening_quantity = models.IntegerField()
    inbound_quantity = models.IntegerField()
    outbound_quantity = models.IntegerField()
    closing_quantity = models.IntegerField()

