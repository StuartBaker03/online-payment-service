from decimal import Decimal

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from payapp.models import UserAccount, DirectPayment, RequestPayment
from payappadmin.forms import RegisterAdminForm


@csrf_protect
@login_required
def admin_home(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorised to view this page.")
        return redirect("home")
    return render(request, "payappadmin/adminhome.html")


@login_required
def admin_view_accounts(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorised to view this page.")
        return redirect("home")
    user_accounts = UserAccount.objects.select_related("user").all()
    return render(request, "payappadmin/viewaccountsadmin.html", {"user_accounts": user_accounts})


@login_required
def admin_view_payments(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorised to view this page.")
        return redirect("home")
    payments = DirectPayment.objects.select_related("sender", "receiver").all().order_by("-transaction_created_at")
    return render(request, "payappadmin/viewpaymentsadmin.html", {"payments": payments})


@login_required
def admin_view_requests(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorised to view this page.")
        return redirect("home")
    requests = RequestPayment.objects.select_related("requester", "requested_from").all().order_by("-transaction_created_at")
    return render(request, "payappadmin/viewrequestsadmin.html", {"requests": requests})


@login_required
def register_admin(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorised to view this page.")
        return redirect("home")
    if request.method == "POST":
        form = RegisterAdminForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data["currency"]

            # Use RESTful service to convert default 'money' into their chosen currency
            try:
                # Add protocol and webhost as conversion doesn't work for https if it is http, and vice versa
                protocol = request.scheme
                webhost = request.get_host()
                conversion_url = f"{protocol}://{webhost}/webapps2026/conversion/GBP/{currency}/500/"
                response = requests.get(conversion_url, timeout=10, verify=False)

                if response.status_code != 200:
                    messages.error(request, "Conversion unsuccessful.")
                    return render(request, "payappadmin/registeradmin.html", {"form": form})

                conversion_data = response.json()
                converted_amount = Decimal(conversion_data["converted_amount"])

                with transaction.atomic():
                    user = form.save()
                    UserAccount.objects.create(user=user, currency=currency, balance=converted_amount)

                messages.success(request, f"You are now registered as {user.username}.")
                return redirect("admin_home")

            except requests.RequestException:
                messages.error(request, "Conversion connection unsuccessful.")
            except KeyError:
                messages.error(request, "Conversion unsuccessful.")
                return render(request, "payappadmin/registeradmin.html", {"form": form})

        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = RegisterAdminForm()

    return render(request, "payappadmin/registeradmin.html", {"form": form})