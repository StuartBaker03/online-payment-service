from decimal import Decimal
import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, OperationalError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DirectPaymentForm, RequestPaymentForm
from .models import UserAccount, DirectPayment, RequestPayment
from . import models

@login_required
def home(request):
    accountDetails = UserAccount.objects.get(user=request.user)
    #Details for notifications
    requests_pending = RequestPayment.objects.filter(requested_from=request.user, current_status="PENDING").order_by(
        "-transaction_created_at")
    recent_payments_received = DirectPayment.objects.filter(receiver=request.user).order_by("-transaction_created_at")[:3]
    return render(request, 'payapp/home.html', {'accountDetails': accountDetails, "requests_pending":
                                                        requests_pending, "recent_payments_received": recent_payments_received})

@login_required
def direct_payment(request):
    accountDetails = UserAccount.objects.get(user=request.user)
    if request.method == "POST":
        form = DirectPaymentForm(request.POST)

        if form.is_valid():
            receiver_email = form.cleaned_data['receiver_email']
            amount_to_transfer = form.cleaned_data["amount_to_transfer"]

            try:
                receiver_user = User.objects.get(email=receiver_email)

                if request.user == receiver_user:
                    messages.error(request, "You cannot transfer money to yourself.")
                    return render(request, "payapp/directpayment.html", {"form": form})

                with transaction.atomic():
                    src_account = UserAccount.objects.select_for_update().get(user=request.user)
                    dst_account = UserAccount.objects.select_for_update().get(user=receiver_user)

                    if src_account.balance < amount_to_transfer:
                        messages.error(request, "You have insufficient funds.")
                        return render(request, "payapp/directpayment.html", {"form": form})

                    if amount_to_transfer <= 0:
                        messages.error(request, "Your transfer amount must be greater than zero.")
                        return render(request, "payapp/directpayment.html", {"form": form})

                    #If both users use the same currency, no conversion necessary
                    if src_account.currency == dst_account.currency:
                        converted_amount = amount_to_transfer
                    #If users have different currencies, use RESTful service
                    else:
                        #Added protocol and webhost as conversion doesn't work for https if it is http, and vice versa
                        protocol = request.scheme
                        webhost = request.get_host()
                        conversion_url = (f"{protocol}://{webhost}/webapps2026/conversion/{src_account.currency}/"
                                          f"{dst_account.currency}/{amount_to_transfer}/")
                        response = requests.get(conversion_url, timeout=10, verify=False)

                        if response.status_code != 200:
                            messages.error(request, "Conversion unsuccessful.")
                            return render(request, "payapp/directpayment.html", {"form": form,
                                                                                 "accountDetails": accountDetails,})

                        conversion_data = response.json()
                        converted_amount = Decimal(conversion_data["converted_amount"])

                    src_account.balance -= amount_to_transfer
                    dst_account.balance += converted_amount

                    src_account.save()
                    dst_account.save()

                    DirectPayment.objects.create(sender=request.user, sender_currency=src_account.currency, receiver=receiver_user,
                                                 receiver_currency=dst_account.currency, amount_sent=amount_to_transfer,
                                                 amount_received=converted_amount)

                messages.success(request, "Payment successful.")
                return redirect("home")

            except User.DoesNotExist:
                messages.error(request, "Receiver email does not exist.")
            except models.UserAccount.DoesNotExist:
                messages.error(request, "One or both users not found.")
            except OperationalError:
                messages.error(request, "Direct payment operation is not possible now.")
            except KeyError:
                messages.error(request, "Conversion unsuccessful.")
            except requests.RequestException:
                messages.error(request, "Conversion connection unsuccessful.")

    else:
        form = DirectPaymentForm()

    return render(request, "payapp/directpayment.html", {"form": form,
                                                         "accountDetails": accountDetails,})

@login_required
def payment_history(request):
    accountDetails = UserAccount.objects.get(user=request.user)
    sent_payments = DirectPayment.objects.filter(sender=request.user).order_by("-transaction_created_at")
    received_payments = DirectPayment.objects.filter(receiver=request.user).order_by("-transaction_created_at")

    return render(request, "payapp/paymenthistory.html", {"accountDetails": accountDetails,
                                                          "sent_payments": sent_payments, "received_payments": received_payments,})


@login_required
def request_payment(request):
    accountDetails = UserAccount.objects.get(user=request.user)
    if request.method == "POST":
        form = RequestPaymentForm(request.POST)

        if form.is_valid():
            receiver_email = form.cleaned_data['receiver_email']
            amount_to_receive = form.cleaned_data["amount_to_transfer"]

            try:
                receiver_user = User.objects.get(email=receiver_email)

                if request.user == receiver_user:
                    messages.error(request, "You cannot request money from yourself.")
                    return render(request, "payapp/requestpayment.html", {"form": form,
                                                                          "accountDetails": accountDetails,})

                receiver_account = UserAccount.objects.get(user=receiver_user)

                # If both users use the same currency, no conversion necessary
                if accountDetails.currency == receiver_account.currency:
                    amount_to_send = amount_to_receive
                # If users have different currencies, use RESTful service
                else:
                    # Add protocol and webhost as conversion doesn't work for https if it is http, and vice versa
                    protocol = request.scheme
                    webhost = request.get_host()
                    conversion_url = (f"{protocol}://{webhost}/webapps2026/conversion/{accountDetails.currency}/"
                                      f"{receiver_account.currency}/{amount_to_receive}/")
                    response = requests.get(conversion_url, timeout=10, verify=False)

                    if response.status_code != 200:
                        messages.error(request, "Conversion unsuccessful.")
                        return render(request, "payapp/requestpayment.html", {"form": form,
                                                                              "accountDetails": accountDetails,})

                    conversion_data = response.json()
                    amount_to_send = Decimal(conversion_data["converted_amount"])

                RequestPayment.objects.create(requester=request.user, requester_currency=accountDetails.currency,
                                              requested_from=receiver_user, requested_from_currency=receiver_account.currency,
                                              amount_to_send=amount_to_send, amount_to_receive=amount_to_receive,
                                              current_status="PENDING")

                messages.success(request, "Payment request successfully sent.")
                return redirect("home")

            except User.DoesNotExist:
                messages.error(request, "Receiver email does not exist.")
            except models.UserAccount.DoesNotExist:
                messages.error(request, "One or both users not found.")
            except KeyError:
                messages.error(request, "Conversion unsuccessful.")
            except requests.RequestException:
                messages.error(request, "Conversion connection unsuccessful.")

    else:
        form = RequestPaymentForm()

    return render(request, "payapp/requestpayment.html", {"form": form,
                                                         "accountDetails": accountDetails,})


@login_required
def request_history(request):
    accountDetails = UserAccount.objects.get(user=request.user)
    sent_requests = RequestPayment.objects.filter(requester=request.user).order_by("-transaction_created_at")
    received_requests = RequestPayment.objects.filter(requested_from=request.user).order_by("-transaction_created_at")

    return render(request, "payapp/requesthistory.html", {"accountDetails": accountDetails,
                                                          "sent_requests": sent_requests, "received_requests": received_requests,})


@login_required
def accept_request(request, request_id):
    try:
        requested_payment = RequestPayment.objects.get(id=request_id, requested_from=request.user)
        if requested_payment.current_status != "PENDING":
            messages.error(request, "This request has already been handled.")
            return redirect("request_history")

        with transaction.atomic():
            requester = UserAccount.objects.select_for_update().get(user=requested_payment.requester)
            requested_from = UserAccount.objects.select_for_update().get(user=request.user)

            if requested_from.balance < requested_payment.amount_to_send:
                messages.error(request, "You have insufficient funds.")
                return redirect("request_history")

            requested_from.balance -= requested_payment.amount_to_send
            requester.balance += requested_payment.amount_to_receive

            requested_from.save()
            requester.save()

            DirectPayment.objects.create(sender=request.user, sender_currency=requested_payment.requested_from_currency,
                                         receiver=requested_payment.requester, receiver_currency=requested_payment.requester_currency,
                                         amount_sent=requested_payment.amount_to_send, amount_received=requested_payment.amount_to_receive,)

            requested_payment.current_status = "ACCEPTED"
            requested_payment.save()
        messages.success(request, "Successfully Accepted Requested Payment.")

    except RequestPayment.DoesNotExist:
        messages.error(request, "Request does not exist.")
    except UserAccount.DoesNotExist:
        messages.error(request, "One or both users not found.")
    except OperationalError:
        messages.error(request, "Could not manage request right now.")

    return redirect("request_history")


@login_required
def reject_request(request, request_id):
    try:
        requested_payment = RequestPayment.objects.get(id=request_id, requested_from=request.user)
        if requested_payment.current_status == "PENDING":
            requested_payment.current_status = "REJECTED"
            requested_payment.save()
            messages.success(request, "Successfully Rejected Requested Payment.")
        else:
            messages.error(request, "This request has already been handled.")

    except RequestPayment.DoesNotExist:
        messages.error(request, "Request does not exist.")

    return redirect("request_history")