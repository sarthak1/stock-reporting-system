from django.db import models

class StockMaster(models.Model):
    stock_name = models.CharField(max_length=255, unique=True)  # Unique constraint for distinct stock names
    category = models.CharField(max_length=100)
    unit_of_measure = models.CharField(max_length=50)
    initial_stock = models.PositiveIntegerField()  # Enforce non-negative values

    def __str__(self):
        return self.stock_name


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('INBOUND', 'Inbound'),
        ('OUTBOUND', 'Outbound'),
    ]

    stock = models.ForeignKey(
        StockMaster, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_date = models.DateField()
    transaction_type = models.CharField(
        max_length=8, 
        choices=TRANSACTION_TYPES
    )
    quantity = models.PositiveIntegerField()  # Enforce non-negative values
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.stock.stock_name} - {self.transaction_type} ({self.quantity})"


class DailyStockSummary(models.Model):
    stock = models.ForeignKey(
        StockMaster, 
        on_delete=models.CASCADE, 
        related_name='daily_summaries'
    )
    date = models.DateField()
    opening_quantity = models.PositiveIntegerField()  # Enforce non-negative values
    inbound_quantity = models.PositiveIntegerField()  # Enforce non-negative values
    outbound_quantity = models.PositiveIntegerField()  # Enforce non-negative values
    closing_quantity = models.PositiveIntegerField()  # Enforce non-negative values

    class Meta:
        unique_together = ('stock', 'date')  # Ensures a unique summary per stock per day

    def __str__(self):
        return f"{self.stock.stock_name} Summary for {self.date}"
