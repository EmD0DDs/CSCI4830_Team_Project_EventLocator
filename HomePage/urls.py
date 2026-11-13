from django.urls import path
from . import views

urlpatterns = [
    path('host-event/', views.host_event, name='host_event'),
    path('', views.home_page, name='home'),
]