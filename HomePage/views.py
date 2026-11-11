from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import APIcalls
from .forms import EventForm

# Create your views here.
@login_required(login_url='login_signup')
def home_page(request):
    events = APIcalls.Events().get_event(category="None",radius=25,unit="mi",location="Omaha, NE",offset=0)
    return render(request, 'home.html', {'events': events})

@login_required(login_url='login_signup')
def host_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            messages.success(request, "Event created!")
            return redirect("host_event")
    else:
        form = EventForm()
    return render(request, "host_event.html", {"form": form})