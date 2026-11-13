from django.conf import settings
from django.db import models


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("Music", "Music"),
        ("Sports", "Sports"),
        ("Communication", "Communication"),
        ("Education", "Education"),
        ("Others", "Others"),
    ]
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
    ]

    event_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    age_req = models.IntegerField(default=0)
    description = models.TextField()
    price = models.FloatField(default=0)
    validation = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Others")
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="bookmarked_by",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_bookmark",
            ),
        ]

    def __str__(self):
        return f"{self.user} bookmarked {self.event}"