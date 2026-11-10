from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

SAMPLE_EVENTS = [
    {
        "Title": "Omaha Symphony",
        "Category": "concerts",
        "Venue": "Holland Performing Arts Center",
        "Start_Time": "2026-11-20T19:30:00",
        "Location": "1200 Douglas St, Omaha, NE",
    },
    {
        "Title": "Mavericks Hockey",
        "Category": "sports",
        "Venue": None,
        "Start_Time": "2026-11-21T19:00:00",
        "Location": "Baxter Arena, Omaha, NE",
    },
    {
        "Title": "Holiday Lights Festival",
        "Category": "festivals",
        "Venue": None,
        "Start_Time": "not a date",
        "Location": "Location unavailable",
    },
]


class HomePageEventsTests(TestCase):
    def setUp(self):
        cache.clear()
        user = get_user_model().objects.create_user(username="tester", email="tester@example.com", password="pass12345!")
        self.client.force_login(user)

    @patch("HomePage.views.Events")
    def test_cards_show_api_events(self, MockEvents):
        MockEvents.return_value.get_event.return_value = SAMPLE_EVENTS
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Omaha Symphony")
        self.assertContains(response, "Holland Performing Arts Center")
        self.assertContains(response, "Nov 20, 2026")
        self.assertContains(response, 'data-category="Music"')
        # No venue: falls back to the address
        self.assertContains(response, "Baxter Arena, Omaha, NE")
        # Unknown category goes to Others; bad date is skipped instead of crashing
        self.assertContains(response, 'data-category="Others"')
        self.assertNotContains(response, "sample events")

    @patch("HomePage.views.Events")
    def test_all_day_event_hides_midnight_and_country(self, MockEvents):
        MockEvents.return_value.get_event.return_value = [{
            "Title": "Fall Session",
            "Category": "academic",
            "Venue": None,
            "Start_Time": "2026-12-01T00:00:00",
            "Location": "6001 Dodge St, Omaha, NE 68182, United States of America",
        }]
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Dec 1, 2026")
        self.assertNotContains(response, "12:00 AM")
        self.assertContains(response, "6001 Dodge St, Omaha, NE 68182")
        self.assertNotContains(response, "United States of America")
        self.assertContains(response, "HomePage/images/slides/slide11.jpg")

    @patch("HomePage.views.Events")
    def test_same_category_cards_take_turns_with_pictures(self, MockEvents):
        game = {"Title": "Game", "Category": "sports", "Venue": "Arena", "Start_Time": "2026-12-01T19:00:00", "Location": "Location unavailable"}
        MockEvents.return_value.get_event.return_value = [game, game]
        response = self.client.get(reverse("home"))

        self.assertContains(response, "HomePage/images/Baskeball.jpg", count=1)
        self.assertContains(response, "HomePage/images/slides/slide10.jpg", count=1)

    @patch("HomePage.views.Events")
    def test_api_error_shows_sample_cards(self, MockEvents):
        MockEvents.return_value.get_event.side_effect = Exception("API down")
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "these are sample events")
        self.assertContains(response, "UNO Fall Concert")
        self.assertContains(response, "HomePage/images/omahaFarmersMarket.jpeg")
        self.assertContains(response, 'alt="Concert crowd and illuminated stage"')

    @patch("HomePage.views.Events")
    def test_no_api_events_shows_sample_cards(self, MockEvents):
        MockEvents.return_value.get_event.return_value = []
        response = self.client.get(reverse("home"))

        self.assertContains(response, "UNO Mavericks Home Game")
        self.assertContains(response, "these are sample events")

    @patch("HomePage.views.timezone.localdate")
    @patch("HomePage.views.Events")
    def test_sample_dates_are_always_upcoming(self, MockEvents, mock_today):
        from datetime import date
        mock_today.return_value = date(2026, 11, 12)
        MockEvents.return_value.get_event.side_effect = Exception("API down")
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Nov 15, 2026 · 7:00 PM")
        self.assertContains(response, "Nov 22, 2026 · 10:00 AM")

    @patch("HomePage.views.Events")
    def test_uses_browser_location(self, MockEvents):
        MockEvents.return_value.get_event.return_value = []
        self.client.get(reverse("home"), {"lat": "40.81", "lon": "-96.70"})

        kwargs = MockEvents.return_value.get_event.call_args.kwargs
        self.assertEqual((kwargs["lat"], kwargs["lon"]), (40.81, -96.70))

    @patch("HomePage.views.Events")
    def test_bad_location_falls_back_to_omaha(self, MockEvents):
        MockEvents.return_value.get_event.return_value = []
        self.client.get(reverse("home"), {"lat": "abc", "lon": "-96.70"})

        kwargs = MockEvents.return_value.get_event.call_args.kwargs
        self.assertEqual((kwargs["lat"], kwargs["lon"]), (41.2565, -95.9345))

    @patch("HomePage.views.Events")
    def test_results_are_cached(self, MockEvents):
        MockEvents.return_value.get_event.return_value = SAMPLE_EVENTS
        self.client.get(reverse("home"))
        self.client.get(reverse("home"))

        self.assertEqual(MockEvents.return_value.get_event.call_count, 1)

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
