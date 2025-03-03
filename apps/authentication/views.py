from datetime import date, datetime
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from apps.authentication.schemas import LoginResponseSchema
from apps.authentication.serializers import   LoginSerializer,LogoutSerializer
from drf_yasg.utils import swagger_auto_schema
from apps.user.models import Users
from loan_management.helpers.response import ResponseInfo
from django.contrib import auth
from loan_management.helpers.custom_messages import  _account_tem_suspended, _invalid_credentials, _422
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated 



class LoginAPIView(GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(LoginAPIView, self).__init__(**kwargs)

    serializer_class = LoginSerializer

    @swagger_auto_schema(tags=["Authorization"])
    def post(self, request):
        try:

            
            serializer = self.serializer_class(data=request.data)
            
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            
            user = auth.authenticate(username=serializer.validated_data.get('email',''), password=serializer.validated_data.get('password',''))
            
            if user:
                serializer = LoginResponseSchema(user, context={"request": request})
                if not user.is_active:
                    data = {'user': {}, 'token': '', 'refresh': ''}
                    self.response_format['status_code'] = status.HTTP_202_ACCEPTED
                    self.response_format["data"] = data
                    self.response_format["status"] = False
                    self.response_format["message"] = _account_tem_suspended
                    return Response(self.response_format, status=status.HTTP_200_OK)
                else:
                    
                    
                    refresh = RefreshToken.for_user(user)
                    data = {'user': serializer.data, 'token': str(
                        refresh.access_token), 'refresh': str(refresh)}
                    self.response_format['status_code'] = status.HTTP_200_OK
                    self.response_format["data"] = data
                    self.response_format["status"] = True

                    return Response(self.response_format, status=status.HTTP_200_OK)
                
            else:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["message"] = _invalid_credentials
                self.response_format["status"] = False
                return Response(self.response_format, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class LogoutAPIView(GenericAPIView):

    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(LogoutAPIView, self).__init__(**kwargs)

    @swagger_auto_schema(tags=["Authorization"])
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            self.response_format['status'] = True
            self.response_format['status_code'] = status.HTTP_200_OK
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    
        
