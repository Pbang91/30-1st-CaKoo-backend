from typing import OrderedDict

from rest_framework import serializers

from products.models import Product, ProductSize
from products.serializers import ProductSizeSerializer

from .models import Cart

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "thumbnail", "discount_rate")

class CartProductSizeSerializer(ProductSizeSerializer):
    products = ProductSerializer(source="product")

    class Meta:
        model  = ProductSize
        fields = ("price", "products", "size")

class CartListSerializer(serializers.ModelSerializer):
    information = CartProductSizeSerializer(source="product_size")
    discount_price = serializers.SerializerMethodField(method_name="get_discount_price")
    
    class Meta:
        model = Cart
        fields = ("id", "quantity", "information", "discount_price")

    def get_discount_price(self, obj):
        obj.discount_price = int(obj.product_size.price * obj.product_size.product.discount_rate)
        
        return obj.discount_price

class CartStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ("quantity", "user", "product_size")

    def create(self, validated_data : OrderedDict):
        cart = Cart.objects.create(**validated_data)
        
        return cart
    
    def update(self, instance : Cart, validated_data : OrderedDict):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.user = validated_data.get('user', instance.user)
        instance.product_size = validated_data.get('product_size', instance.product_size)

        instance.save()

        return instance

class CartSchema(serializers.Serializer):
    '''
    CartList 스키마 시리얼라이저[only used for swagger]
    '''
    size_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()