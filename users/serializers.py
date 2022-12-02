import re
from datetime import datetime, timedelta

import jwt
import bcrypt

from rest_framework import serializers

from config.settings import SECRET_KEY, ALGORITHM

from .models import User


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ('name', 'email', 'password', 'phone_number', 'birthdate')

        extra_kwargs = {
            'password' : {'write_only' : True}
        }
        
    def create(self, validated_data : dict):
        email : str    = validated_data.get('email')
        password : str = validated_data.get('password')
        
        email_regex    = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}'

        validated_email    = re.fullmatch(email_regex, email)
        validated_password = re.fullmatch(password_regex, password)

        if not validated_password or not validated_email:
            raise serializers.ValidationError({"detail" : "Invalid Information"})

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        
        validated_data['password'] = hashed_password

        user = User.objects.create(**validated_data)

        del user.password

        return user

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ('email', 'password')

    def validate(self, validated_data : dict):
        email    = validated_data.email
        password = validated_data.password

        try:
            user = User.objects.get(email=email)
        
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail' : 'Invalid User'})
        
        checked_password = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))

        if not checked_password:
            raise serializers.ValidationError({'detail' : 'Invalid User'})
        
        access_token = jwt.encode({'user_id' : user.id, 'exp' : datetime.utcnow() + timedelta(days=2)}, SECRET_KEY, ALGORITHM)

        data = {
            'access_token' : access_token
        }

        return data