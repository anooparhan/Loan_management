from rest_framework import serializers
from apps.user.models import Users


class LoginResponseSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = ['id','email','username','is_active', 'is_verified','is_admin','is_superuser',]
    
    def to_representation(self, instance):
        datas = super().to_representation(instance)
        for key in datas.keys():
            try:
                if datas[key] is None:
                    datas[key] = ""
            except KeyError:
                pass
        return datas
