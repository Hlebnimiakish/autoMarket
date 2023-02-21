from random import choice, randint

import pytest

from .models import DealerCarParkModel, SellerCarParkModel
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


@pytest.fixture(scope='function', name='car_parks')
def create_car_parks(cars, all_profiles):
    parks = {}
    creation_data_dict = {'dealer': {"profile": all_profiles['dealer'],
                                     "model": DealerCarParkModel,
                                     "serializer": DealerCarParkSerializer},
                          'seller': {"profile": all_profiles['seller'],
                                     "model": SellerCarParkModel,
                                     "serializer": SellersCarParkSerializer}}
    for owner_type, owner in creation_data_dict.items():
        park_data = {
            "car_model": choice([c for c in cars]),
            "available_number": randint(1, 10),
            "car_price": randint(1000, 10000),
            str(owner_type): owner["profile"]["profile_instance"]
        }
        park = owner['model'].objects.create(**park_data)
        parks[f'{owner_type}_park'] = park

    yield parks

    for park in parks.values():
        park.delete()
