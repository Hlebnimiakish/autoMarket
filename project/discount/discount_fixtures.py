# pylint: disable=too-many-locals

"""This module contains fixtures for discount tests"""

from random import randint

import pytest
from django.db.models import CharField
from root.common.models import BaseModel
from user.models import (AutoDealerModel, AutoSellerModel,
                         DealerFromSellerPurchaseNumber)

from .models import CurrentDiscountLevelPerDealerModel as CurrentDiscount
from .models import RegularCustomerDiscountLevelsModel as DiscountLevels
from .serializers import \
    RegularCustomerDiscountLevelsSerializer as DiscountSerializer


@pytest.fixture(scope='function', name='dealers')
def create_dealers_list(all_profiles: dict,
                        additional_profiles: dict) -> list[AutoDealerModel]:
    """Creates and returns list of dealer profiles from all_profiles
    and additional_profiles fixtures"""
    return [all_profiles['dealer']['profile_instance'],
            additional_profiles['dealer']['profile_instance']]


@pytest.fixture(scope='function', name='sellers')
def create_sellers_list(all_profiles: dict,
                        additional_profiles: dict) -> list[AutoSellerModel]:
    """Creates and returns list of seller profiles from all_profiles
    and additional_profiles fixtures"""
    return [all_profiles['seller']['profile_instance'],
            additional_profiles['seller']['profile_instance']]


@pytest.fixture(scope='function', name='purchases')
def create_dealer_purchases(dealers: list,
                            sellers: list) -> dict[AutoDealerModel,
                                                   DealerFromSellerPurchaseNumber]:
    """Creates db records of dealers purchase number, returns dict of dealer
    profiles with their purchase number records"""
    purchases_list = []
    purchases = {}
    for seller in sellers:
        for dealer in dealers:
            purchase_data = {'seller': seller,
                             'dealer': dealer,
                             'purchase_number': randint(2, 45)}
            purchases_list.append(DealerFromSellerPurchaseNumber(**purchase_data))
    purchases_list = DealerFromSellerPurchaseNumber.objects.bulk_create(purchases_list)
    for purchase in purchases_list:
        purchases[purchase.dealer] = purchase
    return purchases


@pytest.fixture(scope='function', name='discounts')
def create_seller_discounts(sellers: list) -> dict[BaseModel, DiscountLevels]:
    """Creates db records of sellers discount levels, returns dict of
    seller profiles with their discount records"""
    discounts_list = []
    for seller in sellers:
        discount_map = {randint(1, 2): randint(3, 10),
                        randint(5, 10): randint(11, 15),
                        randint(20, 50): randint(20, 30)}
        discount_data = {'seller': seller,
                         'purchase_number_discount_map': discount_map}
        discounts_list.append(DiscountLevels(**discount_data))
    created_discounts = DiscountLevels.objects.bulk_create(discounts_list)
    discounts = {}
    for discount in created_discounts:
        discounts[discount.seller] = discount
    return discounts


@pytest.fixture(scope='function', name='current_levels')
def create_current_discount_levels(purchases: dict,
                                   discounts: dict,
                                   sellers: list,
                                   dealers: list) -> dict[CharField, CurrentDiscount]:
    """Creates db records of current dealers discount level, returns dict of
    dealer profile names with their current discount level records"""
    discounts_map = {}
    current_discounts_list = []
    for seller in sellers:
        for dealer in dealers:
            purchase_number = purchases[dealer].purchase_number
            discount_map = \
                DiscountSerializer(discounts[seller]).data['purchase_number_discount_map']
            purchase_number_to_discount = sorted([int(key) for key in
                                                 discount_map.keys()], reverse=True)
            for number in purchase_number_to_discount:
                if int(purchase_number) >= int(number):
                    discount_data = {"seller": seller,
                                     "dealer": dealer,
                                     "current_discount": discount_map[str(number)],
                                     "current_purchase_number": purchase_number}
                    current_discounts_list.append(CurrentDiscount(**discount_data))
                    break
    current_discounts = CurrentDiscount.objects.bulk_create(current_discounts_list)
    for discount in current_discounts:
        discounts_map[discount.dealer.name] = discount
    return discounts_map
