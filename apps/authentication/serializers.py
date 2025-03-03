from rest_framework import serializers
from apps.user.models import Users
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    class Meta:
        model = Users
        fields = ['email','password']
        
    def validate(self, attrs):
        return super().validate(attrs)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')   




            




