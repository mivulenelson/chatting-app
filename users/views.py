from django.conf import settings
from django.core.mail import send_mail
from django.db.transaction import commit
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            send_mail(
                f"{user.email}",
                f"Your new user ID is: {request.user.user_id}",
                settings.DEFAULT_FROM_EMAIL,
                (user.email,),
                fail_silently=False
            )
            user.save()
            messages.success(request, "Registration successful! Check your email for your user ID.")
            return redirect("/")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})

def login_user(request):
    if request.method == "POST":
        form = CustomUserChangeForm(instance=request.user.user_id)
        if form.is_valid():
            user = form.save()


def logout_user(request):
    pass

