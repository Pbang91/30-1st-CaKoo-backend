from django.urls import path

from products.views import ProductListView, ProductDetailView

urlpatterns = [
    path('/<int:product_id>', ProductDetailView.as_view(), name='product_detail'),
    path('', ProductListView.as_view()),
]