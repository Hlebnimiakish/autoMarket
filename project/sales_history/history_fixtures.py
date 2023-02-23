from datetime import date

import pytest

from .models import (CarBuyerHistoryModel, DealerSalesHistoryModel,
                     SellerSalesHistoryModel)


@pytest.fixture(scope='function', name='history_records')
def create_history_record_for_each_user(car_parks, all_profiles):
    records = {}
    for seller, buyer in {'dealer': 'buyer',
                          'seller': 'dealer'}.items():
        park_owner = {'dealer': car_parks['dealer_park'].dealer,
                      'seller': car_parks['seller_park'].seller}
        models = {'dealer': DealerSalesHistoryModel,
                  'seller': SellerSalesHistoryModel}
        cars_quantity = car_parks[f'{seller}_park'].available_number
        car_price = car_parks[f'{seller}_park'].car_price
        record_data = {
            "date": date.today(),
            "sold_cars_quantity": cars_quantity,
            "selling_price": car_price,
            "deal_sum": car_price * cars_quantity,
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
