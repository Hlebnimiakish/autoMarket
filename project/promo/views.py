from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified)
from root.common.views import BaseCRUDView, BaseReadOnlyView
from user.models import AutoDealerModel, AutoSellerModel

from .models import DealerPromoModel, SellerPromoModel
from .promo_filter import PromoFilterDealer, PromoFilterSeller
from .serializers import DealersPromoSerializer, SellersPromoSerializer


class DealerPromoReadOnlyView(BaseReadOnlyView):
    serializer = DealersPromoSerializer
    model = DealerPromoModel
    filterset_class = PromoFilterDealer
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['discount_size']


class SellerPromoReadOnlyView(BaseReadOnlyView):
    permission_classes = [IsSeller & IsVerified | IsDealer & IsVerified]
    serializer = SellersPromoSerializer
    model = SellerPromoModel
    filterset_class = PromoFilterSeller
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['discount_size']


class DealerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsDealer & IsOwnerOrAdmin & IsVerified]
    serializer = DealersPromoSerializer
    model = DealerPromoModel
    user_data = 'creator'
    user_model = AutoDealerModel
    filterset_class = PromoFilterDealer
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['discount_size']


class SellerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsSeller & IsOwnerOrAdmin & IsVerified]
    serializer = SellersPromoSerializer
    model = SellerPromoModel
    user_data = 'creator'
    user_model = AutoSellerModel
    filterset_class = PromoFilterSeller
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['discount_size']
