from rest_framework.serializers import ModelSerializer
from user_app.models import (AutoDealerModel, AutoSellerModel,
                             CarBuyerHistoryModel, CarBuyerModel,
                             CustomUserModel, DealerCarParkModel,
                             DealerPromoModel, DealerSalesHistoryModel,
                             DealerSearchCarSpecificationModel,
                             DealerSuitableCarModel, MarketAvailableCarModel,
                             OfferModel, SellerCarParkModel, SellerPromoModel,
                             SellerSalesHistoryModel)


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ['id', 'email', 'password', 'username', 'user_type', 'is_verified']
        read_only_fields = ['is_verified']
        extra_kwargs = {'password': {'write_only': True}}


class AutoDealerSerializer(ModelSerializer):
    class Meta:
        model = AutoDealerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}


class AutoDealerFrontSerializer(ModelSerializer):
    class Meta:
        model = AutoDealerModel
        exclude = ['balance', 'user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class DealerSearchCarSpecificationsSerializer(ModelSerializer):
    class Meta:
        model = DealerSearchCarSpecificationModel
        fields = '__all__'
        read_only_fields = ['is_active', 'dealer']


class DealerSuitableCarModelsSerializer(ModelSerializer):
    class Meta:
        model = DealerSuitableCarModel
        fields = '__all__'


class MarkerAvailableCarsModelSerializer(ModelSerializer):
    class Meta:
        model = MarketAvailableCarModel
        fields = '__all__'


class DealerCarParkSerializer(ModelSerializer):
    class Meta:
        model = DealerCarParkModel
        fields = '__all__'


class AutoSellersSerializer(ModelSerializer):
    class Meta:
        model = AutoSellerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active', 'clients_number']
        extra_kwargs = {'password': {'write_only': True}}


class AutoSellerFrontSerializer(ModelSerializer):
    class Meta:
        model = AutoSellerModel
        exclude = ['user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class SellersCarParkSerializer(ModelSerializer):
    class Meta:
        model = SellerCarParkModel
        fields = '__all__'


class DealerSalesHistorySerializer(ModelSerializer):
    class Meta:
        model = DealerSalesHistoryModel
        fields = '__all__'


class SellerSalesHistorySerializer(ModelSerializer):
    class Meta:
        model = SellerSalesHistoryModel
        fields = '__all__'


class CarBuyersSerializer(ModelSerializer):
    class Meta:
        model = CarBuyerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}


class CarBuyersFrontSerializer(ModelSerializer):
    class Meta:
        model = CarBuyerModel
        exclude = ['balance', 'user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class CarBuyersHistorySerializer(ModelSerializer):
    class Meta:
        model = CarBuyerHistoryModel
        fields = '__all__'


class OffersSerializer(ModelSerializer):
    class Meta:
        model = OfferModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'


class DealersPromoSerializer(ModelSerializer):
    class Meta:
        model = DealerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'


class SellersPromoSerializer(ModelSerializer):
    class Meta:
        model = SellerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'
