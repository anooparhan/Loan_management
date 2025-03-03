# Generated by Django 4.2.15 on 2025-03-02 05:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.CharField(default=uuid.uuid4, editable=False, max_length=20, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tenure', models.IntegerField()),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('monthly_installment', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_interest', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount_remaining', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('next_due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('DEFAULTED', 'Defaulted')], default='PENDING', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
