from random import choice, randint

import pytest

from .models import DealerSearchCarSpecificationModel, DealerSuitableCarModel
from .serializers import DealerSearchCarSpecificationsSerializer


@pytest.fixture(scope='function', name='spec_data')
def create_spec_data():
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
def create_a_spec(all_profiles, spec_data):
    dealer = all_profiles['dealer']['profile_instance']
    spec_data['dealer'] = dealer
    created_spec = DealerSearchCarSpecificationModel.objects.create(**spec_data)
    created_spec_data = DealerSearchCarSpecificationsSerializer(created_spec).data
    spec = {"spec_data": created_spec_data,
            "spec_instance": created_spec}
    return spec


@pytest.fixture(scope='function', name='suit_cars')
def add_suitable_cars(spec, cars):
    added_cars = []
    for car in cars:
        added_car = DealerSuitableCarModel.objects.create()
        added_car.car_model.add(car)
        added_car.dealer.add(spec['spec_instance'].dealer)
        added_cars.append({'car': added_car,
                          'dealer': spec['spec_instance'].dealer})
    return added_cars
