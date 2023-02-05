from car_spec_app.views import BaseBondedCarView
from models import DealerCarParkModel, SellerCarParkModel
from root.common.permissions import IsDealer, IsOwnerOrAdmin, IsVerified
from serializers import DealerCarParkSerializer, SellersCarParkSerializer


class DealerAutoParkView(BaseBondedCarView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    filter_add_data = 'dealer'


class SellerAutoParkView(BaseBondedCarView):
    permission_classes = [IsDealer & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    filter_add_data = 'seller'
