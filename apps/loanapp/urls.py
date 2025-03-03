from django.urls import path, include, re_path
from apps.loanapp.views import LoanListAPIView,CreateOrUpdateLoanAPIView,LoanDetailsAPIView, LoanDelete

urlpatterns = [
   
  path("create-or-update-employee", CreateOrUpdateLoanAPIView.as_view()),
  path("loan-list", LoanListAPIView.as_view()),
  path("loan-detail", LoanDetailsAPIView.as_view()),
   path("loan-foreclosure",  LoanDelete.as_view()),
]
