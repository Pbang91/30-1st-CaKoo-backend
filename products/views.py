from django.db.models import Min, Q, Prefetch

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_yasg.utils import swagger_auto_schema

from decorator import query_debugger

from .models import Product, ProductSize
from .swaager import ProductSwaager 
from .serializers import ProductDetailSerializer, ProductListSerializer

permission_classes = [AllowAny]

class ProductDetailView(APIView):
    @swagger_auto_schema(manual_parameters=[ProductSwaager.product_id], tags=["Product"],responses={200 : ProductDetailSerializer})
    @query_debugger
    def get(self, requset, product_id):
        try:
            product = Product.objects.annotate(base_price=Min("productsizes__price"))\
                                    .prefetch_related(Prefetch('productsizes', queryset=ProductSize.objects.select_related('size')))\
                                    .get(id=product_id)
            
            serializer = ProductDetailSerializer(product)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response(data={"detail" : "Invalid Product"}, status=status.HTTP_404_NOT_FOUND)

class ProductListView(APIView):
    @swagger_auto_schema(manual_parameters=[ProductSwaager.sort, ProductSwaager.size, ProductSwaager.offset, ProductSwaager.limit], tags=["Product"],responses={200 : ProductDetailSerializer})
    @query_debugger
    def get(self, request):
        sort : str   = request.GET.get('sort', "recent")
        size : str   = request.GET.get('size', 0) #size_id param
        offset : int = int(request.GET.get('offset', 0))
        limit : int  = int(request.GET.get('limit', 8))

        sort_set = {
            'recent'    : '-created_at',
            'old'       : 'created_at',
            'expensive' : '-base_price',
            'cheap'     : 'base_price' 
        }

        q = Q()

        if size:
            size = size.split(',')
            q &= Q(sizes__id__in=size)

        products = Product.objects.annotate(base_price=Min('productsizes__price'))\
                                  .filter(q).order_by(sort_set[sort])[offset:offset+limit]
        
        serializer = ProductListSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)