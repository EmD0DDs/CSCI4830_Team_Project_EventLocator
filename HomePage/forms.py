from django import forms
from .models import Event
from datetime import date

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "category", "visibility"]
    
    def clean_date(self):
        d = self.cleaned_data["date"]
        if d < date.today():
            raise forms.ValidationError("The event date can't be in the past.")
        return d