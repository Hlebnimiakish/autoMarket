# pylint: skip-file

from django.db import models
from django.db.models import DecimalField, ForeignKey
from root.common.models import BaseModel


class OfferModel(BaseModel):
    max_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    car_model: ForeignKey = ForeignKey('car_market.MarketAvailableCarModel',
                                       on_delete=models.CASCADE)
    creator: ForeignKey = ForeignKey('user.CarBuyerModel', on_delete=models.CASCADE)
