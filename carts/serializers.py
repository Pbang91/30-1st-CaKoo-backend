from rest_framework import serializers

from products.models import Product, ProductSize
from products.serializers import SizeSerializer

from .models import Cart

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "thumbnail", "discount_rate")

class ProductSizeSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(source="size")
    products = ProductSerializer(source="product")

    class Meta:
        model  = ProductSize
        fields = ("price", "products", "sizes")


class CartListSerializer(serializers.ModelSerializer):
    information = ProductSizeSerializer(source="product_size")
    discount_price = serializers.SerializerMethodField(method_name="get_discount_price")
    
    class Meta:
        model = Cart
        fields = ("id", "quantity", "information", "discount_price")

    def get_discount_price(self, obj):
        obj.discount_price = int(obj.product_size.price * obj.product_size.product.discount_rate)
        return obj.discount_price