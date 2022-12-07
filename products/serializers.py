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
        fields = ("size",)

class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    
    class Meta:
        model  = ProductSize
        fields = ("price", "size")

class ProductDetailSerializer(serializers.ModelSerializer):
    base_price        = serializers.SerializerMethodField(method_name="get_base_price")
    productimages     = ProductImageSerializer(many=True) #models.ProductImage의 related_name과 같게 설정, many 설정은 Query set이 여러개일 경우 설정
    informationimages = InformationImageSerializer(many=True)
    productsizes      = ProductSizeSerializer(many=True)
    
    class Meta:
        model  = Product
        fields = ("name", "description", "base_price", "thumbnail", "discount_rate", "productimages", "informationimages", "productsizes")

    def get_base_price(self, obj):
        return obj.base_price

class ProductListSerializer(ProductDetailSerializer):
    class Meta:
        model = Product
        fields = ("name", "description", "base_price", "thumbnail", "discount_rate", "productsizes")