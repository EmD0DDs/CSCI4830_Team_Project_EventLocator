import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time, timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse

from django.utils import timezone

from .APIcalls import Events
from .forms import EventForm

logger = logging.getLogger(__name__)

# Downtown Omaha, used when the browser doesn't send a location
OMAHA_LAT, OMAHA_LON = 41.2565, -95.9345
SEARCH_RADIUS_MILES = 25
CARDS_PER_GROUP = 3
CACHE_SECONDS = 15 * 60

# Home page category button -> PredictHQ categories.
# Each button gets its own API request, so busy categories (lots of "community" events)
# can't push the others off the page.
GROUP_CATEGORIES = {
    "Music": "concerts,performing-arts",
    "Sports": "sports",
    "Communication": "conferences,expos",
    "Education": "academic",
    "Others": "community,festivals",
}

# PredictHQ category -> home page category button
CATEGORY_GROUPS = {
    category: group
    for group, categories in GROUP_CATEGORIES.items()
    for category in categories.split(",")
}

# Card pictures and label style for each home page category (the API has no event photos).
# Cards in the same category take turns through their pictures.
CATEGORY_STYLE = {
    "Music": (["HomePage/images/concert(1).webp"], "music-label"),
    "Sports": (["HomePage/images/Baskeball.jpg", "HomePage/images/slides/slide10.jpg"], "sports-label"),
    "Communication": (["HomePage/images/slides/slide06.jpg", "HomePage/images/slides/slide03.jpg"], "other-label"),
    "Education": (["HomePage/images/slides/slide11.jpg", "HomePage/images/slides/slide08.jpg"], "other-label"),
    "Others": (["HomePage/images/omahaFarmersMarket.jpeg", "HomePage/images/slides/slide02.jpg", "HomePage/images/slides/slide03.jpg"], "other-label"),
}

# Kenneth's sample cards, shown when the API gives us nothing (no internet, trial ended, no events).
# (title, place, days from today, start time, category, picture, picture description)
# Dates move with today so the samples always look upcoming.
DEMO_EVENTS = [
    ("UNO Fall Concert", "Baxter Arena", 3, time(19, 0), "Music",
     "HomePage/images/concert(1).webp", "Concert crowd and illuminated stage"),
    ("UNO Mavericks Home Game", "Baxter Arena, Omaha, NE", 5, time(14, 0), "Sports",
     "HomePage/images/Baskeball.jpg", "Basketball players on an indoor court"),
    ("Omaha Farmers Market", "Old Market, Omaha, NE", 10, time(10, 0), "Others",
     "HomePage/images/omahaFarmersMarket.jpeg", "Shoppers walking through the Omaha Old Market farmers market"),
]


def demo_events():
    today = timezone.localdate()
    return [
        {
            "title": title,
            "place": place,
            "start": datetime.combine(today + timedelta(days=days), start_time),
            "show_time": True,
            "category": category,
            "image": image,
            "alt": alt,
            "label_class": CATEGORY_STYLE[category][1],
        }
        for title, place, days, start_time, category, image, alt in DEMO_EVENTS
    ]


def _coordinates(request):
    """Browser location from ?lat=&lon= (set by home_page.js), else Omaha."""
    try:
        lat = float(request.GET["lat"])
        lon = float(request.GET["lon"])
    except (KeyError, ValueError):
        return OMAHA_LAT, OMAHA_LON
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return OMAHA_LAT, OMAHA_LON
    return round(lat, 2), round(lon, 2)


def _to_card(event, index_in_group):
    group = CATEGORY_GROUPS.get(event.get("Category"), "Others")
    images, label_class = CATEGORY_STYLE[group]
    try:
        start = datetime.fromisoformat(event.get("Start_Time", ""))
    except ValueError:
        start = None
    address = event.get("Location") or ""
    if address == "Location unavailable":
        address = ""
    address = address.removesuffix(", United States of America")
    # PredictHQ's predicted attendance; APIcalls turns missing values into "None"/"Not Available"
    try:
        attendance = int(event.get("Attendance", ""))
    except ValueError:
        attendance = None
    return {
        "title": event.get("Title"),
        "place": event.get("Venue") or address or "Omaha, NE",
        "attendance": f"{attendance:,}" if attendance else None,
        "start": start,
        # All-day events start at midnight; show only the date for those
        "show_time": start is not None and (start.hour, start.minute) != (0, 0),
        "category": group,
        "image": images[index_in_group % len(images)],
        "label_class": label_class,
    }


def _group_events(group, lat, lon):
    """The soonest few events for one category button, or None if the request failed."""
    try:
        return Events().get_event(GROUP_CATEGORIES[group], SEARCH_RADIUS_MILES, "mi", "Omaha", 0,
                                  lat=lat, lon=lon, limit=CARDS_PER_GROUP)
    except Exception:
        logger.exception("Could not load %s events from PredictHQ", group)
        return None


def upcoming_events(lat, lon):
    """Upcoming events near (lat, lon) as card dicts, a few per category, soonest first.
    Cached; returns [] if the API fails."""
    cache_key = f"home-events:{lat}:{lon}"
    cards = cache.get(cache_key)
    if cards is not None:
        return cards
    # One request per category, sent at the same time so the page isn't slowed down
    with ThreadPoolExecutor(max_workers=len(GROUP_CATEGORIES)) as pool:
        results = list(pool.map(lambda group: _group_events(group, lat, lon), GROUP_CATEGORIES))
    if all(events is None for events in results):
        return []
    cards = []
    for events in results:
        for index, event in enumerate((events or [])[:CARDS_PER_GROUP]):
            cards.append(_to_card(event, index))
    # Cards without a date go last
    cards.sort(key=lambda card: (card["start"] is None, card["start"] or datetime.max))
    # Only cache complete results, so a failed category is retried on the next visit
    if None not in results:
        cache.set(cache_key, cards, CACHE_SECONDS)
    return cards

# Create your views here.
@login_required(login_url='login_signup')
def home_page(request):
    lat, lon = _coordinates(request)
    events = upcoming_events(lat, lon)
    is_demo = not events
    if is_demo:
        events = demo_events()
    return render(request, 'home.html', {"events": events, "is_demo": is_demo})
  
    
    

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
