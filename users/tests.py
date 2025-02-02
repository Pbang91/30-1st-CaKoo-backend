import json

import bcrypt

from django.urls import reverse

from rest_framework.test import APITestCase

from .models       import User

class UserSignUpTest(APITestCase):
    def setUp(self):
        self.url = reverse('signup')

    def test_success_user_signup(self):
        data = {
            "name" : "testman",
            "email" : "test@test.com",
            "password" : "test1234!",
            "phone_number" : "010-0000-0000",
            "birthdate" : "1900-01-01"
        }

        url = self.url

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "name" : "testman",
                "email" : "test@test.com",
                "phone_number" : "010-0000-0000",
                "birthdate" : "1900-01-01"
            }
        )
    def test_fail_user_signup_due_to_email_required(self):
        data = {
            'password'     : "test1234!",
            'name'         : "testman",
            'phone_number' : "010-0000-0000",
            'birthdate'    : "1900-01-01"
        }

        url = self.url

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "email" : ['This field is required.']
            }
        )
    
    def test_fail_user_signp_due_to_invalid_email(self):
        data = {
            'email'        : 'invalid_email@testcom',
            'password'     : "test1234!",
            'name'         : "testman",
            'phone_number' : "010-0000-0000",
            'birthdate'    : "1900-01-01"
        }

        url = self.url

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "email" : ["Enter a valid email address."]
            }
        )
    
    def test_fail_user_signup_due_to_password_required(self):
        data = {
            'email'        : 'test.test@test.com',
            'name'         : "testman",
            'phone_number' : "010-0000-0000",
            'birthdate'    : "1900-01-01"
        }

        url = self.url

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "password" : ['This field is required.']
            }
        )

    def test_fail_user_signup_due_to_invalid_password_not_special_symbols(self):
        data = {
            'email'        : "test@test.com",
            'password'     : 'test12345',
            'name'         : "testman",
            'phone_number' : "010-0000-0000",
            'birthdate'    : "1900-01-01"
        }
        
        url = self.url

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Invalid Information"
            }
        )
    
    def test_fail_user_signup_due_to_invalid_password_less_than_8(self):
        data = {
            'email'        : "test@test.com",
            'password'     : 'test',
            'name'         : "testman",
            'phone_number' : "010-0000-0000",
            'birthdate'    : "1900-01-01"
        }

        url = self.url

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "detail" : "Invalid Information"
            }
        )

class UserLoginTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        password = bcrypt.hashpw("test1234!".encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        
        User.objects.create(
            name = "user",
            email = "user@test.com",
            password = password,
            phone_number = "010-0000-0000",
            birthdate = "1900-01-01"
        )
    
    def setUp(self):
        self.url = reverse('login')
    
    def test_success_user_login(self):
        data = {
            'email' : 'user@test.com',
            'password' : "test1234!"
        }
        
        url = self.url
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        toten = response.json()['access_token']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "access_token" : toten
            }
        )
    
    def test_fail_user_login_invalid_email(self):
        data = {
            'email' : "user1@test.com",
            "password" : "test1234!"
        }

        url = self.url

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                'detail' : ['Invalid User']
            }
        )
    
    def test_fail_user_login_empty_email(self):
        data = {
            "password" : "test1234!"
        }

        url = self.url

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                'email': ['This field is required.']
            }
        )

    def test_fail_user_login_invalid_password(self):
        data = {
            'email' : "user@test.com",
            "password" : "test1234!!"
        }

        url = self.url

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                'detail' : ['Invalid User']
            }
        )
    
    def test_fail_user_login_empty_password(self):
        data = {
            "email" : "user@test.com"
        }

        url = self.url

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                'password': ['This field is required.']
            }
        )