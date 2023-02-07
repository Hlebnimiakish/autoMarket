from root.common.permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin,
                                     IsVerified)
from root.common.views import BaseCRUDView, BaseReadOnlyView
from user.models import CarBuyerModel

from .models import OfferModel
from .serializers import OffersSerializer


class OfferForDealerView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = OffersSerializer
    model = OfferModel


class OfferCRUDView(BaseCRUDView):
    permission_classes = [IsBuyer & IsOwnerOrAdmin & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    user_data = 'creator'
    user_model = CarBuyerModel
