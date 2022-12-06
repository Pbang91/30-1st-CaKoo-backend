import json
from datetime import datetime, timedelta

import bcrypt
import jwt

from rest_framework.test import APITestCase, APIClient

from users.models import User
from config.settings import SECRET_KEY, ALGORITHM
from products.models import Product, ProductSize, Size

from .models import Cart

class CartTest(APITestCase):
    maxDiff: int = None

    @classmethod
    def setUpTestData(cls):
        password = bcrypt.hashpw("010-0000-0000".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        cls.user = User.objects.create(
            name = "test",
            email = "test.test@test.com",
            password = password,
            phone_number = "010-0000-0000",
        )

        cls.f_client = APIClient()

        token = jwt.encode({'user_id' : cls.user.id, 'exp' : datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, ALGORITHM)

        cls.f_client.credentials(HTTP_AUTHORIZATION=token)

        # cls.f_client.force_authenticate(user=cls.user, token=token)

        size_create_data = [Size(id=1, size="Mini"), Size(id=2, size='1호'), Size(id=3, size='2호'), Size(id=4, size='3호')]
        Size.objects.bulk_create(size_create_data)

        product_create_data = [
            Product(
                id = 1,
                name = "과일타르트케이크",
                description = "상큼한 과일로 장식한 케익",
                thumbnail = "https://test.test/delicious-cake1.jpeg",
                discount_rate = 0.80
            ),
            Product(
                id = 2,
                name = "그냥 타르트케이크",
                description = "일반적인 타르트 케익",
                thumbnail = "https://test.test/delicious-cake2.jpeg",
                discount_rate = 0.90
            ),
            Product(
                id = 3,
                name = "초코 케이크",
                description = "달달한 초코 케익",
                thumbnail = "https://test.test/delicious-cake3.jpeg",
                discount_rate = 0.85
            ),
            Product(
                id = 4,
                name = "딸기 케이크",
                description = "제철 딸기 케잌",
                thumbnail = "https://test.test/delicious-cake4.jpeg",
                discount_rate = 0.95
            )
        ]
        
        Product.objects.bulk_create(product_create_data)

        s1 = Size.objects.get(id=1)
        s2 = Size.objects.get(id=2)
        s3 = Size.objects.get(id=3)
        s4 = Size.objects.get(id=4)

        p1 = Product.objects.get(id=1)
        p2 = Product.objects.get(id=2)
        p3 = Product.objects.get(id=3)
        p4 = Product.objects.get(id=4)

        product_size_create_data = [
            ProductSize(
                id = 1,
                price = 18000,
                product = p1,
                size = s1
            ),
            ProductSize(
                id = 2,
                price = 22000,
                product = p1,
                size = s2
            ),
            ProductSize(
                id = 3,
                price = 25000,
                product = p1,
                size = s3
            ),
            ProductSize(
                id = 4,
                price = 15000,
                product = p2,
                size = s2
            ),
            ProductSize(
                id = 5,
                price = 20000,
                product = p3,
                size = s2
            ),
            ProductSize(
                id = 6,
                price = 24000,
                product = p3,
                size = s3
            ),
            ProductSize(
                id = 7,
                price = 30000,
                product = p4,
                size = s4
            )
        ]

        ProductSize.objects.bulk_create(product_size_create_data)

        ps1 = ProductSize.objects.get(id=1)
        ps2 = ProductSize.objects.get(id=2)
        ps4 = ProductSize.objects.get(id=4)
        ps7 = ProductSize.objects.get(id=7)

        cart_create_data = [
            Cart(id=1, quantity=2, user=cls.user, product_size=ps1),
            Cart(id=2, quantity=1, user=cls.user, product_size=ps7)
        ]

        Cart.objects.bulk_create(cart_create_data)

    def test_success_cart_list_view(self):
        response = self.f_client.get('/api/carts/', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "id" : 1,
                    "information" : {
                        "price" : "18000.00",
                        "products" : {
                            "name" : "과일타르트케이크",
                            "thumbnail" : "https://test.test/delicious-cake1.jpeg",
                            "discount_rate" : "0.80"
                        },
                        "sizes" : {
                            "size" : "Mini"
                        }
                    },
                    "quantity" : 2,
                    "discount_price" : 14400
                },
                {
                    "id" : 2,
                    "information" : {
                        "price" : "30000.00",
                        "products" : {
                            "name" : "딸기 케이크",
                            "thumbnail" : "https://test.test/delicious-cake4.jpeg",
                            "discount_rate" : "0.95"
                        },
                        "sizes" : {
                            "size" : "3호"
                        }
                    },
                    "quantity" : 1,
                    "discount_price" : 28500,
                }
            ]
        )

    def test_success_empty_cart_list_view(self):
        Cart.objects.all().delete()

        response = self.f_client.get('/api/carts/', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'detail' : 'Empty Cart'
            }
        )
    
    def test_success_put_cart_list(self):
        data = {"size_id" : 2, "product_id" : 1, "quantity" : 4}

        response = self.f_client.post('/api/carts/', data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                'detail' : 'Success'
            }
        )

    def test_fail_cart_list_due_to_unauthorized_user(self):
        response = self.client.get('/api/carts/', content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "detail" : "No Authorization In Header"
            }
        )
    
    def test_fail_cart_list_due_to_non_exist_user(self):
        token = jwt.encode({'user_id' : 155, 'exp' : datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, ALGORITHM)
        self.f_client.credentials(HTTP_AUTHORIZATION=token)
        
        response = self.f_client.get('/api/carts/', content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Invalid User"
            }
        )