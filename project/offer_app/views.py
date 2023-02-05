from models import OfferModel
from root.common.permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin,
                                     IsVerified)
from root.common.views import BaseCRUDView, BaseReadOnlyView
from serializers import OffersSerializer
from user_app.models import CarBuyerModel


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
