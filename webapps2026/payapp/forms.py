from django import forms

#Use Form not ModelForm as doesn't have form for this
class DirectPaymentForm(forms.Form):
    receiver_email = forms.EmailField(label="Receiver's Email Address", required=True)
    amount_to_transfer = forms.DecimalField(label="Amount to Transfer", max_digits=10, decimal_places=2, min_value=0.01)

class RequestPaymentForm(forms.Form):
    receiver_email = forms.EmailField(label="Request-Receiver's Email Address", required=True)
    amount_to_transfer = forms.DecimalField(label="Amount to Request", max_digits=10, decimal_places=2, min_value=0.01)