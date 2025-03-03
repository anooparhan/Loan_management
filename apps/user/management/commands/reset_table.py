from django.core.management.base import BaseCommand
from django.core.management import call_command

from apps.user.models import Users

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        
        call_command('migrate','authentication','zero')
        
        call_command('migrate','organization','zero')
        call_command('migrate','encounter','zero')
        call_command('migrate','payment','zero')
        
        
        Users.objects.all().delete()
        