from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    AVAILABLE_CURRENCIES = [("GBP", "Pound Sterling"), ("EUR", "Euro"), ("USD", "US Dollar")]
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(choices=AVAILABLE_CURRENCIES, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name","last_name", "email", "password1", "password2", "currency")

    #Adding to ensure emails are not already in use. Bug found where multiple accounts had same email, causing app to
    #crash during direct payments.
    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email

    def save(self, *args, **kwargs):
        user = super(RegisterForm, self).save(*args, **kwargs)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.save()
        return user