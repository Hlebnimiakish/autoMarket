# pylint: skip-file

from rest_framework.serializers import (CharField, DictField, ModelSerializer,
                                        ValidationError)

from .models import (CurrentDiscountLevelPerDealerModel,
                     RegularCustomerDiscountLevelsModel)


class RegularCustomerDiscountLevelsSerializer(ModelSerializer):
    purchase_number_discount_map = DictField()

    class Meta:
        model = RegularCustomerDiscountLevelsModel
        fields = ['id', 'seller', 'purchase_number_discount_map']
        read_only_fields = ['is_active', 'seller']

    def validate_purchase_number_discount_map(self, discount_map):
        for key in discount_map.keys():
            try:
                int(key)
            except ValueError:
                raise ValidationError("Purchase numbers must be numeric (integer to string)"
                                      ": '<integer value>' or integer: <integer value>")
        for value in discount_map.values():
            if not isinstance(value, int):
                raise ValidationError("Discount size must be integer: <integer value>")
        return discount_map


class CurrentDiscountLevelPerDealerSerializer(ModelSerializer):
    seller_name: CharField = CharField(source='seller.name')
    dealer_name: CharField = CharField(source='dealer.name')

    class Meta:
        model = CurrentDiscountLevelPerDealerModel
        fields = ['id', 'seller_name', 'dealer_name',
                  'current_discount', 'current_purchase_number']
        read_only_fields = ['seller_name', 'dealer_name',
                            'current_discount', 'current_purchase_number']
