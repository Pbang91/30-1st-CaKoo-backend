import json, uuid

from enum          import Enum

from django.http   import JsonResponse
from django.db     import transaction

from users.utils   import login_decorator
from orders.models import Order, OrderItem, OrderStatus
from carts.models  import Cart

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from decorator import query_debugger

from .serializer import OrderSerializer, OrderItemSerializer

class OrderStatusEnum(Enum):
    CONFIRMED = 1  
    CANCELED  = 2
    PENDING   = 3

class OrderView(APIView):
    @query_debugger
    @login_decorator
    def get(self, request):
        try:
            orders = Order.objects.filter(user_id = request.user).select_related('user')
            
            serializer = OrderSerializer(orders, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Order.DoesNotExist:
            return Response({"detail" : "Invalid User"}, status=status.HTTP_400_BAD_REQUEST)

    @query_debugger
    @login_decorator
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            
            cart_ids     = data["cart_ids"]
            carts        = Cart.objects.filter(user=user, id__in=cart_ids)
            order_status = OrderStatus.objects.get(id=OrderStatusEnum.CONFIRMED.value)
        
            request.data['user'] = user
            request.data['sender_name'] = user.name
            request.data['order_number'] = str(uuid.uuid4())
            request.data['order_status'] = order_status
            
            with transaction.atomic():                
                order_serializer = OrderSerializer(data=request.data)
                
                if order_serializer.is_valid():
                    print(order_serializer.data['id'])
                    order_items = [
                        OrderItem(
                            order        = order_serializer,
                            product_size = cart.product_size,
                            quantity     = cart.quantity
                        ) for cart in carts
                    ]
                
                # OrderItem.objects.bulk_create(order_items) 

                    order_item_serializer = OrderItemSerializer(order_items, many=True)

                    if order_item_serializer.is_valid():
                        carts.delete()

                        return Response({'detail' : 'Success'}, status=status.HTTP_201_CREATED)

        except transaction.TransactionManagementError:
            return JsonResponse({'message':'TransactionManagementError'}, status = 400)  

        except KeyError:
            return JsonResponse({"message" : "KEYERROR"}, status = 400)
        
        except (Cart.DoesNotExist, OrderStatus.DoesNotExist):
            return JsonResponse({"message" : "INVALID_ERROR"}, status = 400)