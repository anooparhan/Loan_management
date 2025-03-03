from uuid import uuid4
from rest_framework import serializers
from django.contrib.auth.models import Permission
from apps.user.models import  Users
from django_acl.models import Group, Role




class GetPermissionsSerializer(serializers.ModelSerializer):
    
    value    =  serializers.IntegerField(source='pk')
    label    =  serializers.CharField(source='codename')
    class Meta:
        model  = Permission
        fields = ['value','label']

    
class PermissionSerializer(serializers.ModelSerializer):
    
    
    children = serializers.SerializerMethodField('get_children')
    value    =  serializers.SerializerMethodField('get_label')
    label    =  serializers.CharField(source='sub_label')
    class Meta:
        model  = Permission
        fields = ['label','value', 'children']
        
        
    def get_children(self, obj):
        permissions = Permission.objects.filter(label=obj.label).filter(sub_label=obj.sub_label)
        permission_serializer = GetPermissionsSerializer(permissions, many=True)
        return permission_serializer.data
    
    
    def get_label(self, obj):
        return "{}".format(uuid4())
        

class PermissionsResponceSchema(serializers.ModelSerializer):
    
    
    children = serializers.SerializerMethodField('get_children')
    value    =  serializers.CharField(source='label')
    class Meta:
        model  = Permission
        fields = ['label','value', 'children']
        
    
    def get_children(self, obj):
        permissions = Permission.objects.filter(label=obj.label).order_by('sub_label').distinct('sub_label')
        permission_serializer = PermissionSerializer(permissions, many=True)
        return permission_serializer.data
    
    

        
class RolesListResponceSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Role
        fields = ['id','name','permissions']
    
    def to_representation(self, instance):
        fields = ['id','name','permissions']
        data = super().to_representation(instance)
        for field in fields:
            try:
                if data[field] is None:
                    data[field] = ""
            except KeyError:
                pass
        return data  


class GroupsListResponceSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = ['id','name','roles']
        
    def to_representation(self, instance):
        fields = ['id','name','roles']
        data = super().to_representation(instance)
        for field in fields:
            try:
                if data[field] is None:
                    data[field] = ""
            except KeyError:
                pass
        return data    






class GetUserGroupsSerializer(serializers.ModelSerializer):
    
    value    =  serializers.IntegerField(source='pk')
    label    =  serializers.CharField(source='name')
    class Meta:
        model  = Permission
        fields = ['value','label']


class GetUsersDetailsApiSchema(serializers.ModelSerializer):
    
    user_groups = serializers.SerializerMethodField('get_user_groups')
    class Meta:
        model = Users
        fields = ['pk','username','email','is_active','is_admin','is_staff','is_customer','is_counsellor','user_groups']
        
        
    def get_user_groups(self,obj):
        return GetUserGroupsSerializer(obj.user_groups.all(),many=True).data
        

class StaffListResponceSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = ['username','email','password']




class GetRolesDetailsApiSchema(serializers.ModelSerializer):
    # permissions=GetPermissionsSerializer(many=True)
    class Meta:
        model = Role
        fields = ['id','name','permissions']
        

class GetGroupRolesOptionSerializer(serializers.ModelSerializer):
    
    value    =  serializers.IntegerField(source='pk')
    label    =  serializers.CharField(source='name')
    class Meta:
        model  = Permission
        fields = ['value','label']


class GetGroupDetailsApiSchema(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField('get_role')
    
    class Meta:
        model = Group
        fields = ['id','name','roles']
        

    def get_role(self, obj):
        return GetGroupRolesOptionSerializer(obj.roles.all(),many=True).data

















class GetClientsDropdownApiResposceSchemas(serializers.ModelSerializer):
    value = serializers.IntegerField(source='pk')
    label = serializers.CharField(source='username')
    class Meta:
        model = Users
        fields = ['value','label']
    
    def to_representation(self, instance):

        fields = ['value','label']
        data = super().to_representation(instance)
        for field in fields:
            try:
                if data[field] is None:
                    data[field] = ""
            except KeyError:
                pass
        return data  