import logging
from datetime import datetime, time, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone

from .APIcalls import Events

logger = logging.getLogger(__name__)

# Downtown Omaha, used when the browser doesn't send a location
OMAHA_LAT, OMAHA_LON = 41.2565, -95.9345
SEARCH_RADIUS_MILES = 25
MAX_CARDS = 12
CACHE_SECONDS = 15 * 60

PREDICTHQ_CATEGORIES = "concerts,sports,conferences,expos,academic,community,festivals,performing-arts"

# PredictHQ category -> home page category button
CATEGORY_GROUPS = {
    "concerts": "Music",
    "sports": "Sports",
    "conferences": "Communication",
    "expos": "Communication",
    "academic": "Education",
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
    address = (event.get("Location") or {}).get("formatted_address") or ""
    address = address.removesuffix(", United States of America")
    return {
        "title": event.get("Title"),
        "place": event.get("Venue") or address or "Omaha, NE",
        "start": start,
        # All-day events start at midnight; show only the date for those
        "show_time": start is not None and (start.hour, start.minute) != (0, 0),
        "category": group,
        "image": images[index_in_group % len(images)],
        "label_class": label_class,
    }


def upcoming_events(lat, lon):
    """Upcoming events near (lat, lon) as card dicts. Cached; returns [] if the API fails."""
    cache_key = f"home-events:{lat}:{lon}"
    cards = cache.get(cache_key)
    if cards is not None:
        return cards
    try:
        events = Events().get_event(PREDICTHQ_CATEGORIES, SEARCH_RADIUS_MILES, "mi", "Omaha", 0, lat=lat, lon=lon)
    except Exception:
        logger.exception("Could not load events from PredictHQ")
        return []
    cards = []
    seen_per_group = {}
    for event in events[:MAX_CARDS]:
        group = CATEGORY_GROUPS.get(event.get("Category"), "Others")
        cards.append(_to_card(event, seen_per_group.get(group, 0)))
        seen_per_group[group] = seen_per_group.get(group, 0) + 1
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
