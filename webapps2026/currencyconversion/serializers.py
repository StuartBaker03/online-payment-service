#No model to base it off, so create the model in here
from rest_framework import serializers

class CurrencyConversionSerializer(serializers.Serializer):
    currency1 = serializers.CharField(required=True)
    currency2 = serializers.CharField(required=True)
    conversion_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_of_currency1 = serializers.DecimalField(max_digits=10, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=10, decimal_places=2)