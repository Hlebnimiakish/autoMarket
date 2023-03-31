# pylint: skip-file

import pytest

from .models import (OverallBuyerStatisticsModel, OverallDealerStatisticsModel,
                     OverallSellerStatisticsModel)
from .serializers import (OverallBuyerStatisticsSerializer,
                          OverallDealerStatisticsSerializer,
                          OverallSellerStatisticsSerializer)
from .tasks import (get_buyer_statistics, get_dealer_statistics,
                    get_seller_statistics)

pytestmark = pytest.mark.django_db(transaction=True)


def test_stats_tasks(predefined_stats_data_generator,
                     celery_app,
                     celery_worker):
    get_dealer_statistics.delay()
    dealers_stats = OverallDealerStatisticsModel.objects.all()
    predefined_dealers_stats = predefined_stats_data_generator["predefined_dealer_data"]
    for stat in dealers_stats:
        dealer_id = stat.dealer.pk
        predefined_dealer_stats = predefined_dealers_stats[dealer_id]
        stat_data = OverallDealerStatisticsSerializer(stat).data
        for key, value in stat_data.items():
            assert value == predefined_dealer_stats[key]
    get_seller_statistics.delay()
    sellers_stats = OverallSellerStatisticsModel.objects.all()
    predefined_sellers_stats = predefined_stats_data_generator["predefined_seller_data"]
    for stat in sellers_stats:
        seller_id = stat.seller.pk
        predefined_seller_stats = predefined_sellers_stats[seller_id]
        stat_data = OverallSellerStatisticsSerializer(stat).data
        for key, value in stat_data.items():
            assert value == predefined_seller_stats[key]
    get_buyer_statistics.delay()
    buyers_stats = OverallBuyerStatisticsModel.objects.all()
    predefined_buyers_stats = predefined_stats_data_generator["predefined_buyer_data"]
    for stat in buyers_stats:
        buyer_id = stat.buyer.pk
        predefined_buyer_stats = predefined_buyers_stats[buyer_id]
        stat_data = OverallBuyerStatisticsSerializer(stat).data
        for key, value in stat_data.items():
            assert value == predefined_buyer_stats[key]
