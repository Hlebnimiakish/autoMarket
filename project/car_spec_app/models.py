from car_market_app.models import BaseAutoSpecificationModel
from django.db import models
from django.db.models import ForeignKey, IntegerField, ManyToManyField
from root.common.models import BaseModel


class DealerSearchCarSpecificationModel(BaseAutoSpecificationModel):
    dealer: ForeignKey = ForeignKey('user_app.AutoDealerModel', on_delete=models.CASCADE)
    min_year_of_production: IntegerField = IntegerField()


class DealerSuitableCarModel(BaseModel):
    dealer: ManyToManyField = ManyToManyField('user_app.AutoDealerModel')
    car_model: ManyToManyField = ManyToManyField('car_market_app.MarketAvailableCarModel')
