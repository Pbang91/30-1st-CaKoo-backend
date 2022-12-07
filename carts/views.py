from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from decorator import query_debugger
from users.utils import login_decorator
from products.models import ProductSize

from .models import Cart
from .swagger import CartSwaager
from .serializers import CartListSerializer, CartStoreSerializer, CartSchema

permission_classes = [IsAuthenticated]

class CartListView(APIView):
    @swagger_auto_schema(responses={200: CartListSerializer, 204: "No content"}, tags=["Cart"], operation_summary="Get Cart List")
    @query_debugger
    @login_decorator
    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user).select_related('product_size__product', 'product_size__size')

        if len(carts) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = CartListSerializer(carts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CartSchema, responses={200: CartListSerializer, 201: CartListSerializer, 400: 'Invalid Field'}, tags=["Cart"], operation_summary="Put In Cart")
    @query_debugger
    @login_decorator
    def post(self, request):
        try:
            # print(serializer.errors) 왜 진행이 안되는지 보기 위해서는 errors를 활용하자.
            user = request.user
            size_id = request.data.get('size_id')
            product_id = request.data.get('product_id')

            product_size = ProductSize.objects.get(product_id=product_id, size_id=size_id)
            
            del request.data["product_id"]
            del request.data['size_id']

            db_cart = Cart.objects.filter(user=user, product_size=product_size)
            
            if len(db_cart):
                serializer = CartStoreSerializer(db_cart, data=request.data, partial=True) # partial 부분적인 업데이트를 가능하게 해준다.

                if serializer.is_valid():
                    return Response({'detail' : 'Success'}, status=status.HTTP_200_OK)    

            request.data["user"] = user.id # serialize.Modelserializer를 통해 create를 진행하기 위해서는 Pk값이 필요하다.
            request.data["product_size"] = product_size.id
            
            serializer = CartStoreSerializer(data=request.data)
            

            if serializer.is_valid(): # is_valid를 활용하기 위해서는 data가 dictionary 형태여야 한다..
                serializer.save()

                return Response({'detail' : 'Success'}, status=status.HTTP_201_CREATED)
        
        except ProductSize.DoesNotExist:
            return Response({'detail' : 'Invalid Field'}, status=status.HTTP_400_BAD_REQUEST)
    

class CartDetailView(APIView):
    @swagger_auto_schema(manual_parameters=[CartSwaager.cart_id], responses={200: CartListSerializer, 404: 'Invalid Field'}, tags=["Cart"], operation_summary="Update Cart")
    @query_debugger
    @login_decorator
    def patch(self, request, cart_id):
        try:
            user = request.user
            cart = Cart.objects.get(id = cart_id, user = user)

            serializer = CartStoreSerializer(cart, data=request.data, partial=True)
            
            if serializer.is_valid():
                return Response({"detail" : "Success"}, status=status.HTTP_200_OK)
        
        except KeyError:
            return JsonResponse({"detail" : "key Error"}, status = 400)
        
        except Cart.DoesNotExist:
            return JsonResponse({"detail" : "Invalid Field"}, status = 404)
    
    @swagger_auto_schema(manual_parameters=[CartSwaager.cart_id], responses={200: CartListSerializer, 404: 'Invalid Field'}, tags=["Cart"], operation_summary="Delete Cart")
    @query_debugger
    @login_decorator
    def delete(self, request, cart_id):
        try:
            cart = Cart.objects.get(id = cart_id, user = request.user)
            
            cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Cart.DoesNotExist:
            return JsonResponse({"detail" : "Invalid Field"}, status = 404)