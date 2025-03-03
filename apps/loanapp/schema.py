from rest_framework import serializers
from apps.loanapp.models import Loan
from apps.user.models import Users
from loan_management.services.pdf_storage import PDFStorageService
from datetime import timedelta
from django.utils.timezone import now


from datetime import datetime

from django.db.models import Q 

class LoanListSchema(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
              'id',
              'loan_id',
            # 'user',
            'amount',
            'interest_rate',
            'tenure',
            'monthly_installment',
            'status',
            'amount_paid',
            'amount_remaining',
            'next_due_date',
            'created_by',
            'created_at',
            'amount_paid', 'amount_remaining', 'next_due_date', 'created_at'
        ]
      
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in data.keys():
            try:
                if data[field] is None:
                    data[field] = ""
            except KeyError:
                pass
        return data




from datetime import timedelta
from django.utils.timezone import now
from rest_framework import serializers
from decimal import Decimal
from .models import Loan  # Import your Loan model

class LoanDetailSchema(serializers.ModelSerializer):
    installments = serializers.SerializerMethodField()  
    total_interest = serializers.SerializerMethodField()  # ✅ New Field Added

    class Meta:
        model = Loan
        fields = [
            'id',
            'loan_id',
            
            'amount',
            'interest_rate',
            'tenure',
            'monthly_installment',
            'status',
            'amount_paid',
            'amount_remaining',
            'total_interest',
            'next_due_date',
            'create_by',
            'created_at',
            'installments',
            
        ]

    def get_installments(self, instance):
        """Generate installment details"""
        installments = []
        due_date = instance.next_due_date or now().date()

        for i in range(1, instance.tenure + 1):
            installments.append({
                "installment_no": i,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "amount": float(instance.monthly_installment) if instance.monthly_installment else 0.0
            })
            due_date += timedelta(days=30)  # Assuming monthly intervals

        return installments

    def get_total_interest(self, instance):
        """Calculate total interest payable"""
        if instance.amount and instance.interest_rate and instance.tenure:
            principal = Decimal(instance.amount)
            rate = Decimal(instance.interest_rate) / 100
            time = Decimal(instance.tenure) / 12  # Convert months to years
            total_interest = principal * rate * time  # Simple Interest Formula
            return round(total_interest, 2)
        return 0.0

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in data.keys():
            if data[field] is None:
                data[field] = ""
        return data
    