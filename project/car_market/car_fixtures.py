"""This module contains fixtures for car_market tests"""

from random import choice, randint

import pytest

from .models import MarketAvailableCarModel


@pytest.fixture(scope='function', name='cars')
def create_cars() -> list[MarketAvailableCarModel]:
    """Creates definite number of db records of market available
    cars and returns list of created car instances"""
    cars_data = []
    for _ in range(100):
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
        cars_data.append(MarketAvailableCarModel(**car_data))
    cars = MarketAvailableCarModel.objects.bulk_create(cars_data)
    return cars
