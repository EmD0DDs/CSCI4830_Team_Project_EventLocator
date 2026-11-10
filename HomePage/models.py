from django.conf import settings
from django.db import models

# Create your models here.
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.PROTECT,
        related_name="events",
    )
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    age_req = models.IntegerField()
    description = models.TextField()
    price = models.FloatField()
    validation = models.BooleanField()


    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=255)

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
