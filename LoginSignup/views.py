from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserSignupForm, UserLoginForm

# Create your views here.

def login_signup_view(request):
    login_form = UserLoginForm()
    signup_form = UserSignupForm()
    if request.method == "POST":
        if 'login_submit' in request.POST:
            login_form = UserLoginForm(request, request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('home')
        elif 'signup_submit' in request.POST:
            signup_form = UserSignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('home')
            else:
                print(signup_form.errors)



    return render(request, 'login_signup.html', {
        'login':login_form,
        'signup':signup_form
    })
