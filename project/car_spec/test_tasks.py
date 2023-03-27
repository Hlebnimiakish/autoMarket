# pylint: skip-file

import pytest

from .models import (DealerSearchCarSpecificationModel, DealerSuitableCarModel,
                     DealerSuitableSellerModel)
from .serializers import (DealerSearchCarSpecificationsSerializer,
                          DealerSuitableCarModelsSerializer,
                          DealerSuitableSellerSerializer)
from .tasks import (task_find_suit_cars_for_all_dealers,
                    task_find_suit_cars_for_dealer, task_find_suitable_sellers)

pytestmark = pytest.mark.django_db(transaction=True)


def test_task_all_dealers_suitable_cars_search(celery_app,
                                               celery_worker,
                                               control_case_suit_cars_for_dealer):
    suit_cars = DealerSuitableCarModel.objects.all()
    assert not bool(suit_cars)
    task_find_suit_cars_for_all_dealers.delay()
    suit_cars = DealerSuitableCarModel.objects.all()
    assert bool(suit_cars)
    for case in ['first', 'second']:
        dealer_id = control_case_suit_cars_for_dealer[f'{case}_case']['dealer_id']
        predefined_suit_car_id = control_case_suit_cars_for_dealer[f'{case}_case']['car_id']
        suit_cars_in_case = DealerSuitableCarModel.objects.get(dealer_id=dealer_id)
        cars = DealerSuitableCarModelsSerializer(suit_cars_in_case).data['car_model']
        assert predefined_suit_car_id in cars
        for car in control_case_suit_cars_for_dealer['unsuit_cars_id']:
            assert car not in cars
    dealer_id = control_case_suit_cars_for_dealer['third_case']['dealer_id']
    third_case = DealerSuitableCarModel.objects.get(dealer_id=dealer_id)
    cars = DealerSuitableCarModelsSerializer(third_case).data['car_model']
    assert not cars


def test_task_dealer_suitable_cars_search(control_case_suit_cars_for_dealer,
                                          celery_app,
                                          celery_worker,
                                          client):
    dealer_id = control_case_suit_cars_for_dealer['first_case']['dealer_id']
    suit_cars = DealerSuitableCarModel.objects.get_or_none(dealer_id=dealer_id)
    assert not bool(suit_cars)
    spec = DealerSearchCarSpecificationModel.objects.get(dealer_id=dealer_id)
    spec_data = DealerSearchCarSpecificationsSerializer(spec).data
    task_find_suit_cars_for_dealer.delay(spec_data)
    suit_car = DealerSuitableCarModel.objects.get(dealer_id=dealer_id)
    assert suit_car.car_model
    predefined_suit_car_id = control_case_suit_cars_for_dealer['first_case']['car_id']
    cars = DealerSuitableCarModelsSerializer(suit_car).data['car_model']
    assert predefined_suit_car_id in cars
    for car in control_case_suit_cars_for_dealer['unsuit_cars_id']:
        assert car not in cars


def test_task_find_suitable_sellers_for_dealers(control_case_suit_seller,
                                                celery_app,
                                                celery_worker):
    suit_sellers = DealerSuitableSellerModel.objects.all()
    assert not bool(suit_sellers)
    task_find_suit_cars_for_all_dealers()
    task_find_suitable_sellers.delay()
    suit_sellers = DealerSuitableSellerModel.objects.all()
    assert bool(suit_sellers)
    dealer_id = control_case_suit_seller['dealer_id']
    seller_id = control_case_suit_seller['seller'].pk
    car_model_id = control_case_suit_seller['car_model'].pk
    control_case = DealerSuitableSellerModel.objects.get(dealer_id=dealer_id)
    control_case_data = DealerSuitableSellerSerializer(control_case).data
    assert seller_id in control_case_data["suitable_seller"]
    assert car_model_id in control_case_data["deal_car_models"]
    for seller in control_case_suit_seller['unsuit_sellers']:
        assert seller not in control_case_data["suitable_seller"]
