from typing import OrderedDict

from rest_framework import serializers

from .models import Order, OrderItem, OrderStatus

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ("status",)

class OrderSerializer(serializers.ModelSerializer):
    order_status = OrderStatusSerializer(read_only=True) # 읽기만 할거고, 해당 테이블의 정보들을 가져오기 위해서 설정

    class Meta:
        model = Order
        fields = ("id", "order_number", "sender_name", "address", "recipient_name", "recipient_phone", "order_status")

    def create(self, validated_data : OrderedDict):
        return Order.objects.create(**validated_data)

class OrderSchemaSerializer(serializers.Serializer):
    '''
    Order Post Body Schema
    Only Use Swagger
    '''
    carts_ids       = serializers.ListField()
    address         = serializers.CharField()
    recipient_name  = serializers.CharField()
    recipient_phone = serializers.CharField()
    sender_name     = serializers.CharField(required=False)