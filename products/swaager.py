from drf_yasg import openapi

class ProductSwaager:
    product_id = openapi.Parameter('product_id', openapi.IN_PATH, required=True, type=openapi.TYPE_INTEGER)
    sort = openapi.Parameter('sort', openapi.IN_QUERY, required=True, type=openapi.TYPE_STRING)
    size = openapi.Parameter('size', openapi.IN_QUERY, required=True, type=openapi.TYPE_INTEGER)
    offset = openapi.Parameter('offset', openapi.IN_QUERY, required=True, type=openapi.TYPE_INTEGER)
    limit = openapi.Parameter('limit', openapi.IN_QUERY, required=True, type=openapi.TYPE_INTEGER)