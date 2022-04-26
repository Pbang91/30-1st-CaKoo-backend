import re

from django.forms import ValidationError

def validate_email_and_password(email, password):
    email_regex    = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}'

    validated_email    = re.fullmatch(email_regex, email)
    validated_password = re.fullmatch(password_regex, password)

    if not validated_email:
        raise ValidationError("INVALID_EMAIL")
    
    if not validated_password:
        raise ValidationError("INVALID_PASSWORD")

    return validated_email.group(), validated_password.group()