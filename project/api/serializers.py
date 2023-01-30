from rest_framework import serializers

from user_app.models import CustomUserModel, AutoDealerModel, DealerSearchCarSpecificationModel, \
    MarketAvailableCarModel, DealerSuitableCarModel, DealerCarParkModel, AutoSellerModel, SellerCarParkModel, \
    DealerSalesHistoryModel, SellerSalesHistoryModel, CarBuyerModel, CarBuyerHistoryModel, OfferModel, \
    DealerPromoModel, SellerPromoModel


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ['id', 'email', 'password', 'username', 'user_type', 'is_verified']
        read_only_fields = ['is_verified']
        extra_kwargs = {'password': {'write_only': True}}


class AutoDealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoDealerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}


class AutoDealerFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoDealerModel
        exclude = ['balance', 'user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class DealerSearchCarSpecificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerSearchCarSpecificationModel
        fields = '__all__'
        read_only_fields = ['is_active', 'dealer']


class DealerSuitableCarModelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerSuitableCarModel
        fields = '__all__'


class MarkerAvailableCarsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketAvailableCarModel
        fields = '__all__'


class DealerCarParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerCarParkModel
        fields = '__all__'


class AutoSellersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoSellerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active', 'clients_number']
        extra_kwargs = {'password': {'write_only': True}}


class AutoSellerFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoSellerModel
        exclude = ['user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class SellersCarParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerCarParkModel
        fields = '__all__'


class DealerSalesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerSalesHistoryModel
        fields = '__all__'


class SellerSalesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerSalesHistoryModel
        fields = '__all__'


class CarBuyersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBuyerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}


class CarBuyersFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBuyerModel
        exclude = ['balance', 'user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class CarBuyersHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBuyerHistoryModel
        fields = '__all__'


class OffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'


class DealersPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'


class SellersPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'
