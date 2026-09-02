from django.urls import path
from .views import CurrencyConversionView


urlpatterns = [
    path("conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/", CurrencyConversionView.as_view(),
         name='conversion'),
]