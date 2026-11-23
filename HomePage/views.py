from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.dateparse import parse_date, parse_time

from . import APIcalls
from .forms import EventForm
from .models import Event

# Create your views here.
@login_required(login_url='login_signup')
def home_page(request):
    #return render(request, 'home.html')
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


def _parse(parser, value):
    """Return a parsed date/time, or None if blank or invalid."""
    try:
        return parser(value) if value else None
    except ValueError:
        return None


def public_events(request):
    filters = {
        "q": request.GET.get("q", "").strip(),
        "category": request.GET.get("category", "").strip(),
        "location": request.GET.get("location", "").strip(),
        "date": request.GET.get("date", "").strip(),
        "time": request.GET.get("time", "").strip(),
        "max_price": request.GET.get("max_price", "").strip(),
    }

    events = Event.objects.filter(visibility="public").order_by("date", "time")

    if filters["q"]:
        events = events.filter(
            Q(name__icontains=filters["q"])
            | Q(description__icontains=filters["q"])
            | Q(location__icontains=filters["q"])
        )
    #Category
    valid_categories = [c[0] for c in Event.CATEGORY_CHOICES]
    if filters["category"] in valid_categories:
        events = events.filter(category=filters["category"])

    # Location
    if filters["location"]:
        events = events.filter(location__icontains=filters["location"])

    # Date
    date = _parse(parse_date, filters["date"])
    if date:
        events = events.filter(date__gte=date)


    # Time
    time = _parse(parse_time, filters["time"])
    if time:
        events = events.filter(time__lte=time)

    # Max price
    if filters["max_price"]:
        try:
            events = events.filter(price__lte=float(filters["max_price"]))
        except ValueError:
            pass

    return render(request, "view_events.html", {
        "events": events,
        "filters": filters,
        "categories": Event.CATEGORY_CHOICES,
    })