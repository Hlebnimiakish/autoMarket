from car_spec.views import BaseBondedCarView
from root.common.permissions import IsDealer, IsOwnerOrAdmin, IsVerified

from .models import DealerCarParkModel, SellerCarParkModel
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


class DealerAutoParkView(BaseBondedCarView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    filter_add_data = 'dealer'


class SellerAutoParkView(BaseBondedCarView):
    permission_classes = [IsDealer & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    filter_add_data = 'seller'
