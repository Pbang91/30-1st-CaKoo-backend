import uuid
from enum import Enum

from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from users.utils import login_decorator
from carts.models import Cart
from orders.models import Order, OrderItem, OrderStatus
from products.models import Stock

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from decorator import query_debugger

from .serializer import OrderSerializer, OrderSchemaSerializer

class OrderStatusEnum(Enum):
    CONFIRMED = 1  
    CANCELED  = 2
    PENDING   = 3

class OrderView(APIView):
    @swagger_auto_schema(responses={200 : OrderSerializer, 400 : 'Invalid User'}, tags=["Order"], operation_summary='Get Order List')
    @query_debugger
    @login_decorator
    def get(self, request):
        try:
            orders = Order.objects.filter(user_id = request.user).select_related('user')
            
            serializer = OrderSerializer(orders, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Order.DoesNotExist:
            return Response({"detail" : "Invalid User"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=OrderSchemaSerializer, responses={201 : "Success", 400 : 'Invalid User'}, tags=["Order"], operation_summary='Order Items')
    @query_debugger
    @login_decorator
    def post(self, request):
        try:
            user = request.user
            
            cart_ids     = request.data["cart_ids"]
            carts        = Cart.objects.filter(user=user, id__in=cart_ids).select_related('product_size__product')
            order_status = OrderStatus.objects.get(id=OrderStatusEnum.CONFIRMED.value)

            data = {
                'user'            : user,
                'address'         : request.data['address'],
                'recipient_name'  : request.data['recipient_name'],
                "recipient_phone" : request.data['recipient_phone'],
                'sender_name'     : user.name,
                'order_number'    : str(uuid.uuid4()),
                'order_status'    : order_status
            }
            
            #TODO validator 적용 or Serializer 적용 코드로 변경
            with transaction.atomic():
                order = Order.objects.create(**data)

                for cart in carts:
                    stock = Stock.objects.get(product=cart.product_size.product)
                    stock.quantity -= cart.quantity

                    if stock.quantity < 0:
                        raise ValidationError('Out Of Stock')

                    stock.save()

                    OrderItem.objects.create(
                        order = order,
                        product_size = cart.product_size,
                        quantity = cart.quantity
                    )

                carts.delete()

                return Response({'detail' : 'Success'}, status=status.HTTP_201_CREATED)

        except transaction.TransactionManagementError:
            return JsonResponse({'detail':'Transaction Management Error'}, status = 400)  

        except KeyError:
            return JsonResponse({"detail" : "Invalid Required Information"}, status = 400)
        
        except (Cart.DoesNotExist, OrderStatus.DoesNotExist):
            return JsonResponse({"detail" : "Invalid Required Information"}, status = 400)
        
        except ValidationError as error:
            return JsonResponse({"detail" : error.message}, status = 400)