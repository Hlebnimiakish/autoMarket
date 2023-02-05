from django.db import models
from django.db.models import (CharField, DateTimeField, DecimalField,
                              ManyToManyField, OneToOneField, TextField)
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
    promo_aims: ManyToManyField = ManyToManyField('user_app.CarBuyerModel')
    promo_cars: ManyToManyField = ManyToManyField('car_park_app.DealerCarParkModel')
    creator: OneToOneField = OneToOneField('user_app.AutoDealerModel', on_delete=models.CASCADE)


class SellerPromoModel(BasePromoModel):
    promo_cars: ManyToManyField = ManyToManyField('car_park_app.SellerCarParkModel')
    promo_aims: ManyToManyField = ManyToManyField('user_app.AutoDealerModel')
    creator: OneToOneField = OneToOneField('user_app.AutoSellerModel', on_delete=models.CASCADE)
