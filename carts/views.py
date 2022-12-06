import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import CartListSerializer


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
        
        serializer = CartListSerializer(carts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @query_debugger
    @login_decorator
    def post(self, request):        
        try:
            data_list = json.loads(request.body)
            user      = request.user
            
            for data in data_list:
                size_id      = data["size_id"]
                product_id   = data["product_id"]
                quantity     = data["quantity"]
                product_size = ProductSize.objects.get(product_id=product_id, size_id=size_id)

                if quantity < 1:
                    raise KeyError

                cart, created = Cart.objects.get_or_create(
                    user_id       = user.id,
                    product_size  = product_size,
                    defaults      = {"quantity": quantity}
                )

                if not created:
                    cart.quantity += quantity
                    cart.save()
                    return JsonResponse({"message" : "SUCCESS"}, status = 200)

            return JsonResponse({"message" : "SUCCESS"}, status = 201)

        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status = 400)

        except (Cart.DoesNotExist, ProductSize.DoesNotExist):
            return JsonResponse({"message" : 'INVALID_ERROR'}, status = 404)
        
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
