from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db.models import Q
from django.contrib.auth import get_user_model
from django_acl.models import Role, Group
from django.contrib.auth.models import Permission
from henpec.helpers.helper import get_object_or_none

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        
        Group.objects.all().delete()
        Role.objects.all().delete()
        
        call_command('loaddata', 'initial-data.json')
        
        
        roles = ['Administrator','Owner','Primary Owner','Editor','Viewer']
        
        for role in roles:
            role_instance = Role()
            role_instance.name = role
            role_instance.save()
            
            permissions_data = Permission.objects.order_by('?').all()[:2]
            role_instance = get_object_or_none(Role,id=role_instance.pk)
            for permission in permissions_data:
                role_instance.permissions.add(permission)
                
        groups = ['Manager','CTO','Project Lead']
        for group in groups:
            group_instance = Group()
            group_instance.name = group
            group_instance.save()
            
            role_data = Role.objects.order_by('?').all()[:2]
        
            group_instance = get_object_or_none(Group,id=group_instance.pk)
            for role_item in role_data:
                group_instance.roles.add(role_item)
        