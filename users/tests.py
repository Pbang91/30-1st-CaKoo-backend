from django.test   import TestCase, Client

import json

class SignUpTest(TestCase):
    def setUp(self):
        self.email        = 'test@test.com'
        self.password     = 'test123!!'
        self.name         = 'testman'
        self.phone_number = '010-1234-5678'
        self.birthdate    = '1990-01-01'

    def test_success_post_to_signup_email(self):
        client = Client()

        data = {
            'email'        : self.email,
            'password'     : self.password,
            'name'         : self.name,
            'phone_number' : self.phone_number,
            'birthdate'    : self.birthdate
        }

        response = client.post('/users/signup', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.json(),
            {
                'message' : 'SUCCESS'
            }
        )

    def test_fail_post_to_signup_invalid_email(self):
        client = Client()

        data = {
            'email'        : 'invalid_email@testcom',
            'password'     : self.password,
            'name'         : self.name,
            'phone_number' : self.phone_number,
            'birthdate'    : self.birthdate
        }

        response = client.post('/users/signup', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_fail_post_to_signup_invalid_password_not_special_symbols(self):
        client = Client()

        data = {
            'email'        : self.email,
            'password'     : 'test12345',
            'name'         : self.name,
            'phone_number' : self.phone_number,
            'birthdate'    : self.birthdate
        }

        response = client.post('/users/signup', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
    
    def test_fail_post_to_signup_invalid_password_less_than_8(self):
        client = Client()

        data = {
            'email'        : self.email,
            'password'     : 'test',
            'name'         : self.name,
            'phone_number' : self.phone_number,
            'birthdate'    : self.birthdate
        }

        response = client.post('/users/signup', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
    
    def test_fail_post_to_signup_key_error(self):
        client = Client()

        data = {
            'email'        : self.email,
            'name'         : self.name,
            'phone_number' : self.phone_number,
            'birthdate'    : self.birthdate
        }

        response = client.post('/users/signup', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)