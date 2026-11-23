from django import forms
from .models import Event
from datetime import date

class EventForm(forms.ModelForm):

    AGE_CHOICES = [(0, "All ages"), (13, "13+"), (16, "16+"), (18, "18+"), (21, "21+")]
    age_req = forms.TypedChoiceField(choices=AGE_CHOICES, coerce=int, initial=0)


    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "price", "age_req", "category", "visibility"]
    
    def clean_date(self):
        d = self.cleaned_data["date"]
        if d < date.today():
            raise forms.ValidationError("The event date can't be in the past.")
        return d

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price can't be negative.")
        return price