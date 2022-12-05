import json

from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Product, ProductSize, Size, ProductImage, InformationImage

class ProductDetailTest(APITestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        create_data = [Size(size="Mini"), Size(size='1호'), Size(size='2호'), Size(size='3호')]
        
        Size.objects.bulk_create(
            create_data
        )
        
        s1 = Size.objects.get(id=1)
        s2 = Size.objects.get(id=2)

        p1 = Product.objects.create(
            id = 1,
            name = "과일타르트케이크",
            description = "상큼한 과일로 장식한 케익",
            thumbnail = "https://test.test/delicious-cake1.jpeg",
            discount_rate = 0.80
        )

        ProductSize.objects.create(
            id = 1,
            price = 18000,
            product = p1,
            size = s1
        )

        ProductSize.objects.create(
            id = 2,
            price = 20000,
            product = p1,
            size = s2
        )

        p1.sizes.add(s1)
        p1.sizes.add(s2)

        create_data = [ProductImage(sequence=1,url="https://tmp.test/img1.jpeg", product=p1), ProductImage(sequence=2,url="https://tmp.test/img2.jpeg", product=p1)]

        ProductImage.objects.bulk_create(create_data)

        create_data = [InformationImage(sequence=1,url="https://test.test/img1.jpeg", product=p1), InformationImage(sequence=2,url="https://test.test/img2.jpeg", product=p1)]

        InformationImage.objects.bulk_create(create_data)
    
    @classmethod
    def tearDown(self):
        Size.objects.all().delete()
        Product.objects.all().delete()
        ProductSize.objects.all().delete()
        ProductImage.objects.all().delete()
        InformationImage.objects.all().delete()

    def test_success_product_view_detail(self):
        url = "/api/products/1"
        response = self.client.get(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "name" : "과일타르트케이크",
                "description" : "상큼한 과일로 장식한 케익",
                "discount_rate" : "0.80",
                "base_price" : 18000.0,
                "thumbnail" : "https://test.test/delicious-cake1.jpeg",
                "productsizes" : [
                    {
                        "price" : "18000.00",
                        "size" : {
                            "size" : "Mini"
                        }
                    },
                    {
                        "price" : "20000.00",
                        "size" : {
                            "size" : "1호"
                        }
                    },
                ],
                "productimages" : [
                    {
                        "sequence" : 1,
                        "url" : "https://tmp.test/img1.jpeg"
                    },
                    {
                        "sequence" : 2,
                        "url" : "https://tmp.test/img2.jpeg"
                    }
                ],
                "informationimages" : [
                    {
                        "sequence" : 1,
                        "url" : "https://test.test/img1.jpeg"
                    },
                    {
                        "sequence" : 2,
                        "url" : "https://test.test/img2.jpeg"
                    }
                ]
            }
        )
    
    def test_fail_product_detail_due_to_invalid_id(self):
        url = "/api/products/15"
        response = self.client.get(url, content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Invalid Product"
            }
        )

class ProductListTest(APITestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        s1 = Size.objects.create(size="Mini")
        s2 = Size.objects.create(size="1호")

        p1 = Product.objects.create(
            id = 1,
            name = "과일타르트케이크",
            description = "상큼한 과일로 장식한 케익",
            thumbnail = "https://test.test/delicious-cake1.jpeg",
            discount_rate = 0.80
        )

        p2 = Product.objects.create(
            id = 2,
            name = "그냥타르트케이크",
            description = "그냥타르트",
            thumbnail = "https://test.test/delicious-cake2.jpeg",
            discount_rate =  "0.80",
        )

        ProductSize.objects.create(
            id = 1,
            price = 18000,
            product = p1,
            size = s1
        )

        ProductSize.objects.create(
            id = 2,
            price = 20000,
            product = p1,
            size = s2
        )

        ProductSize.objects.create(
            id = 3,
            price = 30000,
            product = p2,
            size = s2
        )

        p1.sizes.add(s1)
        p1.sizes.add(s2)
        p2.sizes.add(s2)

        create_data = [ProductImage(sequence=1,url="https://tmp.test/img1.jpeg", product=p1), ProductImage(sequence=2,url="https://tmp.test/img2.jpeg", product=p1)]

        ProductImage.objects.bulk_create(create_data)

        create_data = [InformationImage(sequence=1,url="https://test.test/img1.jpeg", product=p1), InformationImage(sequence=2,url="https://test.test/img2.jpeg", product=p1)]

        InformationImage.objects.bulk_create(create_data)
    
    def setUp(self):
       self.url = "/api/products/" 
    
    @classmethod
    def tearDown(self):
        Size.objects.all().delete()
        Product.objects.all().delete()
        ProductSize.objects.all().delete()
        ProductImage.objects.all().delete()
        InformationImage.objects.all().delete()
    
    def test_success_product_view_list(self):
        url = self.url
        
        response = self.client.get(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "name": "그냥타르트케이크",
                    "description": "그냥타르트",
                    "base_price": 30000.0,
                    "thumbnail": "https://test.test/delicious-cake2.jpeg",
                    "discount_rate": "0.80",
                    "productsizes": [
                        {
                            "price": "30000.00",
                            "size": {
                                "size": "1호"
                            }
                        }
                    ]
                },
                {
                    "name": "과일타르트케이크",
                    "description": "상큼한 과일로 장식한 케익",
                    "base_price": 18000.0,
                    "thumbnail": "https://test.test/delicious-cake1.jpeg",
                    "discount_rate": "0.80",
                    "productsizes": [
                        {
                            "price": "18000.00",
                            "size": {
                                "size": "Mini"
                            }
                        },
                        {
                            "price": "20000.00",
                            "size": {
                                "size": "1호"
                            }
                        }
                    ]
                }
            ]
        )