"""This module contains fixtures for sales_history tests"""

import uuid
from datetime import date, timedelta
from random import choice, randint

import pytest
from car_park.models import DealerCarParkModel, SellerCarParkModel
from car_spec.tasks import (task_find_suit_cars_for_all_dealers,
                            task_find_suitable_sellers)
from django.utils import timezone
from promo.models import SellerPromoModel
from pytest import FixtureRequest
from user.models import AutoDealerModel

from .models import (BaseSalesHistoryModel, CarBuyerHistoryModel,
                     DealerSalesHistoryModel, SellerSalesHistoryModel)
from .serializers import (CarBuyersHistorySerializer,
                          DealerSalesHistorySerializer,
                          SellerSalesHistorySerializer)


@pytest.fixture(scope='function', name='history_records')
def create_history_record_for_each_user(car_parks: dict,
                                        all_profiles: dict) -> dict[str,
                                                                    BaseSalesHistoryModel |
                                                                    CarBuyerHistoryModel]:
    """Creates db history record with generated history record data for all user_types,
    returns dict of user_type with his created history record instance"""
    records = {}
    for seller, buyer in {'dealer': 'buyer',
                          'seller': 'dealer'}.items():
        park_owner = {'dealer': car_parks['dealer_park'].dealer,
                      'seller': car_parks['seller_park'].seller}
        models = {'dealer': DealerSalesHistoryModel,
                  'seller': SellerSalesHistoryModel}
        cars_quantity = int(car_parks[f'{seller}_park'].available_number)
        car_price = float(car_parks[f'{seller}_park'].car_price)
        deal_sum = cars_quantity*car_price
        record_data = {
            "date": date.today(),
            "sold_cars_quantity": cars_quantity,
            "selling_price": car_price,
            "deal_sum": deal_sum,
            "sold_car_model": car_parks[f'{seller}_park'],
            "car_buyer": all_profiles[str(buyer)]['profile_instance'],
            str(seller): park_owner[str(seller)]
        }
        record = models[str(seller)].objects.create(**record_data)
        records[str(seller)] = record
    buyer = all_profiles['buyer']['profile_instance']
    cars_quantity = car_parks['dealer_park'].available_number
    car_price = car_parks['dealer_park'].car_price
    record_data = {
        "bought_car_model": car_parks['dealer_park'],
        "auto_dealer": car_parks['dealer_park'].dealer,
        "bought_quantity": cars_quantity,
        "car_price": car_price,
        "deal_sum": cars_quantity * car_price,
        "buyer": buyer,
        "date": date.today()
    }
    record = CarBuyerHistoryModel.objects.create(**record_data)
    records['buyer'] = record
    return records


@pytest.fixture(scope='function', name='dealer_history_record')
def create_additional_dealer_history_record(all_profiles: dict,
                                            cars: list) -> dict[str,
                                                                dict | DealerSalesHistoryModel]:
    """Creates dealer car_park db record with generated data, creates dealer history
    db record with generated data, returns dict of created history record instance with
    it's creation data"""
    park_data = {
        "car_model": choice(list(cars)),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        "dealer": all_profiles['dealer']['profile_instance']
    }
    park = DealerCarParkModel.objects.create(**park_data)
    cars_quantity = int(park.available_number)
    car_price = float(park.car_price)
    deal_sum = cars_quantity * car_price
    record_data = {
            "date": date.today(),
            "sold_cars_quantity": cars_quantity,
            "selling_price": car_price,
            "deal_sum": deal_sum,
            "sold_car_model": park,
            "car_buyer": all_profiles['buyer']['profile_instance'],
            "dealer": all_profiles['dealer']['profile_instance']
        }
    record = DealerSalesHistoryModel.objects.create(**record_data)
    record_data = DealerSalesHistorySerializer(record).data
    return {"record_data": record_data,
            "record_instance": record}


@pytest.fixture(scope='function', name='seller_history_record')
def create_additional_seller_history_record(all_profiles: dict,
                                            cars: list) -> dict[str,
                                                                dict | SellerSalesHistoryModel]:
    """Creates seller car_park db record with generated data, creates seller history
    db record with generated data, returns dict of created history record instance with
    it's creation data"""
    park_data = {
        "car_model": choice(list(cars)),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        "seller": all_profiles['seller']['profile_instance']
    }
    park = SellerCarParkModel.objects.create(**park_data)
    cars_quantity = int(park.available_number)
    car_price = float(park.car_price)
    deal_sum = cars_quantity * car_price
    record_data = {
            "date": date.today(),
            "sold_cars_quantity": cars_quantity,
            "selling_price": car_price,
            "deal_sum": deal_sum,
            "sold_car_model": park,
            "car_buyer": all_profiles['dealer']['profile_instance'],
            "seller": all_profiles['seller']['profile_instance']
        }
    record = SellerSalesHistoryModel.objects.create(**record_data)
    record_data = SellerSalesHistorySerializer(record).data
    return {"record_data": record_data,
            "record_instance": record}


@pytest.fixture(scope='function', name='buyer_history_record')
def create_additional_buyer_history_record(all_profiles: dict,
                                           cars: list) -> dict[str,
                                                               dict | CarBuyerHistoryModel]:
    """Creates dealer car_park db record with generated data, creates buyer history
    db record with generated data, returns dict of created history record instance with
    it's creation data"""
    park_data = {
        "car_model": choice(list(cars)),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        "dealer": all_profiles['dealer']['profile_instance']
    }
    park = DealerCarParkModel.objects.create(**park_data)
    cars_quantity = int(park.available_number)
    car_price = float(park.car_price)
    deal_sum = cars_quantity*car_price
    record_data = {
        "bought_car_model": park,
        "auto_dealer": all_profiles['dealer']['profile_instance'],
        "bought_quantity": cars_quantity,
        "car_price": car_price,
        "deal_sum": deal_sum,
        "buyer": all_profiles['buyer']['profile_instance'],
        "date": date.today()
    }
    record = CarBuyerHistoryModel.objects.create(**record_data)
    record_data = CarBuyersHistorySerializer(record).data
    return {"record_data": record_data,
            "record_instance": record}


@pytest.fixture(scope='function', name='deals_preparations')
def prepare_dealers_for_car_purchase_deals(seller_promos: FixtureRequest):
    """Calls tasks for suitable cars and sellers to be found, for created dealers to
    be ready to participate in car purchase deals for celery tasks test purposes"""
    task_find_suit_cars_for_all_dealers()
    task_find_suitable_sellers()
    return seller_promos


@pytest.fixture(scope='function', name='seller_promos')
def create_seller_promos(control_case_suit_seller: dict):
    """Creates seller promo instances, for celery tasks test
    purposes, do not return values, just fills up the database"""
    dealer_ids = AutoDealerModel.objects.values_list('id', flat=True)
    seller_id = control_case_suit_seller['unsuit_sellers'][0]
    promo_data = {
        "promo_name": f"promo{uuid.uuid4().hex}",
        "promo_description": "This promo is a test promo",
        "start_date": timezone.now(),
        "end_date": (timezone.now() + timedelta(days=5)),
        "discount_size": 25,
        "creator_id": seller_id
    }
    seller_promo = SellerPromoModel.objects.create(**promo_data)
    seller_promo.promo_aims.add(*dealer_ids)
    car_parks = SellerCarParkModel.objects.get(seller_id=seller_id).pk
    seller_promo.promo_cars.add(car_parks)
    return control_case_suit_seller
