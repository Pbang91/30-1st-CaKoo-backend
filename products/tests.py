import json

from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Product, ProductSize, Size, ProductImage, InformationImage

class ProductDetailTest(APITestCase):
    @classmethod
    def setUpTestData(cls):

        create_data = [Size(size="Mini"), Size(size='1호'), Size(size='2호'), Size(size='3호')]
        
        Size.objects.bulk_create(
            create_data
        )

        Product.objects.create(
            id = 1,
            name = "과일타르트케이크",
            description = "상큼한 과일로 장식한 케익",
            thumbnail = "https://test.test/delicious-cake.img",
            discout_rate = 0.80
        )

        



    def setUp(self):
        self.url = reverse('product_detail')

    def test_success_product_view_detail(self):
        product_id = "1"