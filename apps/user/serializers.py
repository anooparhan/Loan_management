from rest_framework import serializers
from django.contrib.auth.models import Permission
from django_acl.models import Group, Role
from loan_management.helpers.helper import get_object_or_none
from django.contrib.auth.hashers import make_password

from apps.user.models import Users



class PermissionListApi(serializers.Serializer):
    
    class Meta:
        model = Permission
        fields = ['id','name','codename']


class CreateOrUpdateRoleSerilizer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(required=False, queryset=Role.objects.all())
    name = serializers.CharField(max_length=255, required=True)
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())
    
    class Meta:
        model = Role
        fields = ['role','name','permissions']
        
 
    def validate(self, attrs):
        role = attrs.get('role')
        name = attrs.get('name')
        role_query_set = Role.objects.filter(name=name)
        if role is not None:
            role_query_set = role_query_set.exclude(pk=role.pk)
         
        if role_query_set.exists():
            raise serializers.ValidationError({"name": ['Sorry, that name already exists!']})   
        return super().validate(attrs)
    
        
    def create(self, validated_data):
        
        instance = Role()
        instance.name = validated_data.get('name')
        instance.save() 
        
        permissions = validated_data.get('permissions')
        if instance is not None:
            permission_instance = get_object_or_none(Role, pk=instance.pk)
            if permission_instance is not None:
                instance.permissions.clear()
                for permission in permissions:
                    permission_instance.permissions.add(permission)
            
        return instance
    
    
    def update(self, instance, validated_data):
        
        instance.name = validated_data.get('name')
        permissions = validated_data.get('permissions')
        instance.save()
        instance.permissions.clear()
        permission_instance = get_object_or_none(Role, pk=instance.pk)
        
        if permission_instance is not None:
            permission_instance.permissions.clear()
            for permission in permissions:
                permission_instance.permissions.add(permission)
        
        return instance
    

class GetRolesApiSerializers(serializers.ModelSerializer):
    
    permissions = serializers.SerializerMethodField('get_permissions')
    
    class Meta:
        model = Role
        fields = ['id','name','permissions']
        
    def get_permissions(self, obj):
        permissions = [name for name in obj.permissions.values_list('name', flat=True)]
        return permissions
    
    
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas
    

class DestroyRoleRequestSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Role.objects.all(), required=True)
    class Meta:
        model = Role
        fields = ['role']
        
        
        
class GetRolesForGroupCreationSerializers(serializers.ModelSerializer):
    
    value = serializers.IntegerField(source='pk')
    label = serializers.CharField(source='name')
    class Meta:
        model = Role
        fields = ['value','label']




        
#--------------------------------GROUPS CURD OPERATIONS --------------------------------

class CreateOrUpdateGroupSerializer(serializers.ModelSerializer):
    
    group = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Group.objects.all(), required=False)
    name = serializers.CharField(max_length=255, required=True)
    roles = serializers.PrimaryKeyRelatedField(read_only=False, many=True, queryset=Role.objects.all())
    
    class Meta:
        model = Group
        fields = ['group','name','roles']
        
 
    def validate(self, attrs):
        group = attrs.get('group')
        name = attrs.get('name')
        group_query_set = Group.objects.filter(name=name)
        if group is not None:
            group_query_set = group_query_set.exclude(pk=group.pk)
         
        if group_query_set.exists():
            raise serializers.ValidationError({"name": ['Sorry, that name already exists!']})   
        
        return super().validate(attrs)
        
        
        
    def create(self, validated_data):
        instance = Group()
        instance.name = validated_data.get('name')
        instance.save()
        
        
        roles = validated_data.pop('roles')
        
        if instance is not None:
            role_instance = get_object_or_none(Group, pk=instance.pk)
            if role_instance is not None:
                role_instance.roles.clear()
                for role in roles:
                    role_instance.roles.add(role)
            
        return instance
    
        
    def update(self, instance, validated_data):
        
        instance.name = validated_data.get('name')
        instance.save()
        
        
        roles = validated_data.pop('roles')
        
        if instance is not None:
            role_instance = get_object_or_none(Group, pk=instance.pk)
            if role_instance is not None:
                role_instance.roles.clear()
                for role in roles:
                    role_instance.roles.add(role)
            
        return instance
    
    
    
    
    
    
    
class GetGroupsApiRequestSerializers(serializers.ModelSerializer):
    
    
    roles = serializers.SerializerMethodField('get_roles')
    class Meta:
        model = Group
        fields = ['pk','name','roles']
        
        
    def get_roles(self, obj):
        # roles = ",".join(str(name) for name in obj.roles.values_list('name', flat=True))
        roles = [name for name in obj.roles.values_list('name', flat=True)]
        return roles
    
        
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas
        
class DestroyGropsRequestSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Group.objects.all())
    class Meta:
        model = Group
        fields = ['group']
        
#--------------------------------USER INTO GROUPS CURD OPERATIONS --------------------------------






class GetUsersApiSerializers(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField('get_groups')
    class Meta:
        model = Users
        fields = ['pk','username','email','is_active','is_admin','is_staff','groups']


    def get_groups(self, obj):
        groups = [name for name in obj.user_groups.values_list('name', flat=True)]
        return groups
    



class CreateOrUpdateUserSerializer(serializers.ModelSerializer):
    user            = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Users.objects.all(), required=False)
    username        = serializers.CharField(required=True)
    email           = serializers.EmailField(required=True)
    password        = serializers.CharField(required=False )
    phone_number    = serializers.IntegerField(required=False)
    is_admin        = serializers.BooleanField(default=False)
    is_staff        = serializers.BooleanField(default=False)
    # groups          = serializers.PrimaryKeyRelatedField(read_only=False, many=True, queryset=Group.objects.all(), required=True)
    

    class Meta:
        model = Users
        fields = ['user','username','email','phone_number','password','is_active','is_admin','is_staff',]
        
    
    def validate(self, attrs):
        email = attrs.get('email', '') 
        user = attrs.get('user', None)
        phone_number =  attrs.get('phone_number', None)
        if email is not None:
            user_query_set = Users.objects.filter(email=email)
            if user is not None:
                user_query_set = user_query_set.exclude(pk=user.pk)
            if user_query_set.exists():
                raise serializers.ValidationError(
                    {'email': ('email address is already in use')})
        else:
            user_query_set = Users.objects.filter(phone_number=phone_number)
            if user is not None:
                user_query_set = user_query_set.exclude(pk=user.pk)
            if user_query_set.exists():
                raise serializers.ValidationError(
                    {'Phone number': ('Phone number is already in use')})
        return super().validate(attrs)


    def create(self, validated_data):
        
        
        password = validated_data.get('password',None)
        
        instance = Users()
        instance.username = validated_data.get('username')
        instance.phone_number= validated_data.get("phone_number")
        instance.email = validated_data.get('email')
        if password != '' and password is not None:
            instance.set_password(password) 
        instance.is_active = validated_data.get('is_active')
        instance.is_admin = validated_data.get('is_admin')
        instance.is_staff = validated_data.get('is_staff')
        instance.save()
        
        
        # groups = validated_data.pop('groups')
        
        # for group_instance in groups:
        #     if group_instance is not None:
        #         group_instance.user_set.add(instance)
        
        return instance

    
    def update(self, instance, validated_data):
        
        groups = validated_data.pop('groups')
        
        active_groups = instance.user_groups.all().values_list('id',flat=True)
                
        remove_groups = [item for item in active_groups if str(item) not in groups]
        
        [groups.remove(str(item)) for item in active_groups if str(item) in groups]
        
        password = validated_data.get('password','')
 
        instance.username = validated_data.get('username')
        instance.email = validated_data.get('email')
        instance.phone_number= validated_data.get("phone_number")
        
        if password:
            instance.set_password(password) 
            
        if validated_data.get('is_active',''):
            instance.is_active = validated_data.get('is_active')
            
        if validated_data.get('is_admin',''):
            instance.is_admin = validated_data.get('is_admin')
            
        if validated_data.get('is_staff',''):
            instance.is_staff = validated_data.get('is_staff')
            

        instance.save()
        
        if instance is not None:
            for group_instance in groups:
                if group_instance is not None:
                    group_instance.user_set.add(instance)
                
        for remove_group in remove_groups:
            remove_group_instance = get_object_or_none(Group,id=remove_group)
            if remove_group_instance is not None:
                remove_group_instance.user_set.remove(instance)
        
        return instance

    
class GetUserDetailsRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Users.objects.all(), required=True)
    class Meta:
        model = Role
        fields = ['user']



class ActiveOrDeactivteUsersSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all(), help_text="This field required for only update user api call")
    class Meta:
        model = Users
        fields = ['user']

        
    def validate(self, attrs):
        return super().validate(attrs)


    def update(self, instance , validated_data):
        instance.is_active = True if not instance.is_active else False
        instance.save()
        return instance

 
class GetRoleDetailsRequestSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Role.objects.all(), required=True)
    class Meta:
        model = Role
        fields = ['role']
    

class GetGroupDetailsRequestSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Group.objects.all(), required=True)
    class Meta:
        model = Group
        fields = ['group']
    

class GetGroupsForUserCreationSerializers(serializers.ModelSerializer):
    
    value = serializers.IntegerField(source='pk')
    label = serializers.CharField(source='name')
    class Meta:
        model = Group
        fields = ['value','label']



class CreateStaffListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = ['staff','username','email','password','is_active',]



class CreateStaffSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(required=False, queryset=Users.objects.all())
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    
    class Meta:
        model = Users
        fields = ['staff','username','email','password','is_active',]
        
    def validate(self, attrs):
        staff = attrs.get('staff',None)
        if staff is not None:
            staff_query_set = Users.objects.filter(pk=staff.pk)
            staff_query_set = staff_query_set.exclude(pk=staff.pk)  
            if staff_query_set.exists():
                raise serializers.ValidationError({"staff": ['Sorry, that staff id already exists!']})
        return super().validate(attrs)  


    def update(self, instance, validated_data):
        password = validated_data.get('password')
        instance.username = validated_data.get('username')
        instance.email = validated_data.get('email')
        instance.password = make_password(password)
        instance.is_staff = True
        instance.save()    
        return instance

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')
        hash_pass = make_password(password)
        instance = Users.objects.create(username=username,email=email,password=hash_pass)
        instance.save()
        return instance



class StaffActiveOrInactiveSerializer(serializers.Serializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    class Meta:
        model = Users
        fields = ['staff']

        
    def validate(self, attrs):
        return super().validate(attrs)


    def update(self, instance , validated_data):
        instance.is_active = True if not instance.is_active else False
        instance.save()
        return instance










