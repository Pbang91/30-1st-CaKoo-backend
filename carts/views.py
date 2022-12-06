import json
from typing import OrderedDict

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import CartListSerializer, CartStoreSerializer


from django.http    import JsonResponse

from users.utils     import login_decorator
from products.models import ProductSize
from .models         import Cart
from decorator       import query_debugger

permission_classes = [IsAuthenticated]

class CartView(APIView):
    @query_debugger
    @login_decorator
    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user).select_related('product_size__product', 'product_size__size')

        if len(carts) == 0:
            return Response({'detail' : 'Empty Cart'}, status=status.HTTP_200_OK)
        
        serializer = CartListSerializer(carts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @query_debugger
    @login_decorator
    def post(self, request : OrderedDict):
        try:
            # print(serializer.errors) 왜 진행이 안되는지 보기 위해서는 errors를 활용하자.
            user = request.user
            size_id = request.data.get('size_id')
            product_id = request.data.get('product_id')

            product_size = ProductSize.objects.get(product_id=product_id, size_id=size_id)

            del request.data["product_id"]
            del request.data['size_id']
            
            request.data["user"] = user.id # serialize.Modelserializer를 통해 create를 진행하기 위해서는 Pk값이 필요하다.
            request.data["product_size"] = product_size.id
            
            serializer = CartStoreSerializer(data=request.data)
            

            if serializer.is_valid(): # is_valid를 활용하기 위해서는 dictionary 형태여야 한다..
                serializer.save()

                return Response({'detail' : 'Success'}, status=status.HTTP_201_CREATED)
        
        except ProductSize.DoesNotExist:
            return Response({'detail' : 'Required Field'}, status=status.HTTP_400_BAD_REQUEST)
    
        
    @query_debugger
    @login_decorator
    def patch(self, request, cart_id):
        try:
            data     = json.loads(request.body)
            quantity = data['quantity']            
            
            cart = Cart.objects.get(id = cart_id, user = request.user)
            
            cart.quantity = quantity
            cart.save()
        
            return JsonResponse({"message" : "SUCCESS"}, status = 200)
        
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status = 400)
        
        except Cart.DoesNotExist:
            return JsonResponse({"message" : "INVALID_CART"}, status = 404)
        
    @query_debugger
    @login_decorator
    def delete(self, request, cart_id):
        try:
            cart = Cart.objects.get(id = cart_id, user = request.user)
            cart.delete()

            return JsonResponse({"message":"NO_CONTENT"}, status=204)
        
        except Cart.DoesNotExist:
            return JsonResponse({"message" : "INVALID_CART"}, status = 404)
