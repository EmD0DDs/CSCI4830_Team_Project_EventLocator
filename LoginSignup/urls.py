from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_signup_view, name="login_signup"),
]

