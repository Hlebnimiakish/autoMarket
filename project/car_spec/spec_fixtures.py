# pylint: disable=unused-argument

"""This module contains fixtures for car_spec tests"""


import uuid
from random import choice, randint

import pytest
from car_market.models import MarketAvailableCarModel
from car_park.models import SellerCarParkModel
from car_spec.models import DealerSearchCarSpecificationModel
from discount.models import RegularCustomerDiscountLevelsModel
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


@pytest.fixture(scope='function', name='dealers_for_control_cases')
def create_dealers_for_control_cases() -> list[AutoDealerModel]:
    """Creates a couple of dealer instances for celery task tests purposes,
    returns list of created dealer instances"""
    dealers = []
    for _ in range(3):
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
        dealers.append(dealer)
    return dealers


@pytest.fixture(scope='function', name='control_case_suit_cars_for_dealer')
def create_control_cases_of_dealer_and_their_spec_suit_cars(dealers_for_control_cases) \
        -> dict[str, dict[str, int] | list[int]]:
    """Creates dealer car specifications for passed in dealers and cars, some of which
    can and some can not match created specification parameters for celery task tests
    purposes, returns dict of dealers and their predefined suitable and unsuitable cars"""
    dealers_suit_cars = {}
    dealers = dealers_for_control_cases
    first_dealer_spec_data = {
        "transmission": 'AUTO',
        "body_type": "SUV",
        "engine_fuel_type": 'DIESEL',
        "engine_volume": 1.6,
        "drive_unit": "FULL",
        "safe_controls": False,
        "parking_help": False,
        "climate_controls": False,
        "multimedia": True,
        "additional_safety": False,
        "other_additions": False,
        "color": 'black',
        "min_year_of_production": 1995,
        "dealer": dealers[0]
    }
    first_spec = \
        DealerSearchCarSpecificationModel.objects.create(**first_dealer_spec_data)
    second_dealer_spec_data = {
        "transmission": 'MANUAL',
        "body_type": "COUPE",
        "engine_fuel_type": 'GASOLINE',
        "engine_volume": 3.2,
        "drive_unit": "FRONT",
        "safe_controls": False,
        "parking_help": True,
        "climate_controls": False,
        "multimedia": False,
        "additional_safety": False,
        "other_additions": False,
        "color": 'white',
        "min_year_of_production": 2020,
        "dealer": dealers[1]
    }
    second_spec = \
        DealerSearchCarSpecificationModel.objects.create(**second_dealer_spec_data)
    third_dealer_spec_data = {
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
        "color": 'green',
        "min_year_of_production": 2030,
        "dealer": dealers[2]
    }
    third_spec = \
        DealerSearchCarSpecificationModel.objects.create(**third_dealer_spec_data)
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_1',
        "year_of_production": 2000,
        "transmission": 'AUTO',
        "body_type": "SUV",
        "engine_fuel_type": 'DIESEL',
        "engine_volume": 2.0,
        "drive_unit": "FULL",
        "safe_controls": False,
        "parking_help": True,
        "climate_controls": False,
        "multimedia": True,
        "additional_safety": False,
        "other_additions": False,
        "color": 'black',
        'demand_level': randint(0, 100)
    }
    suit_first = MarketAvailableCarModel.objects.create(**car_data).pk
    dealers_suit_cars['first_case'] = {"dealer_id": first_spec.dealer.pk,
                                       "car_id": suit_first}
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_2',
        "year_of_production": 2020,
        "transmission": 'MANUAL',
        "body_type": "COUPE",
        "engine_fuel_type": 'GASOLINE',
        "engine_volume": 3.2,
        "drive_unit": "FRONT",
        "safe_controls": False,
        "parking_help": True,
        "climate_controls": False,
        "multimedia": False,
        "additional_safety": True,
        "other_additions": False,
        "color": 'white',
        'demand_level': randint(0, 100)
    }
    suit_second = MarketAvailableCarModel.objects.create(**car_data).pk
    dealers_suit_cars['second_case'] = {"dealer_id": second_spec.dealer.pk,
                                        "car_id": suit_second}
    unsuit_cars = []
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_3',
        "year_of_production": 1990,
        "transmission": 'AUTO',
        "body_type": "SUV",
        "engine_fuel_type": 'DIESEL',
        "engine_volume": 3.2,
        "drive_unit": "FULL",
        "safe_controls": True,
        "parking_help": True,
        "climate_controls": True,
        "multimedia": True,
        "additional_safety": True,
        "other_additions": True,
        "color": 'white',
        'demand_level': randint(0, 100)
    }
    car = MarketAvailableCarModel.objects.create(**car_data)
    unsuit_cars.append(car.pk)
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_3',
        "year_of_production": 2023,
        "transmission": 'ROBOTIC',
        "body_type": "COUPE",
        "engine_fuel_type": 'GASOLINE',
        "engine_volume": 5.0,
        "drive_unit": "FRONT",
        "safe_controls": True,
        "parking_help": True,
        "climate_controls": True,
        "multimedia": True,
        "additional_safety": True,
        "other_additions": True,
        "color": 'white',
        'demand_level': randint(0, 100)
    }
    car = MarketAvailableCarModel.objects.create(**car_data)
    unsuit_cars.append(car.pk)
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_3',
        "year_of_production": 2023,
        "transmission": 'ROBOTIC',
        "body_type": "COUPE",
        "engine_fuel_type": 'GASOLINE',
        "engine_volume": 1.2,
        "drive_unit": "FRONT",
        "safe_controls": True,
        "parking_help": True,
        "climate_controls": True,
        "multimedia": True,
        "additional_safety": True,
        "other_additions": True,
        "color": 'white',
        'demand_level': randint(0, 100)
    }
    car = MarketAvailableCarModel.objects.create(**car_data)
    unsuit_cars.append(car.pk)
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_1',
        "year_of_production": 2000,
        "transmission": 'AUTO',
        "body_type": "SUV",
        "engine_fuel_type": 'DIESEL',
        "engine_volume": 2.0,
        "drive_unit": "FULL",
        "safe_controls": False,
        "parking_help": False,
        "climate_controls": False,
        "multimedia": False,
        "additional_safety": False,
        "other_additions": False,
        "color": 'black',
        'demand_level': randint(0, 100)
    }
    car = MarketAvailableCarModel.objects.create(**car_data)
    unsuit_cars.append(car.pk)
    car_data = {
        "brand_name": 'Test',
        "car_model_name": 'Case_2',
        "year_of_production": 2020,
        "transmission": 'MANUAL',
        "body_type": "COUPE",
        "engine_fuel_type": 'GASOLINE',
        "engine_volume": 3.2,
        "drive_unit": "FRONT",
        "safe_controls": False,
        "parking_help": False,
        "climate_controls": False,
        "multimedia": False,
        "additional_safety": False,
        "other_additions": False,
        "color": 'white',
        'demand_level': randint(0, 100)
    }
    car = MarketAvailableCarModel.objects.create(**car_data)
    unsuit_cars.append(car.pk)
    dealers_suit_cars['third_case'] = {"dealer_id": third_spec.dealer.pk,
                                       "car_id": None}
    dealers_suit_cars['unsuit_cars_id'] = unsuit_cars
    return dealers_suit_cars


@pytest.fixture(scope='function', name='control_case_suit_seller')
def create_control_case_of_suit_sellers_for_dealers(control_case_suit_cars_for_dealer) \
        -> dict[str, AutoSellerModel | int | MarketAvailableCarModel]:
    """Creates user and seller instances, their car parks and discount with cars, suitable
    for created dealers for celery task tests purposes, returns dict with predefined suitable
    seller for defined dealer, car model to buy and list of unsuitable sellers"""
    sellers = []
    for _ in range(3):
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
        sellers.append(seller)
    discount_map = {0: 10,
                    5: 20}
    discount_data = {'seller': sellers[0],
                     'purchase_number_discount_map': discount_map}
    RegularCustomerDiscountLevelsModel.objects.create(**discount_data)
    car_id = control_case_suit_cars_for_dealer['first_case']['car_id']
    park_data = {
        "car_model": MarketAvailableCarModel.objects.get(id=car_id),
        "available_number": 100000,
        "car_price": 1100,
        "seller": sellers[0]
    }
    SellerCarParkModel.objects.create(**park_data)
    dealer_predefined_seller = {
                                "dealer_id":
                                control_case_suit_cars_for_dealer['first_case']['dealer_id'],
                                "seller":
                                sellers[0],
                                "car_model":
                                park_data['car_model']
                                }
    park_data = {
        "car_model": MarketAvailableCarModel.objects.get(id=car_id),
        "available_number": 100000,
        "car_price": 1000,
        "seller": sellers[1]
    }
    SellerCarParkModel.objects.create(**park_data)
    car_id = choice(control_case_suit_cars_for_dealer['unsuit_cars_id'])
    park_data = {
        "car_model": MarketAvailableCarModel.objects.get(id=car_id),
        "available_number": 100000,
        "car_price": 500,
        "seller": sellers[2]
    }
    SellerCarParkModel.objects.create(**park_data)
    dealer_predefined_seller['unsuit_sellers'] = [sellers[1].pk, sellers[2].pk]
    return dealer_predefined_seller
