from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Event, Bookmark


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "date", "time", "category", "visibility", "validation")
    list_filter = ("category", "visibility", "validation", "date")
    search_fields = ("name", "description", "location", "host__username")
    list_editable = ("validation",)  # tick events as approved straight from the list
    ordering = ("date", "time")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "event")
    search_fields = ("user__username", "event__name")