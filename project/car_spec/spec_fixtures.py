# pylint: disable=unused-argument

"""This module contains fixtures for car_spec tests"""


import uuid
from datetime import timedelta
from random import choice, randint, sample

import pytest
from car_market.models import MarketAvailableCarModel
from car_park.models import SellerCarParkModel
from car_spec.models import DealerSearchCarSpecificationModel
from discount.models import RegularCustomerDiscountLevelsModel
from django.utils import timezone
from promo.models import SellerPromoModel
from pytest import FixtureRequest
from user.models import AutoDealerModel, AutoSellerModel, CustomUserModel

from .models import DealerSuitableCarModel
from .serializers import DealerSearchCarSpecificationsSerializer


@pytest.fixture(scope='function', name='spec_data')
def create_spec_data() -> dict:
    """Creates and returns dict of required car_specification data"""
    spec_data = {
        "transmission": choice(['MANUAL', 'AUTO', 'ROBOTIC']),
        "body_type": choice(["COUPE", "SEDAN", "HATCHBACK", "SUV", "MINIVAN"]),
        "engine_fuel_type": choice(['GASOLINE', 'DIESEL', 'GAS']),
        "engine_volume": choice([1.2, 1.6, 3.2, 4.0, 5.0]),
        "drive_unit": choice(["FRONT", "BACK", "FULL"]),
        "safe_controls": choice([True, False]),
        "parking_help": choice([True, False]),
        "climate_controls": choice([True, False]),
        "multimedia": choice([True, False]),
        "additional_safety": choice([True, False]),
        "other_additions": choice([True, False]),
        "color": choice(['red', 'green', 'blue', 'black', 'white']),
        "min_year_of_production": randint(1990, 2010)
    }
    return spec_data


@pytest.fixture(scope='function', name='spec')
def create_spec(all_profiles: dict, spec_data: dict) -> dict[str,
                                                             dict |
                                                             DealerSearchCarSpecificationModel]:
    """Creates db record of dealer search car specification, returns dict
    of created car specification instance and it's creation data"""
    dealer = all_profiles['dealer']['profile_instance']
    spec_data['dealer'] = dealer
    created_spec = DealerSearchCarSpecificationModel.objects.create(**spec_data)
    created_spec_data = DealerSearchCarSpecificationsSerializer(created_spec).data
    spec = {"spec_data": created_spec_data,
            "spec_instance": created_spec}
    return spec


@pytest.fixture(scope='function', name='suit_cars')
def add_suitable_cars(spec: dict, cars: list) -> dict[str,
                                                      AutoDealerModel |
                                                      list[MarketAvailableCarModel]]:
    """Creates db record of dealer suitable cars, adds all cars from market available
     cars to dealer suitable cars list, returns list of dicts of dealer instance and
     his suitable cars"""
    dealer = spec['spec_instance'].dealer
    suit_cars = DealerSuitableCarModel.objects.create(dealer=dealer)
    added_cars = {'dealer': dealer,
                  'cars': []}
    for car in cars:
        suit_cars.car_model.add(car)
        added_cars['cars'].append(car)
    return added_cars


@pytest.fixture(scope='function', name='many_cars')
def create_many_cars():
    """Creates lots of car model instances (50 000) for celery tasks test
    purposes, do not return values, just fills up the database"""
    cars_data = []
    for _ in range(50000):
        car_data = {
            "brand_name": choice(['Mesla', 'PulseWagen', 'Meely', 'Konda',
                                  'Pissan', 'Laudi', 'Koyota', 'Peat']),
            "car_model_name": choice(['Carbon', 'Leman', 'Turtle', 'Rabbit', 'Hobbit',
                                      'Bilbo', 'Jinnie', 'Mini', 'Cat', 'Bug', 'Slug']),
            "year_of_production": randint(1990, 2023),
            "transmission": choice(['MANUAL', 'AUTO', 'ROBOTIC']),
            "body_type": choice(["COUPE", "SEDAN", "HATCHBACK", "SUV", "MINIVAN"]),
            "engine_fuel_type": choice(['GASOLINE', 'DIESEL', 'GAS']),
            "engine_volume": choice([1.2, 1.6, 3.2, 4.0, 5.0]),
            "drive_unit": choice(["FRONT", "BACK", "FULL"]),
            "safe_controls": choice([True, False]),
            "parking_help": choice([True, False]),
            "climate_controls": choice([True, False]),
            "multimedia": choice([True, False]),
            "additional_safety": choice([True, False]),
            "other_additions": choice([True, False]),
            "color": choice(['red', 'green', 'blue', 'black', 'white']),
            'demand_level': randint(0, 100)
        }
        cars_data.append(MarketAvailableCarModel(**car_data))
    MarketAvailableCarModel.objects.bulk_create(cars_data)
    cars_data = []
    for _ in range(50000):
        car_data = {
            "brand_name": choice(['Mesla', 'PulseWagen', 'Meely', 'Konda',
                                  'Pissan', 'Laudi', 'Koyota', 'Peat']),
            "car_model_name": choice(['Carbon', 'Leman', 'Turtle', 'Rabbit', 'Hobbit',
                                      'Bilbo', 'Jinnie', 'Mini', 'Cat', 'Bug', 'Slug']),
            "year_of_production": randint(1990, 2023),
            "transmission": choice(['MANUAL', 'AUTO', 'ROBOTIC']),
            "body_type": choice(["COUPE", "SEDAN", "HATCHBACK", "SUV", "MINIVAN"]),
            "engine_fuel_type": choice(['GASOLINE', 'DIESEL', 'GAS']),
            "engine_volume": choice([1.2, 1.6, 3.2, 4.0, 5.0]),
            "drive_unit": choice(["FRONT", "BACK", "FULL"]),
            "safe_controls": choice([True, False]),
            "parking_help": choice([True, False]),
            "climate_controls": choice([True, False]),
            "multimedia": choice([True, False]),
            "additional_safety": choice([True, False]),
            "other_additions": choice([True, False]),
            "color": choice(['red', 'green', 'blue', 'black', 'white']),
            'demand_level': randint(0, 100)
        }
        cars_data.append(MarketAvailableCarModel(**car_data))
    MarketAvailableCarModel.objects.bulk_create(cars_data)


@pytest.fixture(scope='function', name='dealers_and_specs')
def create_dealers_and_their_specs(many_cars: FixtureRequest):
    """Creates auto dealer and their specifications instances, for celery tasks
    test purposes, do not return values, just fills up the database"""
    for _ in range(100):
        user_data = {
            "username": f"test{uuid.uuid4().hex}",
            "password": f"pass{uuid.uuid4().hex}",
            "email": f"test{uuid.uuid4().hex}@am.com",
            "user_type": "DEALER",
            "is_verified": True
        }
        user = CustomUserModel.objects.create_user(**user_data)
        dealer_profile_data = {
            "name": f"tdealer{uuid.uuid4().hex}",
            "home_country": "AL",
            "user": user,
            "balance": 1000000
        }
        dealer = AutoDealerModel.objects.create(**dealer_profile_data)
        spec_data = {
            "transmission": choice(['MANUAL', 'AUTO', 'ROBOTIC']),
            "body_type": choice(["COUPE", "SEDAN", "HATCHBACK", "SUV", "MINIVAN"]),
            "engine_fuel_type": choice(['GASOLINE', 'DIESEL', 'GAS']),
            "engine_volume": choice([1.2, 1.6, 3.2, 4.0, 5.0]),
            "drive_unit": choice(["FRONT", "BACK", "FULL"]),
            "safe_controls": choice([True, False]),
            "parking_help": choice([True, False]),
            "climate_controls": choice([True, False]),
            "multimedia": choice([True, False]),
            "additional_safety": choice([True, False]),
            "other_additions": choice([True, False]),
            "color": choice(['red', 'green', 'blue', 'black', 'white']),
            "min_year_of_production": randint(1990, 2000),
            "dealer": dealer
        }
        DealerSearchCarSpecificationModel.objects.create(**spec_data)


@pytest.fixture(scope='function', name='min_spec_data')
def create_new_dealer_and_generate_minimal_spec_data():
    """Creates another dealer instance and his potential specifications data with
    minimal car requirements, for celery tasks test purposes, returns created specification
    serialized data"""
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": "DEALER",
        "is_verified": True
    }
    user = CustomUserModel.objects.create_user(**user_data)
    dealer_profile_data = {
        "name": f"tdealer{uuid.uuid4().hex}",
        "home_country": "AL",
        "user": user,
        "balance": 1000000
    }
    dealer = AutoDealerModel.objects.create(**dealer_profile_data)
    minimal_spec_data = {
        "transmission": 'MANUAL',
        "body_type": "COUPE",
        "engine_fuel_type": 'GASOLINE',
        "engine_volume": 1.2,
        "drive_unit": "FRONT",
        "safe_controls": False,
        "parking_help": False,
        "climate_controls": False,
        "multimedia": False,
        "additional_safety": False,
        "other_additions": False,
        "color": 'white',
        "min_year_of_production": 1990,
        "dealer": dealer
    }
    min_spec = DealerSearchCarSpecificationModel.objects.create(**minimal_spec_data)
    min_spec_data = DealerSearchCarSpecificationsSerializer(min_spec).data
    return min_spec_data


@pytest.fixture(scope='function', name='sellers_parks_discounts')
def create_sellers_seller_car_parks_and_discounts(many_cars: FixtureRequest):
    """Creates sellers, their discounts and car park instances, for celery tasks
    test purposes, do not return values, just fills up the database"""
    car_ids = list(MarketAvailableCarModel.objects.values_list('id', flat=True))
    for _ in range(100):
        user_data = {
            "username": f"test{uuid.uuid4().hex}",
            "password": f"pass{uuid.uuid4().hex}",
            "email": f"test{uuid.uuid4().hex}@am.com",
            "user_type": "SELLER",
            "is_verified": True
        }
        user = CustomUserModel.objects.create_user(**user_data)
        seller_profile_data = {
            "name": f"tseller{uuid.uuid4().hex}",
            "year_of_creation": randint(1000, 2023),
            "user": user
        }
        seller = AutoSellerModel.objects.create(**seller_profile_data)
        if int(seller.id) % 5 == 0:
            discount_map = {randint(1, 9): randint(3, 10),
                            randint(10, 25): randint(11, 15),
                            randint(30, 70): randint(20, 30)}
            discount_data = {'seller': seller,
                             'purchase_number_discount_map': discount_map}
            RegularCustomerDiscountLevelsModel.objects.create(**discount_data)
        for _ in range(100):
            car_id = choice(car_ids)
            park_data = {
                "car_model": MarketAvailableCarModel.objects.get(id=car_id),
                "available_number": 100000,
                "car_price": randint(1400, 15000),
                "seller": seller
            }
            SellerCarParkModel.objects.create(**park_data)


@pytest.fixture(scope='function', name='seller_promos')
def create_seller_promos(sellers_parks_discounts: FixtureRequest):
    """Creates seller promo instances, for celery tasks test
    purposes, do not return values, just fills up the database"""
    dealers = list(AutoDealerModel.objects.all())
    for seller in sample(list(AutoSellerModel.objects.all()), 25):
        promo_data = {
            "promo_name": f"promo{uuid.uuid4().hex}",
            "promo_description": "This promo is a test promo",
            "start_date": timezone.now(),
            "end_date": (timezone.now() + timedelta(days=5)),
            "discount_size": choice([3, 5, 10, 15, 20]),
            "creator": seller
        }
        seller_promo = SellerPromoModel.objects.create(**promo_data)
        seller_promo.promo_aims.add(*sample(dealers, 40))
        car_parks = list(SellerCarParkModel.objects.filter(seller=seller))
        seller_promo.promo_cars.add(*sample(car_parks, 40))
