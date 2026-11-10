from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from HomePage.views import GROUP_CATEGORIES

SAMPLE_EVENTS = [
    {
        "Title": "Omaha Symphony",
        "Category": "concerts",
        "Venue": "Holland Performing Arts Center",
        "Attendance": "1200",
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


def fake_api(events):
    """Stand-in for Events().get_event: returns only the events in the requested categories."""
    def get_event(category, *args, limit=50, **kwargs):
        wanted = category.split(",")
        return [event for event in events if event["Category"] in wanted][:limit]
    return get_event


class HomePageEventsTests(TestCase):
    def setUp(self):
        cache.clear()
        user = get_user_model().objects.create_user(username="tester", email="tester@example.com", password="pass12345!")
        self.client.force_login(user)

    @patch("HomePage.views.Events")
    def test_cards_show_api_events(self, MockEvents):
        MockEvents.return_value.get_event.side_effect = fake_api(SAMPLE_EVENTS)
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
        # Attendance shown with a thousands separator; events without it don't get the line
        self.assertContains(response, "Expected attendance: 1,200", count=1)

    @patch("HomePage.views.Events")
    def test_all_day_event_hides_midnight_and_country(self, MockEvents):
        MockEvents.return_value.get_event.side_effect = fake_api([{
            "Title": "Fall Session",
            "Category": "academic",
            "Venue": None,
            "Start_Time": "2026-12-01T00:00:00",
            "Location": "6001 Dodge St, Omaha, NE 68182, United States of America",
        }])
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Dec 1, 2026")
        self.assertNotContains(response, "12:00 AM")
        self.assertContains(response, "6001 Dodge St, Omaha, NE 68182")
        self.assertNotContains(response, "United States of America")
        self.assertContains(response, "HomePage/images/slides/slide11.jpg")

    @patch("HomePage.views.Events")
    def test_performing_arts_counts_as_music(self, MockEvents):
        MockEvents.return_value.get_event.side_effect = fake_api([{
            "Title": "Lion King Musical", "Category": "performing-arts", "Venue": "Orpheum Theater",
            "Start_Time": "2026-12-01T19:30:00", "Location": "Location unavailable",
        }])
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'data-category="Music"')
        self.assertContains(response, "music-label")

    @patch("HomePage.views.Events")
    def test_same_category_cards_take_turns_with_pictures(self, MockEvents):
        game = {"Title": "Game", "Category": "sports", "Venue": "Arena", "Start_Time": "2026-12-01T19:00:00", "Location": "Location unavailable"}
        MockEvents.return_value.get_event.side_effect = fake_api([game, game])
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
        MockEvents.return_value.get_event.side_effect = fake_api(SAMPLE_EVENTS)
        self.client.get(reverse("home"))
        self.client.get(reverse("home"))

        # One request per category button on the first visit, none on the second
        self.assertEqual(MockEvents.return_value.get_event.call_count, len(GROUP_CATEGORIES))

    @patch("HomePage.views.Events")
    def test_busy_category_does_not_hide_music(self, MockEvents):
        # Like the real Omaha data: lots of community events happening before the only concert
        community = [{"Title": f"Meetup {n}", "Category": "community", "Venue": "Library",
                      "Start_Time": f"2026-11-10T{8 + n:02d}:00:00", "Location": ""} for n in range(10)]
        concert = {"Title": "Late Concert", "Category": "concerts", "Venue": "Slowdown",
                   "Start_Time": "2026-11-11T20:00:00", "Location": ""}
        MockEvents.return_value.get_event.side_effect = fake_api(community + [concert])
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Late Concert")
        self.assertContains(response, 'class="event-card" data-category="Music"', count=1)
        # Only a few cards per category
        self.assertContains(response, 'class="event-card" data-category="Others"', count=3)

    @patch("HomePage.views.Events")
    def test_each_category_asks_for_only_a_few_events(self, MockEvents):
        MockEvents.return_value.get_event.return_value = []
        self.client.get(reverse("home"))

        calls = MockEvents.return_value.get_event.call_args_list
        self.assertEqual(sorted(c.args[0] for c in calls), sorted(GROUP_CATEGORIES.values()))
        self.assertTrue(all(c.kwargs["limit"] == 3 for c in calls))

    @patch("HomePage.views.Events")
    def test_cards_from_all_categories_are_sorted_by_date(self, MockEvents):
        MockEvents.return_value.get_event.side_effect = fake_api(SAMPLE_EVENTS)
        content = self.client.get(reverse("home")).content.decode()

        # Symphony (Nov 20) before Hockey (Nov 21); the festival has no date so it goes last
        self.assertLess(content.index("Omaha Symphony"), content.index("Mavericks Hockey"))
        self.assertLess(content.index("Mavericks Hockey"), content.index("Holiday Lights Festival"))

    @patch("HomePage.views.Events")
    def test_one_failed_category_keeps_the_others_and_is_retried(self, MockEvents):
        working = fake_api(SAMPLE_EVENTS)
        def flaky(category, *args, **kwargs):
            if "sports" in category:
                raise Exception("timeout")
            return working(category, *args, **kwargs)
        MockEvents.return_value.get_event.side_effect = flaky
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Omaha Symphony")
        self.assertNotContains(response, "Mavericks Hockey")
        self.assertNotContains(response, "sample events")
        # Not cached, so the next visit asks again
        self.client.get(reverse("home"))
        self.assertEqual(MockEvents.return_value.get_event.call_count, 2 * len(GROUP_CATEGORIES))

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
