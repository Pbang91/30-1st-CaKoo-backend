from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Min, Q, Prefetch

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from decorator import query_debugger

from .models import Product, ProductSize, Size
from .serializers import ProductDetailSerializer

permission_classes = [AllowAny]

product_id = openapi.Parameter('product_id', openapi.IN_PATH, required=True, type=openapi.TYPE_INTEGER)

class ProductDetailView(APIView):
    @swagger_auto_schema(manual_parameters=[product_id], responses={200 : ProductDetailSerializer})
    @query_debugger
    def get(self, requset, product_id):
        try:
            product = Product.objects.annotate(base_price=Min("productsizes__price"))\
                                    .prefetch_related(Prefetch('productsizes', queryset=ProductSize.objects.select_related('size')))\
                                    .get(id=product_id)
            
            serializer = ProductDetailSerializer(product)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response(data={"detail" : "Invalid Product"}, status=status.HTTP_400_BAD_REQUEST)

class ProductsView(View):
    @query_debugger
    def get(self, request): 
        try:
            sort     = request.GET.get('sort', "recent")
            size     = request.GET.get('size', 0)
            offset   = int(request.GET.get('offset', 0))
            limit    = int(request.GET.get('limit', 8))
            
            q = Q()
                
            if size:
                size = size.split(',')
                q &= Q(sizes__id__in=size)
            
            sort_set = {
                'recent'    : '-created_at',
                'old'       : 'created_at',
                'expensive' : '-base_price',
                'cheap'     : 'base_price' 
            } 
                      
            products = Product.objects.annotate(base_price=Min('productsizes__price'))\
                                      .filter(q).prefetch_related(Prefetch('sizes', queryset=Size.objects.all().order_by('id')))\
                                      .order_by(sort_set[sort])
            
            results = [{
                "id"             : product.id,
                "name"           : product.name,
                "description"    : product.description,
                "thumbnail"      : product.thumbnail,
                "sizes"          : [size.size for size in product.sizes.all()],
                "discount_rate"  : float(product.discount_rate),
                "price"          : int(product.base_price), 
                "discount_price" : int(product.base_price * product.discount_rate)
            } for product in products[offset:limit]]
            

            return JsonResponse({"lists" : results}, status = 200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)