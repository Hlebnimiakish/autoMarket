# pylint: skip-file

import pytest

from .models import DealerSuitableCarModel, DealerSuitableSellerModel
from .tasks import (task_find_suit_cars_for_all_dealers,
                    task_find_suit_cars_for_dealer, task_find_suitable_sellers)

pytestmark = pytest.mark.django_db(transaction=True)


def test_task_all_dealers_suitable_cars_search(dealers_and_specs,
                                               many_cars,
                                               celery_app,
                                               celery_worker):
    suit_cars = DealerSuitableCarModel.objects.all()
    assert not bool(suit_cars)
    task_find_suit_cars_for_all_dealers.delay()
    suit_cars = DealerSuitableCarModel.objects.all()
    assert bool(suit_cars)


def test_task_dealer_suitable_cars_search(many_cars,
                                          min_spec_data,
                                          celery_app,
                                          celery_worker,
                                          client):
    dealer_id = min_spec_data['dealer']
    suit_cars = DealerSuitableCarModel.objects.filter(dealer_id=dealer_id)
    assert not bool(suit_cars)
    task_find_suit_cars_for_dealer.delay(min_spec_data)
    suit_car = DealerSuitableCarModel.objects.get(dealer_id=dealer_id)
    assert suit_car.car_model


def test_task_find_suitable_sellers_for_dealers(sellers_parks_discounts,
                                                dealers_and_specs,
                                                celery_app,
                                                celery_worker):
    suit_sellers = DealerSuitableSellerModel.objects.all()
    assert not bool(suit_sellers)
    task_find_suit_cars_for_all_dealers()
    task_find_suitable_sellers.delay()
    suit_sellers = DealerSuitableSellerModel.objects.all()
    assert bool(suit_sellers)
