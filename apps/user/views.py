import logging
from rest_framework.response import Response
from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from apps.user.schemas import GetGroupDetailsApiSchema,  GetRolesDetailsApiSchema, GetUsersDetailsApiSchema, PermissionsResponceSchema
from apps.user.serializers import CreateStaffListSerializer, GetRolesForGroupCreationSerializers, CreateStaffSerializer, GetGroupDetailsRequestSerializer, GetGroupsForUserCreationSerializers, GetRoleDetailsRequestSerializer, GetUserDetailsRequestSerializer, PermissionListApi, CreateOrUpdateRoleSerilizer, GetRolesApiSerializers, DestroyRoleRequestSerializer, CreateOrUpdateGroupSerializer, GetGroupsApiRequestSerializers, DestroyGropsRequestSerializer, CreateOrUpdateUserSerializer, ActiveOrDeactivteUsersSerializer, GetUsersApiSerializers, StaffActiveOrInactiveSerializer
from apps.user.models import Group, Users
from django_acl.models import Role
from loan_management.helpers.response import ResponseInfo
from loan_management.helpers.custom_messages import _record_not_found, _success
from django.contrib.auth.models import Permission
from rest_framework.permissions import IsAuthenticated
from loan_management.helpers.pagination import RestPagination
from drf_yasg import openapi
from django_acl.utils.helper import get_object_or_none
from django.contrib.auth import get_user_model
from django_acl.models import Role
from rest_framework import filters
from django.db.models import Q
from loan_management.helpers.helper import get_token_user_or_none


logger = logging.getLogger(__name__)


# ----------------- Permission Listing Api------------------------------------------#
class GetPermissionsApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetPermissionsApiView, self).__init__(**kwargs)

    serializer_class = PermissionListApi
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Permission"])
    def get(self, request):

        try:

            permissions = Permission.objects.order_by(
                'label').distinct('label')
            serializer = PermissionsResponceSchema(
                permissions, many=True, context={"request": request})
            user_instance = get_object_or_none(Users, pk=request.user.pk)

            user_groups_field = get_user_model()._meta.get_field("user_groups")
            user_groups_query = "group__%s" % user_groups_field.related_query_name()

            roles = Role.objects.filter(**{user_groups_query: user_instance})

            active_permissions = set()
            for role in roles:
                role_permissions = role.permissions.all()
                for role_permission in role_permissions:
                    active_permissions.add(role_permission.pk)

            self.response_format['status_code'] = status.HTTP_200_OK
            data = {'permissions': serializer.data,
                    'active_permissions': active_permissions}
            self.response_format["data"] = data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------------------- End of Permission Listing Api------------------------------------------#
# --------------------------------ROLES CURD OPERATIONS START --------------------------------#


class CreateOrUpdateRoleApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateRoleApiView, self).__init__(**kwargs)

    serializer_class = CreateOrUpdateRoleSerilizer

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Roles"])
    def post(self, request):
        try:

            role = request.data.get('role', None)
            if role is not None and role:
                role = get_object_or_none(Role, pk=role)
                if role is None:
                    self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                    self.response_format["message"] = _record_not_found
                    self.response_format["status"] = False
                    return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)

                serializer = self.serializer_class(
                    role, data=request.data, context={'request': request})
            else:
                serializer = self.serializer_class(
                    data=request.data, context={'request': request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetRolesApiView(generics.ListAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetRolesApiView, self).__init__(**kwargs)

    queryset = Role.objects.all()
    serializer_class = GetRolesApiSerializers
    permission_classes = (IsAuthenticated,)
    pagination_class = RestPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name',]

    @swagger_auto_schema(pagination_class=RestPagination, tags=["Roles"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class DestroyRoleApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(DestroyRoleApiView, self).__init__(**kwargs)

    serializer_class = DestroyRoleRequestSerializer
    permission_classes = (IsAuthenticated,)
    role = openapi.Schema('Destroy role record', in_=openapi.IN_BODY, required=['role'], properties={
                          'role': openapi.Schema(type=openapi.TYPE_INTEGER)}, type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(tags=["Roles"], request_body=role)
    def delete(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():

                role = serializer.validated_data.get('role', None)
                role.delete()

                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format["message"] = _success
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetRoleDetailsApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetRoleDetailsApiView, self).__init__(**kwargs)

    serializer_class = GetRoleDetailsRequestSerializer
    permission_classes = (IsAuthenticated,)
    role = openapi.Parameter('role', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                             required=True, description="Enter role id")

    @swagger_auto_schema(tags=["Roles"], manual_parameters=[role])
    def get(self, request):

        try:
            serializer = self.serializer_class(data=request.GET)

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            role = serializer.validated_data.get('role', None)
            if role is None:
                self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            data = {'role': GetRolesDetailsApiSchema(
                role, context={'request': request}).data}

            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["data"] = data
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------- ROLES CURD OPERATIONS END --------------------------------

# -------------------------------- GROUPS CURD OPERATIONS START --------------------------------

class CreateOrUpdateGroupApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateGroupApiView, self).__init__(**kwargs)

    serializer_class = CreateOrUpdateGroupSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Groups"])
    def post(self, request):
        try:
            group = request.data.get('group', None)
            if group is not None and group:
                group_instance = get_object_or_none(Group, pk=group)
                if group_instance is not None:
                    serializer = self.serializer_class(
                        group_instance, data=request.data, context={'request': request})
                else:
                    self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                    self.response_format["message"] = _record_not_found
                    self.response_format["status"] = False
                    return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
            else:
                serializer = self.serializer_class(
                    data=request.data, context={'request': request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetGroupsApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetGroupsApiView, self).__init__(**kwargs)

    queryset = Group.objects.all()
    serializer_class = GetGroupsApiRequestSerializers
    permission_classes = (IsAuthenticated,)
    pagination_class = RestPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name',]

    @swagger_auto_schema(pagination_class=RestPagination, tags=["Groups"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class GetRolesForGroupCreationApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetRolesForGroupCreationApiView, self).__init__(**kwargs)

    serializer_class = GetRolesForGroupCreationSerializers

    @swagger_auto_schema(tags=["Groups"])
    def get(self, request):
        try:
            roles = Role.objects.all()
            serializer = self.serializer_class(
                roles, many=True, context={"request": request})
            self.response_format['status_code'] = status.HTTP_200_OK
            data = {'roles': serializer.data}
            self.response_format["data"] = data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DestroyGroupsApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(DestroyGroupsApiView, self).__init__(**kwargs)

    serializer_class = DestroyGropsRequestSerializer
    permission_classes = (IsAuthenticated,)

    group = openapi.Schema('Destroy group record', in_=openapi.IN_BODY, required=['group'], properties={
                           'group': openapi.Schema(type=openapi.TYPE_INTEGER)}, type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(tags=["Groups"], request_body=group)
    def delete(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():

                group = serializer.validated_data.get('group', None)
                group.delete()

                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format["message"] = _success
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

            else:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetGroupDetailsApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetGroupDetailsApiView, self).__init__(**kwargs)

    serializer_class = GetGroupDetailsRequestSerializer
    permission_classes = (IsAuthenticated,)
    group = openapi.Parameter('group', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              required=True, description="Enter group id")

    @swagger_auto_schema(tags=["Groups"], manual_parameters=[group])
    def get(self, request):

        try:
            serializer = self.serializer_class(data=request.GET)
            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            group = serializer.validated_data.get('group', None)
            if group is None:
                self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            data = {'group': GetGroupDetailsApiSchema(
                group, context={'request': request}).data}

            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["data"] = data
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------------------- GROUPS CURD OPERATIONS END --------------------------------

# -------------------------------- User management --------------------------------


class CreateOrUpdateUserApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateUserApiView, self).__init__(**kwargs)

    serializer_class = CreateOrUpdateUserSerializer
    # permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Users"])
    def post(self, request):
        try:
            user = request.data.get('user', None)
            if user is not None:
                user_instance = get_object_or_none(Users, pk=user)
                if user_instance is None:

                    self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                    self.response_format["message"] = _record_not_found
                    self.response_format["status"] = False
                    return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)

                serializer = self.serializer_class(
                    user_instance, data=request.data, context={'request': request})
            else:
                serializer = self.serializer_class(
                    data=request.data, context={'request': request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActiveOrDeactivteUsersApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ActiveOrDeactivteUsersApiView, self).__init__(**kwargs)

    serializer_class = ActiveOrDeactivteUsersSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Users"])
    def put(self, request):

        try:

            user = request.data.get('user', None)
            user_serializer = self.serializer_class(data=request.data)
            if not user_serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = user_serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            user = user_serializer.validated_data.get('user')
            serializer = self.serializer_class(
                user, data=request.data, context={'request': request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUsersApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetUsersApiView, self).__init__(**kwargs)

    queryset = Users.objects.all().exclude(Q(is_superuser=1))
    serializer_class = GetUsersApiSerializers
    permission_classes = (IsAuthenticated,)
    pagination_class = RestPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email',]

    @swagger_auto_schema(pagination_class=RestPagination, tags=["Users"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class GetUserDetailsApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetUserDetailsApiView, self).__init__(**kwargs)

    serializer_class = GetUserDetailsRequestSerializer
    user = openapi.Parameter('user', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                             required=True, description="Enter user id")

    @swagger_auto_schema(tags=["Users"], manual_parameters=[user])
    def get(self, request):

        try:
            serializer = self.serializer_class(data=request.GET)

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.validated_data.get('user', None)

            if user is None:
                self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            data = {'user': GetUsersDetailsApiSchema(
                user, context={'request': request}).data}

            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["data"] = data
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetGroupsForUserCreationApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetGroupsForUserCreationApiView, self).__init__(**kwargs)

    serializer_class = GetGroupsForUserCreationSerializers

    @swagger_auto_schema(tags=["Users"])
    def get(self, request):
        try:
            groups = Group.objects.all()
            serializer = self.serializer_class(
                groups, many=True, context={"request": request})
            self.response_format['status_code'] = status.HTTP_200_OK
            data = {'groups': serializer.data}
            self.response_format["data"] = data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateStaffApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateStaffApiView, self).__init__(**kwargs)

    serializer_class = CreateStaffSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Users"])
    def post(self, request):

        try:
            staff = request.data.get('staff', None)

            if staff is not None and staff:
                staff = Users.objects.get(pk=staff)
                serializer = self.serializer_class(
                    staff, data=request.data, context={'request': request})
            else:

                serializer = self.serializer_class(
                    data=request.data, context={'request': request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Users.DoesNotExist:
            self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
            self.response_format["message"] = _record_not_found
            self.response_format["status"] = False
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StaffActiveOrInactiveApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(StaffActiveOrInactiveApiView, self).__init__(**kwargs)

    serializer_class = StaffActiveOrInactiveSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Users"])
    def post(self, request):

        try:

            staff = request.data.get('staff', None)
            if staff is not None and staff:
                staffs = Users.objects.get(pk=staff)
                serializer = self.serializer_class(
                    staffs, data=request.data, context={'request': request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Users.DoesNotExist:
            self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
            self.response_format["message"] = _record_not_found
            self.response_format["status"] = False
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StaffApiListingApiView(generics.ListAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(StaffApiListingApiView, self).__init__(**kwargs)

    serializer_class = CreateStaffListSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Users.objects.all()
    pagination_class = RestPagination

    @swagger_auto_schema(pagination_class=RestPagination, tags=["Users"])
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)
