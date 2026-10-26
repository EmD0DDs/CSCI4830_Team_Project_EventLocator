from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import EmailInput, TextInput,ModelForm
from .models import User
from django.utils.translation import gettext_lazy as _

class UserSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets ={
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'email': EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            }
        
        labels = {
            'first_name': _("First Name"), 
            'last_name': _("Last Name"), 
            'username': _("Username"), 
            'email': _("Email"),
        }
        help_texts  = {
            'username': ''


        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label=''

        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm your password'})

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label=''
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your username'})
        self.fields['password'].widget.attrs.update({'class': "form-control", 'placeholder': 'Enter your password'})