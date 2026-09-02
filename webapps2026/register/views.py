from decimal import Decimal
import requests
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
from register.forms import RegisterForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from payapp.models import UserAccount


@csrf_protect
def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            currency  = form.cleaned_data["currency"]

            #Use RESTful service to convert default 'money' into their chosen currency
            try:
                # Add protocol and webhost as conversion doesn't work for https if it is http, and vice versa
                protocol = request.scheme
                webhost = request.get_host()
                conversion_url = f"{protocol}://{webhost}/webapps2026/conversion/GBP/{currency}/500/"
                response = requests.get(conversion_url, timeout=10, verify=False)

                if response.status_code != 200:
                    messages.error(request, "Conversion unsuccessful.")
                    return render(request, "register/register.html", {"form": form})

                conversion_data = response.json()
                converted_amount = Decimal(conversion_data["converted_amount"])

                with transaction.atomic():
                    user = form.save()
                    UserAccount.objects.create(user=user, currency=currency, balance=converted_amount)

                messages.success(request, f"You are now registered as {user.username}.")
                return redirect("login")

            except requests.RequestException:
                messages.error(request, "Conversion connection unsuccessful.")
            except KeyError:
                messages.error(request, "Conversion unsuccessful.")
                return render(request, "register/register.html", {"form": form})

        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.info(request, f"You are now logged in as {user.username}.")
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "register/login.html", {"form": form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")