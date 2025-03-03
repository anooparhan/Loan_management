from django.shortcuts import render
import sys,os
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics,status
from loan_management.helpers.pagination import RestPagination
from drf_yasg import openapi
from functools import reduce
from django.db.models import Q 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from loan_management.helpers.response import ResponseInfo
from loan_management.helpers.helper import get_object_or_none
from loan_management.helpers.custom_messages import _success,_record_not_found
from apps.loanapp.serializers import  (
    LoanSerializer,ForeClosureSerializer  )
from apps.loanapp.schema import LoanListSchema,LoanDetailSchema
from apps.loanapp.models import Loan
# Create your views here.




class CreateOrUpdateLoanAPIView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateOrUpdateLoanAPIView, self).__init__(**kwargs)

    serializer_class   = LoanSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=['Loan'])
    def post(self,request):

        try:

            loan_instance = get_object_or_none(Loan,pk=request.data.get('id',None))

            serializer = self.serializer_class(loan_instance,data=request.data,context={'request':request})
            if not serializer.is_valid():
                self.response_format['status_code']             = status.HTTP_400_BAD_REQUEST
                self.response_format['status']                  = False
                self.response_format['errors']                  = serializer.errors
                return Response(self.response_format, status    = status.HTTP_400_BAD_REQUEST)

            serializer.save()
            self.response_format['status_code']             = status.HTTP_200_OK
            self.response_format['status']                  = True
            self.response_format['message']                 = _success
            return Response(self.response_format, status    = status.HTTP_200_OK)
           
    
        except Exception as e:

            exc_type,exc_obj,exc_tb  = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    
            self.response_format['status_code']             = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status']                  = True
            self.response_format['message']                 = f' exc_type : {exc_type}, fname : {fname} , tblineno : {exc_tb.tb_lineno} , error : {str(e)}'
            return Response(self.response_format, status    = status.HTTP_500_INTERNAL_SERVER_ERROR)






class LoanListAPIView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(LoanListAPIView, self).__init__(**kwargs)

    serializer_class   = LoanListSchema
    permission_classes = (IsAuthenticated,)
    pagination_class   = RestPagination

    search        = openapi.Parameter('search',openapi.IN_QUERY,type=openapi.TYPE_STRING,required=False,description='The search Value')
    sort_by       = openapi.Parameter('sort_by',openapi.IN_QUERY,type=openapi.TYPE_STRING,required=False,description='sort_by value')
    order         = openapi.Parameter('order',openapi.IN_QUERY,type=openapi.TYPE_STRING,required=False,description='asc or desc')
  
   

    @swagger_auto_schema(tags=['Loan'],manual_parameters=[search,sort_by,order],pagination_class=RestPagination)
    def get(self,request):

        try:
            search_value        = request.GET.get('search',None)
            sort_by             = request.GET.get('sort_by','id')
            order               = request.GET.get('order','asc')
         
          
            filter_query_set    = []

            if search_value not in ['',None]:
                filter_query_set.append(Q(tenure__istartswith=search_value) | Q(loan_id__icontains=search_value) )



           

                 
        

            valid_sort_fields = ['tenure','loan_id']
            if sort_by not in valid_sort_fields:
                sort_by = 'id'

            if order == "desc":
                sort_by = f"-{sort_by}"

            combine_filter = reduce(lambda x, y : x & y, filter_query_set, Q())    

            query_set=Loan.objects.filter(combine_filter).order_by(sort_by)
            page = self.paginate_queryset(query_set)
            serializer = self.serializer_class(page,many=True,context={'request':request})
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            exc_type,exc_obj,exc_tb  = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code']  = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status']       =  False
            self.response_format['message']      = f"exc_type : {exc_type}, fname : {fname}, tb_lineno : {exc_tb.tb_lineno}, error : {str(e)}"
            return Response(self.response_format,status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LoanDetailsAPIView(generics.GenericAPIView):

    def __init__(self,**kwargs):
        self.response_format = ResponseInfo().response
        super(LoanDetailsAPIView,self).__init__(**kwargs)

    serializer_class   = LoanDetailSchema
    permission_classes = (IsAuthenticated,)

    id = openapi.Parameter('id',openapi.IN_QUERY,type=openapi.TYPE_STRING,required=True,description="The Id")
    @swagger_auto_schema(tags=['Loan'],manual_parameters=[id])
    def get(self,request):

        try:

            loan_instance = get_object_or_none(Loan,pk=request.GET.get('id',None))
            if loan_instance is None:
                self.response_format['status_code']  = status.HTTP_204_NO_CONTENT
                self.response_format['status']       = False
                self.response_format['message']      = _record_not_found
                return Response(self.response_format,status=status.HTTP_200_OK)

            serializer=self.serializer_class(loan_instance,context={'request':request})
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format['status']      = True
            self.response_format['message']     = _success
            self.response_format['data']        = serializer.data
            return Response(self.response_format,status=status.HTTP_200_OK)

        except Exception as e:
            exc_type,exc_obj,exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status']      = False
            self.response_format['message']     = f" exc_type : {exc_type} , fname : {fname}, tblineno : {exc_tb.tb_lineno}, error :{str(e)}"
            return Response(self.response_format,status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LoanDelete(generics.DestroyAPIView):
    def __init__(self, **kwargs):
        self.response_format = {
            "status": False,
            "status_code": 500,
            "message": "",
            "data": {},
            "errors": {}
        }
        super(LoanDelete, self).__init__(**kwargs)

    serializer_class = ForeClosureSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Loan"], request_body=serializer_class)
    def delete(self, request, *args, **kwargs):
        try:
            # Validate request data
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
                self.response_format["status"] = False
                self.response_format["errors"] = serializer.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            loan_id = serializer.validated_data.get('id')

            # Fetch the loan
            loan = Loan.objects.filter(id=loan_id).first()
            if not loan:
                self.response_format["status_code"] = status.HTTP_404_NOT_FOUND
                self.response_format["status"] = False
                self.response_format["message"] = "Loan not found."
                return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)

            # **Foreclosure Calculation**
            remaining_tenure = loan.tenure - (loan.amount_paid // loan.monthly_installment)
            foreclosure_discount = round(loan.total_interest * Decimal('0.05'), 2)  # Convert to Decimal
            final_settlement_amount = round(loan.amount_remaining - Decimal(foreclosure_discount), 2)

            # Update Loan Status
            loan.status = "CLOSED"
            loan.amount_paid = loan.total_amount  # Assume full settlement
            loan.amount_remaining = 0
            loan.save()

            # **Response Data**
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["status"] = True
            self.response_format["message"] = "Loan foreclosed successfully."
            self.response_format["data"] = {
                "loan_id": loan.loan_id,
                "amount_paid": float(loan.amount_paid),
                "foreclosure_discount": foreclosure_discount,
                "final_settlement_amount": final_settlement_amount,
                "status": loan.status
            }
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format["status_code"] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format["status"] = False
            self.response_format["message"] = f"exc_type: {exc_type}, fname: {fname}, tb_lineno: {exc_tb.tb_lineno}, error: {str(e)}"
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
