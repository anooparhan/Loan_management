# Generated by Django 4.2.15 on 2025-03-02 06:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='user',
        ),
    ]
