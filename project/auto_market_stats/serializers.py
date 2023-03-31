# pylint: skip-file

from rest_framework.serializers import ModelSerializer

from .models import (OverallBuyerStatisticsModel, OverallDealerStatisticsModel,
                     OverallSellerStatisticsModel)


class OverallDealerStatisticsSerializer(ModelSerializer):
    class Meta:
        model = OverallDealerStatisticsModel
        fields = ["sold_cars_number", "total_revenue", "avg_sold_car_price",
                  "uniq_buyers_number", "most_sold_car", "bought_cars_number",
                  "total_expenses", "avg_bought_car_price", "total_profit"]


class OverallBuyerStatisticsSerializer(ModelSerializer):
    class Meta:
        model = OverallBuyerStatisticsModel
        fields = ["bought_cars_number", "total_expenses", "avg_bought_car_price"]


class OverallSellerStatisticsSerializer(ModelSerializer):
    class Meta:
        model = OverallSellerStatisticsModel
        fields = ["sold_cars_number", "total_revenue", "avg_sold_car_price",
                  "uniq_buyers_number", "most_sold_car"]
