from car_market.models import BaseCarParametersModel
from django.db import models
from django.db.models import ForeignKey, IntegerField, ManyToManyField
from root.common.models import BaseModel


class DealerSearchCarSpecificationModel(BaseCarParametersModel):
    dealer: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)
    min_year_of_production: IntegerField = IntegerField()


class DealerSuitableCarModel(BaseModel):
    dealer: ManyToManyField = ManyToManyField('user.AutoDealerModel')
    car_model: ManyToManyField = ManyToManyField('car_market.MarketAvailableCarModel')
