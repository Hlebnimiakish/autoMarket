from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified)
from root.common.views import BaseCRUDView, BaseReadOnlyView
from user.models import AutoDealerModel, AutoSellerModel

from .models import DealerPromoModel, SellerPromoModel
from .serializers import DealersPromoSerializer, SellersPromoSerializer


class DealerPromoReadOnlyView(BaseReadOnlyView):
    serializer = DealersPromoSerializer
    model = DealerPromoModel


class SellerPromoReadOnlyView(BaseReadOnlyView):
    serializer = SellersPromoSerializer
    model = SellerPromoModel


class DealerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsDealer & IsOwnerOrAdmin & IsVerified]
    serializer = DealersPromoSerializer
    model = DealerPromoModel
    user_data = 'creator'
    user_model = AutoDealerModel


class SellerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsSeller & IsOwnerOrAdmin & IsVerified]
    serializer = SellersPromoSerializer
    model = SellerPromoModel
    user_data = 'creator'
    user_model = AutoSellerModel