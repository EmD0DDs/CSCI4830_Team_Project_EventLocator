from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import APIcalls

# Create your views here.
@login_required(login_url='login_signup')
def home_page(request):
    events = APIcalls.Events().get_event(category="None",radius=25,unit="mi",location="Omaha, NE",offset=0)
    return render(request, 'home.html', {'events': events})
