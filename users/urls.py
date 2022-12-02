from django.urls import path

from users.views import SignUp, LogIn

urlpatterns = [
    path("signup", SignUp.as_view(), name="signup"),
    path("login", LogIn.as_view(), name='login'),
]