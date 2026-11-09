from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('host-event/', login_required(TemplateView.as_view(template_name='host_event.html'), login_url='login_signup'), name='host_event'),
    path('', views.home_page, name="home"),
]