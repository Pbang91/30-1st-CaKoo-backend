from django.urls    import path

from products.views import ProductsView, ProductDetailView

urlpatterns = [
    path('/<int:product_id>', ProductDetailView.as_view(), name='product_detail'),
    path('', ProductsView.as_view()),
]