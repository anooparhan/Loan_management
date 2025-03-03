
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    
    

    path('create-or-update-user', views.CreateOrUpdateUserApiView.as_view()),
    path('get-users', views.GetUsersApiView.as_view()),
    path('activate-or-deactivate-users', views.ActiveOrDeactivteUsersApiView.as_view()),
    path('get-user-details', views.GetUserDetailsApiView.as_view()),
    path('get-groups-for-user-creation', views.GetGroupsForUserCreationApiView.as_view()),
    
    
   

]