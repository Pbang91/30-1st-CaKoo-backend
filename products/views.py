from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Min, Q, Prefetch

from products.models  import Product, ProductSize, Size
from decorator        import query_debugger

class ProductDetailView(APIView):
    pass

class ProductDetailView(View):
    @query_debugger
    def get(self, request, product_id):
        try:
            products : list = [product for product in Product.objects.filter(id = product_id)\
                                                                     .annotate(base_price=Min("productsizes__price"))
                                                                     .prefetch_related(Prefetch('productimages'),
                                                                                       Prefetch('informationimages'),
                                                                                       Prefetch('productsizes', queryset=ProductSize.objects.select_related('size')))]
            product          = products[0]
            product_urls     = [image.url for image in product.productimages.all()]
            information_urls = [information_image.url for information_image in product.informationimages.all()]
            
            sizes = [{
                'size_id' : product_size.size.id,
                'size'    : product_size.size.size,
                'price'   : product_size.price
            } for product_size in product.productsizes.all()]
        
            result = {
                'description'        : product.description,
                'name'               : product.name,
                'base_price'         : product.base_price,
                'sizes'              : sizes,
                'discount_rate'      : product.discount_rate,
                'product_images'     : product_urls,
                'information_images' : information_urls
            }
            
            return JsonResponse({"message" : result}, status = 200)
        
        except IndexError:
            return JsonResponse({"message" : "INVALID_PRODUCT"}, status = 404)

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