from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_yasg.utils import swagger_auto_schema

from decorator import query_debugger

from .serializers import UserSignUpSerializer, UserLoginSerializer

permission_classes = [AllowAny]

class SignUp(APIView):
    @swagger_auto_schema(request_body=UserSignUpSerializer, responses={201: UserSignUpSerializer, 400: "Invalid Information"}, tags=["User"], operation_summary="Sign up", operation_description="Need email, password, phone_number, birthdate")
    @query_debugger
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LogIn(APIView):
    @swagger_auto_schema(request_body=UserLoginSerializer, responses={200: UserLoginSerializer, 400: "Invalid User"}, tags=["User"], operation_summary="Login", operation_description="Need email, password")
    @query_debugger
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)