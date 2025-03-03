from rest_framework import serializers
from apps.loanapp.models import Loan
from apps.user.models import Users
from decimal import Decimal
from django.db.models import Max

from loan_management.helpers.helper import get_object_or_none, get_token_user_or_none
from loan_management.services.pdf_storage import PDFStorageService
from datetime import datetime


import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from rest_framework import serializers
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    id                  = serializers.PrimaryKeyRelatedField(queryset=Loan.objects.all(), required=False)
    amount              = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    interest_rate       = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    tenure              = serializers.IntegerField(required=True)
    monthly_installment = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    status              = serializers.ChoiceField(choices=["PENDING", "ACTIVE", "COMPLETED", "DEFAULTED"], required=False)

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
            'next_due_date',
            'created_at',
        ]
        read_only_fields = ['amount_paid', 'amount_remaining', 'next_due_date', 'created_at']

    # Individual field validations
    def validate_amount(self, value):
        if not isinstance(value, (int, float, Decimal)):
            raise serializers.ValidationError("Amount must be a valid number.")
        if value < 1000 or value > 100000:
            raise serializers.ValidationError("Loan amount must be between ₹1,000 and ₹100,000.")
        return value

    def validate_interest_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Interest rate must be between 0 and 100.")
        return value

    def validate_tenure(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Tenure must be a whole number.")
        if value < 3 or value > 24:
            raise serializers.ValidationError("Tenure must be between 3 and 24 months.")
        return value

    def create(self, validated_data):
        request = self.context.get('request', None)
        user_instance = get_token_user_or_none(request)
        
        last_loan = Loan.objects.aggregate(Max('loan_id'))['loan_id__max']
        if last_loan:
            try:
                last_number = int(last_loan[4:])  # Extract numeric part
                new_number = last_number + 1
            except ValueError:
                new_number = 1  # Fallback for invalid data
        else:
            new_number = 1

        new_loan_id = f"LOAN{new_number:03d}"  # Format as LOAN001, LOAN002, etc.

        # Create new Loan instance
        instance = Loan(
            loan_id=new_loan_id,
            amount=validated_data.get('amount'),
            interest_rate=validated_data.get('interest_rate'),
            tenure=validated_data.get('tenure'),
            monthly_installment=validated_data.get('monthly_installment'),
            status=validated_data.get('status', 'PENDING'),
            created_by=user_instance,
            modified_by=user_instance
        )

        instance.calculate_loan_details()  # Calculate EMI before saving
        instance.save()
        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        user_instance = get_token_user_or_none(request)

        instance.amount = validated_data.get('amount', instance.amount)
        instance.interest_rate = validated_data.get('interest_rate', instance.interest_rate)
        instance.tenure = validated_data.get('tenure', instance.tenure)
        instance.status = validated_data.get('status', instance.status)
        instance.modified_by = user_instance  # Ensure modified_by is set

        if 'amount' in validated_data or 'interest_rate' in validated_data or 'tenure' in validated_data:
            instance.calculate_loan_details()  # Recalculate if key loan details change

        instance.save()
        return instance


class ForeClosureSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True) #[1,2,3]

    class Meta: 
        model   = Loan
        fields  = ['id']


