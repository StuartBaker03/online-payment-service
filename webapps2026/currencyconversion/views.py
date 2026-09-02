from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from currencyconversion.serializers import CurrencyConversionSerializer

#Currency conversions true as of 24/04/2026
CONVERSION_RATES = {
    "EUR": {"EUR": Decimal("1.00"), "GBP": Decimal("0.87"), "USD": Decimal("1.17")},
    "GBP": {"EUR": Decimal("1.15"), "GBP": Decimal("1.00"), "USD": Decimal("1.35")},
    "USD": {"EUR": Decimal("0.86"), "GBP": Decimal("0.74"), "USD": Decimal("1.00")},
}

class CurrencyConversionView(APIView):
    def get(self, request, currency1, currency2, amount_of_currency1):
        #Ensure they are uppercase
        currency1 = currency1.upper()
        currency2 = currency2.upper()

        if currency1 not in CONVERSION_RATES or currency2 not in CONVERSION_RATES[currency1]:
            return Response({"error": "One or both of the currencies are invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        #Ensures amount_of_currency1 is converted to a decimal correctly, so is numbers, not 'abc' for instance
        try:
            amount_of_currency1 = Decimal(amount_of_currency1)
        except InvalidOperation:
            return Response({"error": "Invalid amount."},
                            status=status.HTTP_400_BAD_REQUEST)

        if amount_of_currency1 < Decimal("0.00"):
            return Response({"error": "Cannot be a negative amount."},
                            status=status.HTTP_400_BAD_REQUEST)

        conversion_rate = CONVERSION_RATES[currency1][currency2]
        converted_amount = amount_of_currency1 * conversion_rate

        data = {"currency1": currency1, "currency2": currency2, "conversion_rate": conversion_rate,
                "amount_of_currency1": amount_of_currency1, "converted_amount": converted_amount}

        serializer = CurrencyConversionSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)