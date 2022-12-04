from django.db.models import Min, Q, Prefetch

from rest_framework import serializers

from .models import Product, ProductSize, Size, ProductImage, InformationImage

class InformationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = InformationImage
        fields = ('sequence', 'url')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductImage
        fields = ('sequence', 'url')

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Size
        fields = "__all__"

class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    
    class Meta:
        model  = ProductSize
        fields = "__all__"

class ProductDetailSerializer(serializers.ModelSerializer):
    product_size      = ProductSizeSerializer(read_only=True)
    product_image     = ProductImageSerializer(read_only=True)
    information_image = InformationImageSerializer(read_only=True)
    
    class Meta:
        model  = Product
        fields = "__all__"

    def validate(self, product_id : int):
        product = Product.objects.filter(id=product_id).annotate(base_price=Min("productsizes__price"))[0]

        return product