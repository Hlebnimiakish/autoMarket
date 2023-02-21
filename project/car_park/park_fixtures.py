from random import choice, randint

import pytest

from .models import DealerCarParkModel, SellerCarParkModel
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


@pytest.fixture(scope='function', name='car_parks')
def create_car_parks(cars, all_profiles):
    parks = {}
    for owner_type, owner in {'dealer': {"profile": all_profiles['dealer'],
                                         "model": DealerCarParkModel,
                                         "serializer": DealerCarParkSerializer},
                              'seller': {"profile": all_profiles['seller'],
                                         "model": SellerCarParkModel,
                                         "serializer": SellersCarParkSerializer}}.items():
        park_data = {
            "car_model": choice([n['car_instance'] for n in cars.values()]),
            "available_number": randint(1, 10),
            "car_price": randint(1000, 10000),
            f"{owner_type}": owner["profile"]["profile_instance"]
        }
        park = owner['model'].objects.create(**park_data)
        parks[f'{owner_type}'] = {
            'park_data': owner['serializer'](park).data,
            'park_instance': park
        }

    yield parks

    for park in parks.values():
        park['park_instance'].delete()
