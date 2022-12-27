import json
from uuid import uuid4
from datetime import datetime, timedelta

import jwt
import bcrypt

from rest_framework.test import APITestCase, APIClient

from users.models import User
from carts.models import Cart
from products.models import Size, Product, ProductSize, Stock
from config.settings import SECRET_KEY, ALGORITHM

from .models import Order, OrderItem, OrderStatus


class OrderTest(APITestCase):
    maxDiff : int = None

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
            )
        ]

        Product.objects.bulk_create(product_create_data)

        Stock.objects.create(quantity=2, product_id=1)
        Stock.objects.create(quantity=15, product_id=2)

        s1 = Size.objects.get(id=1)
        s2 = Size.objects.get(id=2)
        p1 = Product.objects.get(id=1)
        p2 = Product.objects.get(id=2)

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
                price = 15000,
                product = p2,
                size = s2
            )
        ]

        ProductSize.objects.bulk_create(product_size_create_data)

        ps1 = ProductSize.objects.get(id=1)
        ps2 = ProductSize.objects.get(id=2)
        ps3 = ProductSize.objects.get(id=3)

        cart_create_data = [
            Cart(id=1, quantity=1, user=cls.user, product_size=ps1),
            Cart(id=2, quantity=1, user=cls.user, product_size=ps2),
            Cart(id=3, quantity=1, user=cls.user, product_size=ps3),
        ]

        Cart.objects.bulk_create(cart_create_data)
        
        order_status_create_data = [
            OrderStatus(id=1, status="Confirmed"),
            OrderStatus(id=2, status="Canceled"),
            OrderStatus(id=3, status="Pending")
        ]

        OrderStatus.objects.bulk_create(order_status_create_data)

        os1 = OrderStatus.objects.get(id=1)

        cls.order_number1 = uuid4()
        
        o1 = Order.objects.create(
            order_number = cls.order_number1,
            sender_name = "giver1",
            address = "test dong, test gu, test city, Repulic of Korea",
            recipient_name = "reciever1",
            recipient_phone = "010-1111-1111",
            order_status = os1,
            user = cls.user
        )
        
        cls.order_number2 = uuid4()
        
        o2 = Order.objects.create(
            order_number = cls.order_number2,
            sender_name = "giver2",
            address = "test dong, test gu, test city, Repulic of Korea",
            recipient_name = "reciever2",
            recipient_phone = "010-1111-1112",
            order_status = os1,
            user = cls.user
        )

        OrderItem.objects.create(
            order = o1,
            product_size = ps1,
            quantity = 2
        )

        OrderItem.objects.create(
            order = o2,
            product_size = ps2,
            quantity = 1
        )

    def test_success_order_get_list(self):
        '''
        View Order List
        '''
        order_number1 = str(self.order_number1)
        order_number2 = str(self.order_number2)
        
        response = self.f_client.get("/api/orders")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    'id' : 1,
                    'order_number' : order_number1,
                    "sender_name" : 'giver1',
                    'address' : "test dong, test gu, test city, Repulic of Korea",
                    'recipient_name' : 'reciever1',
                    'recipient_phone' : '010-1111-1111',
                    'order_status' : {
                        'status' : 'Confirmed'
                    }
                },
                {
                    'id' : 2,
                    'order_number' : order_number2,
                    'sender_name' : 'giver2',
                    'address' : 'test dong, test gu, test city, Repulic of Korea',
                    'recipient_name' : 'reciever2',
                    'recipient_phone' : '010-1111-1112',
                    'order_status' : {
                        'status' : 'Confirmed'
                    }
                }
            ]
        )
    
    def test_success_order_items(self):
        '''
        Order Items
        '''

        Order.objects.all().delete()

        data = {
            'cart_ids' : [1, 2, 3],
            'address' : 'test city',
            'recipient_name' : '아무개',
            'recipient_phone' : '010-1234-5678'
        }

        response = self.f_client.post('/api/orders', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                'detail' : 'Success'
            }
        )
    
    def test_fail_order_get_list_due_to_unauthorized_user(self):
        '''
        View Order List
        '''
        response = self.client.get('/api/orders', content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Unauthorized User"
            }
        )

    def test_fail_order_get_list_non_exist_user(self):
        token = jwt.encode({'user_id' : 155, 'exp' : datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, ALGORITHM)
        self.f_client.credentials(HTTP_AUTHORIZATION=token)

        response = self.f_client.get('/api/orders', content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Invalid User"
            }
        )
    
    def test_fail_orders_items_due_to_unauthorized_user(self):
        '''
        Order Items
        '''
        Order.objects.all().delete()

        data = {
            'cart_ids' : [1, 2, 3],
            'address' : 'test city',
            'recipient_name' : '아무개',
            'recipient_phone' : '010-1234-5678'
        }

        response = self.client.post('/api/orders', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Unauthorized User"
            }
        )

    def test_fail_orders_items_non_exist_user(self):
        token = jwt.encode({'user_id' : 155, 'exp' : datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, ALGORITHM)
        self.f_client.credentials(HTTP_AUTHORIZATION=token)
        Order.objects.all().delete()


        data = {
            'cart_ids' : [1, 2, 3],
            'address' : 'test city',
            'recipient_name' : '아무개',
            'recipient_phone' : '010-1234-5678'
        }

        response = self.f_client.post('/api/orders', data=data, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Invalid User"
            }
        )
    
    def test_fail_order_items_due_to_invalid_quantity(self):
        modified_cart = Cart.objects.get(id=3)

        modified_cart.quantity += 200
        modified_cart.save()

        data = {
            'cart_ids' : [1, 2, 3],
            'address' : 'test city',
            'recipient_name' : '아무개',
            'recipient_phone' : '010-1234-5678'
        }

        response = self.f_client.post('/api/orders', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                'detail' : "Out Of Stock"
            }
        )