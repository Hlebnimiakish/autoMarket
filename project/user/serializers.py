from rest_framework.serializers import ModelSerializer

from .models import (AutoDealerModel, AutoSellerModel, CarBuyerModel,
                     CustomUserModel)


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


class AutoSellerSerializer(ModelSerializer):
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


class CarBuyerSerializer(ModelSerializer):
    class Meta:
        model = CarBuyerModel
        fields = '__all__'
        read_only_fields = ['balance', 'user', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}


class CarBuyerFrontSerializer(ModelSerializer):
    class Meta:
        model = CarBuyerModel
        exclude = ['balance', 'user', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}
