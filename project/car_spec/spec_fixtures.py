"""This module contains fixtures for car_spec tests"""

from random import choice, randint

import pytest
from car_market.models import MarketAvailableCarModel
from user.models import AutoDealerModel

from .models import DealerSearchCarSpecificationModel, DealerSuitableCarModel
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
