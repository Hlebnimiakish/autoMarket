# pylint: disable=duplicate-code

"""This module contains fixtures for offer tests"""

import uuid
from decimal import Decimal
from random import choice, randint

import pytest
from pytest import FixtureRequest
from rest_framework.test import APIClient
from user.models import CarBuyerModel, CustomUserModel

from .models import OfferModel


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
