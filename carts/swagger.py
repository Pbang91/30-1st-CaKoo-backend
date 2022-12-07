from drf_yasg import openapi

class CartSwaager:
    cart_id = openapi.Parameter('cart_id', openapi.IN_PATH, required=True, type=openapi.TYPE_INTEGER)