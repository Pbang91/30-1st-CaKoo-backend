from django.urls import path

from carts.views import CartListView, CartDetailView

urlpatterns = [
    path('', CartListView.as_view()),
    path('/<int:cart_id>', CartDetailView.as_view()),
]