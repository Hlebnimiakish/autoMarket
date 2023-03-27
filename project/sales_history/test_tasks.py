# pylint: skip-file

import pytest
from car_park.models import DealerCarParkModel, SellerCarParkModel

from .models import SellerSalesHistoryModel
from .tasks import task_dealer_cars_purchase

pytestmark = pytest.mark.django_db(transaction=True)


def test_task_dealer_cars_purchase(deals_preparations,
                                   celery_app,
                                   celery_worker):
    dealer_parks = DealerCarParkModel.objects.all()
    seller_sales = SellerSalesHistoryModel.objects.all()
    assert not bool(dealer_parks)
    assert not bool(seller_sales)
    seller_id = deals_preparations['unsuit_sellers'][0]
    seller_park = SellerCarParkModel.objects.get(seller_id=seller_id)
    car_number_before_deal = int(seller_park.available_number)
    task_dealer_cars_purchase.delay()
    seller_sales = SellerSalesHistoryModel.objects.all()
    dealer_parks = DealerCarParkModel.objects.all()
    assert bool(dealer_parks)
    assert bool(seller_sales)
    dealer_id = deals_preparations['dealer_id']
    seller_park = SellerCarParkModel.objects.get(seller_id=seller_id)
    car_number_after_deal = int(seller_park.available_number)
    dealer_park = DealerCarParkModel.objects.get(dealer_id=dealer_id)
    assert dealer_park.car_model == seller_park.car_model
    assert car_number_before_deal > car_number_after_deal
    seller_history = SellerSalesHistoryModel.objects.get(seller_id=seller_id)
    assert seller_park == seller_history.sold_car_model
    assert dealer_park.car_model == seller_history.sold_car_model.car_model
