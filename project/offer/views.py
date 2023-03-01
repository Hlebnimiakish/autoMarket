from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from root.common.permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin,
                                     IsVerified)
from root.common.views import BaseCRUDView, BaseReadOnlyView
from user.models import CarBuyerModel

from .models import OfferModel
from .offer_filter import OfferFilter
from .serializers import OffersSerializer


class OfferForDealerView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    filterset_class = OfferFilter
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['max_price']


class OfferCRUDView(BaseCRUDView):
    permission_classes = [IsBuyer & IsOwnerOrAdmin & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    user_data = 'creator'
    user_model = CarBuyerModel
