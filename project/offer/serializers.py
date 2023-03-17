# pylint: skip-file

from decimal import Decimal

from rest_framework.serializers import ModelSerializer, ValidationError

from .models import OfferModel


class OffersSerializer(ModelSerializer):
    class Meta:
        model = OfferModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'

    def validate_max_price(self, max_price):
        buyer = self.context.get('creator')
        if buyer:
            if not buyer.balance:
                raise ValidationError("You should have balance to create an offer")
            if Decimal(max_price) > Decimal(buyer.balance):
                raise ValidationError("You do not have enough balance to "
                                      "buy car on specified price")
        return max_price
