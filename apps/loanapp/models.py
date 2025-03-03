from django.db import models

# Create your models here.
from django.db import models
from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import uuid
from datetime import timedelta
from loan_management.models import AbstractDateTimeFieldBaseModel

User = get_user_model()

class Loan(AbstractDateTimeFieldBaseModel):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("DEFAULTED", "Defaulted"),
    ]

    loan_id = models.CharField(max_length=255, unique=True, editable=False, default=uuid.uuid4)
  
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Loan principal amount
    tenure = models.IntegerField()  # Tenure in months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        """Calculate monthly EMI, total interest, and total payable amount before saving"""
        if not self.monthly_installment:
            self.calculate_loan_details()
        super().save(*args, **kwargs)

    def calculate_loan_details(self):
        """Calculate EMI using the formula: EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)"""
        principal = float(self.amount)
        rate = float(self.interest_rate) / 100 / 12  # Monthly interest rate
        months = int(self.tenure)

        if rate == 0:
            emi = principal / months  # No interest case
        else:
            emi = principal * rate * ((1 + rate) ** months) / (((1 + rate) ** months) - 1)

        total_interest = (emi * months) - principal
        total_amount = principal + total_interest

        self.monthly_installment = round(emi, 2)
        self.total_interest = round(total_interest, 2)
        self.total_amount = round(total_amount, 2)
        self.amount_remaining = self.total_amount
        self.next_due_date = now().date() + timedelta(days=30)

    def __str__(self):
        return f"Loan {self.loan_id} - {self.user.username} - {self.status}"
