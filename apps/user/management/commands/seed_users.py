from django.core.management.base import BaseCommand
from django.db.models import Q
from henpec.helpers.helper import get_object_or_none
from apps.user.models import Users
import uuid
from faker import Faker



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        fake = Faker()
        for i in range(1,100):
            instance = Users()
            instance.email       = fake.email()
            instance.username    = fake.name()
            instance.set_password('aaa')
            instance.is_verified = True
            instance.is_admin    = False
            instance.is_staff    = False
            instance.is_active   = True
            instance.save()