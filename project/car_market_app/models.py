from django.db.models import (BooleanField, CharField, DecimalField,
                              FloatField, IntegerField)
from root.common.models import BaseModel


class BaseAutoSpecificationModel(BaseModel):
    TRANSMISSION_CHOICES = [
                            ("MANUAL", "Manual"),
                            ("AUTO", "Auto"),
                            ("ROBOTIC", "Robotic")
                            ]
    transmission: CharField = CharField(max_length=50,
                                        choices=TRANSMISSION_CHOICES,
                                        default=None)
    BODY_TYPE_CHOICES = [
                        ("COUPE", "Coupe"),
                        ("SEDAN", "Sedan"),
                        ("HATCHBACK", "Hatchback"),
                        ("SUV", "SUV"),
                        ("MINIVAN", "Minivan")
                        ]
    body_type: CharField = CharField(max_length=50,
                                     choices=BODY_TYPE_CHOICES,
                                     default=None)
    ENGINE_FUEL_TYPE_CHOICES = [
                                ("GASOLINE", "Gasoline"),
                                ('DIESEL', "Diesel"),
                                ("GAS", "Gas")
                                ]
    engine_fuel_type: CharField = CharField(max_length=50,
                                            choices=ENGINE_FUEL_TYPE_CHOICES,
                                            default=None)
    engine_volume: FloatField = FloatField()
    DRIVE_UNIT_CHOICES = [
                        ("FRONT", "Front"),
                        ("BACK", "Back"),
                        ("FULL", "Full")
                        ]
    drive_unit: CharField = CharField(max_length=50,
                                      choices=DRIVE_UNIT_CHOICES,
                                      default=None)
    safe_controls: BooleanField = BooleanField(default=False)
    parking_help: BooleanField = BooleanField(default=False)
    climate_controls: BooleanField = BooleanField(default=False)
    multimedia: BooleanField = BooleanField(default=False)
    additional_safety: BooleanField = BooleanField(default=False)
    other_additions: BooleanField = BooleanField(default=False)
    color: CharField = CharField(max_length=100)

    class Meta:
        abstract = True


class MarketAvailableCarModel(BaseAutoSpecificationModel):
    brand_name: CharField = CharField(max_length=100)
    car_model_name: CharField = CharField(max_length=100)
    year_of_production: IntegerField = IntegerField()
    demand_level: DecimalField = DecimalField(max_digits=5, decimal_places=2, blank=True)
