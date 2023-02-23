from root.common.permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin,
                                     IsSeller, IsVerified)
from root.common.views import BaseOwnModelReadView
from user.models import AutoDealerModel, AutoSellerModel, CarBuyerModel

from .models import (CarBuyerHistoryModel, DealerSalesHistoryModel,
                     SellerSalesHistoryModel)
from .serializers import (CarBuyersHistorySerializer,
                          DealerSalesHistorySerializer,
                          SellerSalesHistorySerializer)


class SellerSalesHistoryOwnView(BaseOwnModelReadView):
    permission_classes = [IsVerified & IsSeller & IsOwnerOrAdmin]
    model = SellerSalesHistoryModel
    serializer = SellerSalesHistorySerializer
    user_model = AutoSellerModel
    user_type = 'seller'


class DealerSalesHistoryOwnView(BaseOwnModelReadView):
    permission_classes = [IsVerified & IsDealer & IsOwnerOrAdmin]
    model = DealerSalesHistoryModel
    serializer = DealerSalesHistorySerializer
    user_model = AutoDealerModel
    user_type = 'dealer'


class BuyerPurchaseHistoryOwnView(BaseOwnModelReadView):
    permission_classes = [IsVerified & IsBuyer & IsOwnerOrAdmin]
    model = CarBuyerHistoryModel
    serializer = CarBuyersHistorySerializer
    user_model = CarBuyerModel
    user_type = 'buyer'
