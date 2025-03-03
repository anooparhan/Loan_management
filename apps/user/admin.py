from django.contrib import admin
from apps.user.models import Users
from django_acl.models import Role, Group
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import GroupAdmin as AuthGroupAdmin
from django.contrib.auth.models import Group as AuthGroup







class UsersAdmin(admin.ModelAdmin):
    model = Users
    list_display = ['id', 'email','username','phone_number']
    list_display_links = ['email']
    
    fieldsets = (
        ("Profile", {'fields': ('email','username')}),
        ('Permissions', {'fields': ('is_staff','is_active','is_admin','is_superuser','is_verified','user_groups','user_permissions')}),
    )

    list_filter = (
        'date_joined',
        'last_login',
        'is_verified',
        'is_admin',
        'is_staff',
        'is_superuser',
        'is_active',
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    
admin.site.register(Users,UsersAdmin)





