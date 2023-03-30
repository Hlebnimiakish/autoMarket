# pylint: skip-file

from django.db import models
from django.db.models import (DateField, DecimalField, ForeignKey,
                              IntegerField, OneToOneField)


class BaseOverallStatisticsModel(models.Model):
    last_analyzed_date: DateField = DateField(null=True, editable=True)

    class Meta:
        abstract = True


class BaseOverallSalesStatisticsModel(BaseOverallStatisticsModel):
    sold_cars_number: IntegerField = IntegerField(default=0)
    total_revenue: DecimalField = DecimalField(default=0, max_digits=20, decimal_places=2)
    avg_sold_car_price: DecimalField = DecimalField(default=0, max_digits=12, decimal_places=2)
    uniq_buyers_number: IntegerField = IntegerField(default=0)
    most_sold_car: ForeignKey = \
        ForeignKey('car_market.MarketAvailableCarModel', on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True


class BaseOverallPurchaseStatisticsModel(BaseOverallStatisticsModel):
    bought_cars_number: IntegerField = IntegerField(default=0)
    total_expenses: DecimalField = DecimalField(default=0, max_digits=20, decimal_places=2)
    avg_bought_car_price: DecimalField = DecimalField(default=0, max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class OverallSellerStatisticsModel(BaseOverallSalesStatisticsModel):
    seller: OneToOneField = OneToOneField('user.AutoSellerModel', on_delete=models.CASCADE)


class OverallDealerStatisticsModel(BaseOverallSalesStatisticsModel,
                                   BaseOverallPurchaseStatisticsModel):
    dealer: OneToOneField = OneToOneField('user.AutoDealerModel', on_delete=models.CASCADE)
    total_profit: DecimalField = DecimalField(default=0, max_digits=20, decimal_places=2)


class OverallBuyerStatisticsModel(BaseOverallPurchaseStatisticsModel):
    buyer: OneToOneField = OneToOneField('user.CarBuyerModel', on_delete=models.CASCADE)
