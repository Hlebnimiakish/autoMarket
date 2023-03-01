from django.db import models
from django.db.models import DecimalField, ForeignKey, IntegerField
from root.common.models import BaseModel


class BaseCurrentCarParkModel(BaseModel):
    car_model: ForeignKey = ForeignKey('car_market.MarketAvailableCarModel',
                                       on_delete=models.CASCADE)
    available_number: IntegerField = IntegerField()
    car_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerCarParkModel(BaseCurrentCarParkModel):
    dealer: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)


class SellerCarParkModel(BaseCurrentCarParkModel):
    seller: ForeignKey = ForeignKey('user.AutoSellerModel', on_delete=models.CASCADE)
