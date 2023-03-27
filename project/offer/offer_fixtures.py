# pylint: disable=duplicate-code, too-many-locals

"""This module contains fixtures for offer tests"""

import uuid
from datetime import timedelta
from decimal import Decimal
from random import choice, randint

import pytest
from car_market.models import MarketAvailableCarModel
from car_park.models import DealerCarParkModel
from django.utils import timezone
from promo.models import DealerPromoModel
from pytest import FixtureRequest
from rest_framework.test import APIClient
from user.models import CarBuyerModel, CustomUserModel

from .models import OfferModel
from .serializers import OffersSerializer


@pytest.fixture(scope='function', name='not_rich_buyer')
def create_buyer_with_low_balance(request: FixtureRequest,
                                  client: APIClient) -> CarBuyerModel:
    """Creates and returns a buyer profile with passed balance,
    also authenticate created buyer"""
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": "BUYER",
        "is_verified": True
    }
    user = CustomUserModel.objects.create_user(**user_data)
    buyer_profile_data = {
        "firstname": f"tbuyer{uuid.uuid4().hex}",
        "lastname": f"tbuyer{uuid.uuid4().hex}",
        "drivers_license_number": str(uuid.uuid4().hex),
        "balance": Decimal(request.param),
        "user": user
    }
    buyer = CarBuyerModel.objects.create(**buyer_profile_data)
    client.force_authenticate(user=user)
    return buyer


@pytest.fixture(scope='function', name='offer_data')
def create_offer_data(cars: list) -> dict:
    """Creates and returns a dict of required offer data"""
    offer_data = {
        "max_price": randint(5000, 15000),
        "car_model": choice(cars).id
    }
    return offer_data


@pytest.fixture(scope='function', name='offer')
def create_offer(all_profiles: dict, cars: list) -> OfferModel:
    """Creates db record of an offer, returns created instance
    of an offer"""
    buyer = all_profiles['buyer']['profile_instance']
    offer_data = {
        "max_price": randint(5000, 15000),
        "car_model": choice(cars),
        "creator": buyer
    }
    offer = OfferModel.objects.create(**offer_data)
    return offer


@pytest.fixture(scope='function', name='control_case_dealers_parks_offer')
def create_control_case_dealers_their_parks_and_offer(dealers_for_control_cases: list,
                                                      all_profiles: dict):
    """Creates car park and promo instances for created dealers, creates buyer offer
    based on created car parks with high maximum car price for future deal and
    returns created offer serialized data for celery tasks test purposes"""
    dealers = dealers_for_control_cases
    cars_data = []
    for _ in range(10):
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
    all_cars = MarketAvailableCarModel.objects.bulk_create(cars_data)
    car_model = choice(all_cars)
    first_park_data = {
        "car_model": car_model,
        "available_number": 100000,
        "car_price": 1000,
        "dealer": dealers[0]
    }
    DealerCarParkModel.objects.create(**first_park_data)
    second_park_data = {
            "car_model": car_model,
            "available_number": 100000,
            "car_price": 1100,
            "dealer": dealers[1]
    }
    DealerCarParkModel.objects.create(**second_park_data)
    third_park_data = {
        "car_model": car_model,
        "available_number": 100000,
        "car_price": 1200,
        "dealer": dealers[2]
    }
    third_park = DealerCarParkModel.objects.create(**third_park_data)
    buyer = all_profiles['buyer']['profile_instance']
    promo_data = {
        "promo_name": f"promo{uuid.uuid4().hex}",
        "promo_description": "This promo is a test promo",
        "start_date": timezone.now(),
        "end_date": (timezone.now() + timedelta(days=5)),
        "discount_size": 25,
        "creator": dealers[2]
    }
    dealer_promo = DealerPromoModel.objects.create(**promo_data)
    dealer_promo.promo_aims.add(buyer.pk)
    dealer_promo.promo_cars.add(third_park.pk)
    case_offer_data = {
            "max_price": 1000,
            "car_model": car_model,
            "creator": buyer
        }
    offer = OfferModel.objects.create(**case_offer_data)
    offer_data = OffersSerializer(offer).data
    return {"offer_data": offer_data, "predefined_park": third_park}
