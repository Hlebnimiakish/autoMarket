"""This module contains fixtures for offer tests"""

from random import choice, randint

import pytest

from .models import OfferModel


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
