from django.db import models
from django.db.models import DateField, DecimalField, ForeignKey, IntegerField
from root.common.models import BaseModel


class BaseSalesHistoryModel(BaseModel):
    date: DateField = DateField(auto_now_add=True)
    selling_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    sold_cars_quantity: IntegerField = IntegerField()
    deal_sum: DecimalField = DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerSalesHistoryModel(BaseSalesHistoryModel):
    dealer: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)
    sold_car_model: ForeignKey = ForeignKey('car_park.DealerCarParkModel',
                                            on_delete=models.CASCADE)
    car_buyer: ForeignKey = ForeignKey('user.CarBuyerModel', on_delete=models.CASCADE)


class SellerSalesHistoryModel(BaseSalesHistoryModel):
    seller: ForeignKey = ForeignKey('user.AutoSellerModel', on_delete=models.CASCADE)
    sold_car_model: ForeignKey = ForeignKey('car_park.SellerCarParkModel',
                                            on_delete=models.CASCADE)
    car_buyer: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)


class CarBuyerHistoryModel(BaseModel):
    bought_car_model: ForeignKey = ForeignKey('car_park.DealerCarParkModel',
                                              on_delete=models.CASCADE)
    auto_dealer: ForeignKey = ForeignKey('user.AutoDealerModel',
                                         on_delete=models.CASCADE)
    bought_quantity: IntegerField = IntegerField()
    car_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    deal_sum: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    buyer: ForeignKey = ForeignKey('user.CarBuyerModel', on_delete=models.CASCADE)
    date: DateField = DateField(auto_now_add=True)
