from random import choice, randint

import pytest

from .models import MarketAvailableCarModel
from .serializers import MarkerAvailableCarsModelSerializer


@pytest.fixture(scope='function', name='cars')
def create_ten_cars():
    cars = {}
    for car in range(10):
        car_data = {
            "brand_name": choice(['Mesla', 'PulseWagen', 'Meely', 'Konda',
                                  'Pissan', 'Laudi', 'Koyota', 'Peat']),
            "car_model_name": choice(['Carbon', 'Leman', 'Turtle', 'Rabbit', 'Hobbit',
                                      'Bilbo', 'Jinnie', 'Mini', 'Cat', 'Bug', 'Slug']),
            "year_of_production": randint(1990, 2023),
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
            'demand_level': randint(0, 100)
        }
        created_car = MarketAvailableCarModel.objects.create(**car_data)
        created_car_data = MarkerAvailableCarsModelSerializer(created_car).data
        cars[car+1] = {
            'car_instance': created_car,
            'car_data': created_car_data
        }
    yield cars

    for car in cars.values():
        car['car_instance'].delete()
