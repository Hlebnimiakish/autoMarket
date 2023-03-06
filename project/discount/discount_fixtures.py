from random import randint

import pytest
from user.models import DealerFromSellerPurchaseNumber

from .models import CurrentDiscountLevelPerDealerModel as CurrentDiscount
from .models import RegularCustomerDiscountLevelsModel as DiscountLevels


@pytest.fixture(scope='function', name='purchases')
def create_dealer_purchases(all_profiles, additional_profiles):
    dealer = all_profiles['dealer']['profile_instance']
    seller = all_profiles['seller']['profile_instance']
    dealer2 = additional_profiles['dealer']['profile_instance']
    seller2 = additional_profiles['seller']['profile_instance']
    sellers = [seller, seller2]
    dealers = [dealer, dealer2]
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
def create_seller_discounts(all_profiles, additional_profiles):
    seller = all_profiles['seller']['profile_instance']
    seller2 = additional_profiles['seller']['profile_instance']
    sellers = [seller, seller2]
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
                                   all_profiles,
                                   additional_profiles):
    dealer = all_profiles['dealer']['profile_instance']
    seller = all_profiles['seller']['profile_instance']
    dealer2 = additional_profiles['dealer']['profile_instance']
    seller2 = additional_profiles['seller']['profile_instance']
    sellers = [seller, seller2]
    dealers = [dealer, dealer2]
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
