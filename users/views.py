import json, bcrypt, jwt

from datetime         import datetime, timedelta

from django.forms     import ValidationError
from django.http      import JsonResponse
from django.views     import View

from users.models     import User
from users.validators import validate_email_and_password
from config.settings  import SECRET_KEY, ALGORITHM
from decorator        import query_debugger

class SignUpView(View):
    @query_debugger
    def post(self, request):
        try:
            request_data = json.loads(request.body)
            
            user_email : str        = request_data['email']
            user_password : str     = request_data['password']
            user_name : str         = request_data['name']
            user_phone_number : str = request_data['phone_number']
            user_birthdate : str    = request_data['birthdate']

            validated_email, validated_password = validate_email_and_password(email    = user_email,
                                                                              password = user_password)
            
            hashed_password = bcrypt.hashpw(validated_password.encode('utf-8'),
                                            bcrypt.gensalt()).decode('utf-8')
            
            user = User(
                        name         = user_name,
                        email        = validated_email,
                        password     = hashed_password,
                        phone_number = user_phone_number,
                        birthdate    = user_birthdate
                    )
            
            user.full_clean()
            user.save()

            return JsonResponse({"message": "SUCCESS"}, status = 201)
        
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        
        except ValidationError as err:
            return JsonResponse({"message" : str(err)}, status = 400)
        

class SignInView(View):
    @query_debugger
    def post(self, request):
        try:
            request_data = json.loads(request.body)
            
            user_email : str    = request_data['email']
            user_password : str = request_data['password']

            user = User.objects.get(email = user_email)

            checked_password = bcrypt.checkpw(user_password.encode('utf-8'), user.password.encode('utf-8'))
            
            if not checked_password:
                raise User.DoesNotExist
            
            access_token = jwt.encode({'user_id' : user.id, 'exp' : datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, ALGORITHM)
            
            return JsonResponse({"message" : "SUCCESS", "access_token" : access_token}, status = 200)
            
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status = 400)
        
        except User.DoesNotExist:
            return JsonResponse({"message" : "INVALID_USER"}, status = 400)