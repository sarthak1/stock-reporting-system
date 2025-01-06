# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('record-transaction/', views.record_transaction, name='record_transaction'),
    path('calculate-daily-summary/', views.calculate_and_save_daily_summary, name='calculate_daily_summary'),
]

