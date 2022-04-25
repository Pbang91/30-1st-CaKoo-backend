import json, bcrypt, jwt
from django.forms import EmailField, ValidationError

from django.http      import JsonResponse
from django.views     import View
from pymysql import DatabaseError, IntegrityError

from users.models     import User
from users.validators import validate_email_and_password
from config.settings  import SECRET_KEY, ALGORITHM
from decorator        import query_debugger

class SignUpView(View):
    @query_debugger
    def post(self, request):
        try:
            data = json.loads(request.body)

            validated_email, validated_password = validate_email_and_password(email = data['email'], password = data['password'])

            if validated_email and validated_password:
                hashed_password = bcrypt.hashpw(validated_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                user = User(
                            name         = data['name'],
                            email        = validated_email,
                            password     = hashed_password,
                            phone_number = data['phone_number'],
                            birthdate    = data['birthdate']
                        )
                
                user.full_clean()
                user.save()

                return JsonResponse({"message": "SUCCESS"}, status = 201)

            return JsonResponse({'message' : 'INVALID_FORM'}, status = 400)
        
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status = 400)
        
        except ValidationError as err:
            return JsonResponse({"message" : str(err)}, status = 400)
        

class SignInView(View):
    def post(self, request):
        try:
            data            = json.loads(request.body)
            signin_email    = data['email']
            signin_password = data['password']

            if not User.objects.filter(email = signin_email).exists():
                return JsonResponse({"message" : "INVALID_USER"}, status = 401)

            user         = User.objects.get(email = signin_email)
            access_token = jwt.encode({'user_id' : user.id}, SECRET_KEY, ALGORITHM)
            
            if not bcrypt.checkpw(signin_password.encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({"message" : "INVALID_USER"}, status = 401)

            return JsonResponse({"message" : "SUCCESS", "access_token" : access_token}, status = 200)
            
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status = 400)