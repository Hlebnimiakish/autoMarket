from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified)
from root.common.views import BaseOwnModelReadView, BaseReadOnlyView
from user.models import AutoDealerModel, AutoSellerModel

from .models import DealerCarParkModel, SellerCarParkModel
from .park_filter import DealerParkFilter, SellerParkFilter
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


class DealerAutoParkFrontView(BaseReadOnlyView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    filterset_class = DealerParkFilter
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['available_number', 'car_price']


class SellerAutoParkFrontView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    filterset_class = SellerParkFilter
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['available_number', 'car_price']


class DealerOwnAutoParkReadView(BaseOwnModelReadView):
    permission_classes = [IsDealer & IsVerified & IsOwnerOrAdmin]
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    user_type = 'dealer'
    user_model = AutoDealerModel
    filterset_class = DealerParkFilter
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['available_number', 'car_price']


class SellerOwnAutoParkReadView(BaseOwnModelReadView):
    permission_classes = [IsSeller & IsVerified & IsOwnerOrAdmin]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    user_type = 'seller'
    user_model = AutoSellerModel
    filterset_class = SellerParkFilter
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['available_number', 'car_price']
