import uuid
from enum import Enum

from django.db import transaction
from django.http import JsonResponse

from users.utils import login_decorator
from carts.models import Cart
from orders.models import Order, OrderItem, OrderStatus

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from decorator import query_debugger

from .serializer import OrderSerializer

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
            user = request.user
            
            cart_ids     = request.data["cart_ids"]
            carts        = Cart.objects.filter(user=user, id__in=cart_ids)
            order_status = OrderStatus.objects.get(id=OrderStatusEnum.CONFIRMED.value)

            data = {
                'user' : user,
                'address' : request.data['address'],
                'recipient_name' : request.data['recipient_name'],
                "recipient_phone" : request.data['recipient_phone'],
                'sender_name' : user.name,
                'order_number' : str(uuid.uuid4()),
                'order_status' : order_status
            }
            
            order = Order.objects.create(**data)

            with transaction.atomic():
                order_items = [
                    OrderItem(
                        order        = order,
                        product_size = cart.product_size,
                        quantity     = cart.quantity
                    ) for cart in carts
                ]
                
                OrderItem.objects.bulk_create(order_items)

                carts.delete()

                return Response({'detail' : 'Success'}, status=status.HTTP_201_CREATED)

        except transaction.TransactionManagementError:
            return JsonResponse({'detail':'Transaction Management Error'}, status = 400)  

        except KeyError:
            return JsonResponse({"datail" : "Invalid User"}, status = 400)
        
        except (Cart.DoesNotExist, OrderStatus.DoesNotExist):
            return JsonResponse({"detail" : "Invalid Order"}, status = 400)