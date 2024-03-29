# pylint: skip-file

from django.db import models
from django.db.models import (CharField, DateTimeField, DecimalField,
                              ForeignKey, ManyToManyField, TextField)
from root.common.models import BaseModel


class BasePromoModel(BaseModel):
    promo_name: CharField = CharField(max_length=100)
    promo_description: TextField = TextField()
    start_date: DateTimeField = DateTimeField()
    end_date: DateTimeField = DateTimeField()
    discount_size: DecimalField = DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        abstract = True


class DealerPromoModel(BasePromoModel):
    promo_aims: ManyToManyField = ManyToManyField('user.CarBuyerModel')
    promo_cars: ManyToManyField = ManyToManyField('car_park.DealerCarParkModel')
    creator: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)


class SellerPromoModel(BasePromoModel):
    promo_cars: ManyToManyField = ManyToManyField('car_park.SellerCarParkModel')
    promo_aims: ManyToManyField = ManyToManyField('user.AutoDealerModel')
    creator: ForeignKey = ForeignKey('user.AutoSellerModel', on_delete=models.CASCADE)
