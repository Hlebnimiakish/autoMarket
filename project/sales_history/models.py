from django.db import models
from django.db.models import DateField, DecimalField, ForeignKey, IntegerField
from root.common.models import BaseModel


class BaseSalesHistoryModel(BaseModel):
    date: DateField = DateField(auto_now_add=True)
    buyer: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)
    selling_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    sold_cars_quantity: IntegerField = IntegerField()
    deal_sum: DecimalField = DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerSalesHistoryModel(BaseSalesHistoryModel):
    buyer: ForeignKey = ForeignKey('user.CarBuyerModel', on_delete=models.CASCADE)


class SellerSalesHistoryModel(BaseSalesHistoryModel):
    pass


class CarBuyerHistoryModel(BaseModel):
    bought_car_model: ForeignKey = ForeignKey('car_market.MarketAvailableCarModel',
                                              on_delete=models.CASCADE)
    auto_dealer: ForeignKey = ForeignKey('user.AutoDealerModel',
                                         on_delete=models.CASCADE)
    bought_quantity: IntegerField = IntegerField()
    car_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    deal_sum: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    buyer: ForeignKey = ForeignKey('user.CarBuyerModel', on_delete=models.CASCADE)
    date: DateField = DateField(auto_now_add=True)
