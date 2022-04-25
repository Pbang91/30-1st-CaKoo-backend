import re

def validate_email_and_password(email, password):
    email_regex    = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}'

    validated_email    = re.fullmatch(email_regex, email)
    validated_password = re.fullmatch(password_regex, password)

    return validated_email.group(), validated_password.group()