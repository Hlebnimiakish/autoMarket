# pylint: skip-file

from rest_framework.serializers import ModelSerializer, ValidationError

from .models import DealerPromoModel, SellerPromoModel


class BasePromoSerializer(ModelSerializer):
    def validate_discount_size(self, discount_size):
        if discount_size > 100:
            raise ValidationError("Discount can't be more than 100%")
        return discount_size


class DealersPromoSerializer(BasePromoSerializer):
    class Meta:
        model = DealerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'


class SellersPromoSerializer(BasePromoSerializer):
    class Meta:
        model = SellerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'
