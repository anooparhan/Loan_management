# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_date',
        'modified_date',
        'deleted',
        'deleted_by_cascade',
        'created_by',
        'modified_by',
        'is_active',
        'loan_id',
        'amount',
        'tenure',
        'interest_rate',
        'monthly_installment',
        'total_interest',
        'total_amount',
        'amount_paid',
        'amount_remaining',
        'next_due_date',
        'status',
        'created_at',
    )
    list_filter = (
        'created_date',
        'modified_date',
        'deleted',
        'deleted_by_cascade',
        'created_by',
        'modified_by',
        'is_active',
        'next_due_date',
        'created_at',
    )
    date_hierarchy = 'created_at'
