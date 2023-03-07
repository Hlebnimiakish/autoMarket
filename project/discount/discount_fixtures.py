"""This module contains fixtures for discount tests"""

from random import randint
from typing import Dict, List

import pytest
from django.db.models import CharField
from root.common.models import BaseModel
from user.models import (AutoDealerModel, AutoSellerModel,
                         DealerFromSellerPurchaseNumber)

from .models import CurrentDiscountLevelPerDealerModel as CurrentDiscount
from .models import RegularCustomerDiscountLevelsModel as DiscountLevels


@pytest.fixture(scope='function', name='dealers')
def create_dealers_list(all_profiles, additional_profiles) -> List[AutoDealerModel]:
    """Creates and returns list of dealer profiles from all_profiles
    and additional_profiles for other fixtures"""
    return [all_profiles['dealer']['profile_instance'],
            additional_profiles['dealer']['profile_instance']]


@pytest.fixture(scope='function', name='sellers')
def create_sellers_list(all_profiles, additional_profiles) -> List[AutoSellerModel]:
    """Creates and returns list of seller profiles from all_profiles
    and additional_profiles for other fixtures"""
    return [all_profiles['seller']['profile_instance'],
            additional_profiles['seller']['profile_instance']]


@pytest.fixture(scope='function', name='purchases')
def create_dealer_purchases(dealers, sellers) -> Dict[AutoDealerModel,
                                                      DealerFromSellerPurchaseNumber]:
    """Creates db records of dealers purchase number, returns dict of dealer
    profiles with their purchase number records"""
    purchases = {}
    for seller in sellers:
        for dealer in dealers:
            purchase_record = {'seller': seller,
                               'dealer': dealer,
                               'purchase_number': randint(2, 50)}
            purchase = DealerFromSellerPurchaseNumber.objects.create(**purchase_record)
            purchases[dealer] = purchase
    return purchases


@pytest.fixture(scope='function', name='discounts')
def create_seller_discounts(sellers) -> Dict[BaseModel, Dict[str, DiscountLevels | dict]]:
    """Creates db records of sellers discount levels, returns dict of seller
        profiles with their discount records"""
    discounts = {}
    for seller in sellers:
        discount_map = {randint(1, 2): randint(3, 10),
                        randint(5, 10): randint(11, 15),
                        randint(20, 50): randint(20, 30)}
        discount_data = {'seller': seller,
                         'purchase_number_discount_map': discount_map}
        discount = DiscountLevels.objects.create(**discount_data)
        discounts[seller] = {'discount_instance': discount,
                             'discount_data': discount_data}
    return discounts


@pytest.fixture(scope='function', name='current_levels')
def create_current_discount_levels(purchases,
                                   discounts,
                                   sellers,
                                   dealers) -> Dict[CharField, CurrentDiscount]:
    """Creates db records of current dealers discount level, returns dict of dealer profile
    names with their current discount level records"""
    discounts_map = {}
    for seller in sellers:
        for dealer in dealers:
            purchase_number = purchases[dealer].purchase_number
            discount_map = \
                discounts[seller]['discount_data']['purchase_number_discount_map']
            purchase_number_to_discount = sorted([int(key) for key in
                                                 discount_map.keys()], reverse=True)
            for number in purchase_number_to_discount:
                if int(purchase_number) >= int(number):
                    discount_data = {"seller": seller,
                                     "dealer": dealer,
                                     "current_discount": discount_map[number],
                                     "current_purchase_number": purchase_number}
                    current_discount = CurrentDiscount.objects.create(**discount_data)
                    discounts_map[dealer.name] = current_discount
                    break
    return discounts_map
