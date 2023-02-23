from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified)
from root.common.views import BaseOwnModelReadView, BaseReadOnlyView
from user.models import AutoDealerModel, AutoSellerModel

from .models import DealerCarParkModel, SellerCarParkModel
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


class DealerAutoParkFrontView(BaseReadOnlyView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel


class SellerAutoParkFrontView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel


class DealerOwnAutoParkReadView(BaseOwnModelReadView):
    permission_classes = [IsDealer & IsVerified & IsOwnerOrAdmin]
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    user_type = 'dealer'
    user_model = AutoDealerModel


class SellerOwnAutoParkReadView(BaseOwnModelReadView):
    permission_classes = [IsSeller & IsVerified & IsOwnerOrAdmin]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    user_type = 'seller'
    user_model = AutoSellerModel
