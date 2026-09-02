from django.contrib.auth.models import User
from django.db import models

class UserAccount(models.Model):
    AVAILABLE_CURRENCIES = [("GBP", "Pound Sterling"), ("EUR", "Euro"), ("USD", "US Dollar")]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=AVAILABLE_CURRENCIES, default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500)

    def __str__(self):
        details = ''
        details += f'Username        : {self.user.username}\n'
        details += f'Currency         : {self.currency}\n'
        details += f'Balance         : {self.balance}\n'
        return details

class DirectPayment(models.Model):
    AVAILABLE_CURRENCIES = [("GBP", "Pound Sterling"), ("EUR", "Euro"), ("USD", "US Dollar")]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    sender_currency = models.CharField(max_length=3, choices=AVAILABLE_CURRENCIES, default='GBP')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    receiver_currency = models.CharField(max_length=3, choices=AVAILABLE_CURRENCIES, default='GBP')
    amount_sent = models.DecimalField(max_digits=10, decimal_places=2)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        details = ''
        details += f'Senders username       : {self.sender}\n'
        details += f'Sender Currency        : {self.sender_currency}\n'
        details += f'Receivers username     : {self.receiver}\n'
        details += f'Receiver Currency      : {self.receiver_currency}\n'
        details += f'Amount Sent            : {self.amount_sent}\n'
        details += f'Amount Received        : {self.amount_received}\n'
        details += f'Transaction Created At : {self.transaction_created_at}\n'
        return details

class RequestPayment(models.Model):
    AVAILABLE_CURRENCIES = [("GBP", "Pound Sterling"), ("EUR", "Euro"), ("USD", "US Dollar")]
    STATUS_OPTIONS = [("ACCEPTED", "Accepted"), ("REJECTED", "Rejected"), ("PENDING", "Pending")]
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requester')
    requester_currency = models.CharField(max_length=3, choices=AVAILABLE_CURRENCIES)
    requested_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_from')
    requested_from_currency = models.CharField(max_length=3, choices=AVAILABLE_CURRENCIES)
    amount_to_send = models.DecimalField(max_digits=10, decimal_places=2)
    amount_to_receive = models.DecimalField(max_digits=10, decimal_places=2)
    current_status = models.CharField(max_length=8, choices=STATUS_OPTIONS, default='PENDING')
    transaction_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        details = ''
        details += f'Requesters username        : {self.requester}\n'
        details += f'Requester Currency         : {self.requester_currency}\n'
        details += f'Requested from username    : {self.requested_from}\n'
        details += f'Requested from Currency    : {self.requested_from_currency}\n'
        details += f'Amount to Send             : {self.amount_to_send}\n'
        details += f'Amount to Receive          : {self.amount_to_receive}\n'
        details += f'Current Status             : {self.current_status}\n'
        details += f'Transaction Created At     : {self.transaction_created_at}\n'
        return details