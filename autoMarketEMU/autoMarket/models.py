from django.db import models
from django_countries.fields import CountryField


class Activeness(models.Model):
    is_active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AutoDealer(Activeness):
    name = models.CharField(max_length=100)
    home_country = CountryField()
    balance = models.FloatField()


class AutoSpecifications(models.Model):
    TRANSMISSION_CHOICES = [
                            ("MANUAL", "Manual"),
                            ("AUTO", "Auto"),
                            ("ROBOTIC", "Robotic")
                            ]
    transmission = models.CharField(max_length=50,
                                    choices=TRANSMISSION_CHOICES,
                                    default=None)
    BODY_TYPE_CHOICES = [
                        ("COUPE", "Coupe"),
                        ("SEDAN", "Sedan"),
                        ("HATCHBACK", "Hatchback"),
                        ("SUV", "SUV"),
                        ("MINIVAN", "Minivan")
                        ]
    body_type = models.CharField(max_length=50,
                                 choices=BODY_TYPE_CHOICES,
                                 default=None)
    ENGINE_FUEL_TYPE_CHOICES = [
                                ("GASOLINE", "Gasoline"),
                                ('DIESEL', "Diesel"),
                                ("GAS", "Gas")
                                ]
    engine_fuel_type = models.CharField(max_length=50,
                                        choices=ENGINE_FUEL_TYPE_CHOICES,
                                        default=None)
    engine_volume = models.FloatField()
    DRIVE_UNIT_CHOICES = [
                        ("FRONT", "Front"),
                        ("BACK", "Back"),
                        ("FULL", "Full")
                        ]
    drive_unit = models.CharField(max_length=50,
                                  choices=DRIVE_UNIT_CHOICES,
                                  default=None)
    safe_controls = models.BooleanField(default=False)
    parking_help = models.BooleanField(default=False)
    climate_controls = models.BooleanField(default=False)
    multimedia = models.BooleanField(default=False)
    additional_safety = models.BooleanField(default=False)
    other_additions = models.BooleanField(default=False)
    color = models.CharField(max_length=100)

    class Meta:
        abstract = True


class DealerSearchCarSpecifications(AutoSpecifications, Activeness):
    dealer = models.ForeignKey('AutoDealer', on_delete=models.CASCADE)
    min_year_of_production = models.IntegerField()


class MarketAvailableCars(AutoSpecifications, Activeness):
    brand_name = models.CharField(max_length=100)
    car_model_name = models.CharField(max_length=100)
    year_of_production = models.IntegerField()
    demand_level = models.FloatField()


class DealerSuitableCarModels(Activeness):
    dealer = models.ManyToManyField('AutoDealer')
    car_model = models.ManyToManyField('MarketAvailableCars')


class CurrentCarPark(models.Model):
    car_model_id = models.ForeignKey('MarketAvailableCars', on_delete=models.CASCADE)
    available_number = models.IntegerField()
    car_price = models.FloatField()

    class Meta:
        abstract = True


class DealerCarPark(CurrentCarPark, Activeness):
    pass


class AutoSellers(Activeness):
    name = models.CharField(max_length=100)
    year_of_creation = models.IntegerField()
    clients_number = models.IntegerField()


class SellersCarPark(CurrentCarPark, Activeness):
    pass


class SalesHistory(models.Model):
    date = models.DateField(auto_now_add=True)
    buyer = models.ForeignKey('AutoDealer', on_delete=models.CASCADE)
    selling_price = models.FloatField()
    sold_cars_quantity = models.IntegerField()
    deal_sum = models.FloatField()

    class Meta:
        abstract = True


class DealerSalesHistory(SalesHistory):
    buyer = models.ForeignKey('CarBuyers', on_delete=models.CASCADE)


class SellerSalesHistory(SalesHistory):
    pass


class CarBuyers(Activeness):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    balance = models.FloatField()
    drivers_license_number = models.CharField(max_length=100)


class CarBuyersHistory(models.Model):
    bought_car_model = models.ForeignKey('MarketAvailableCars', on_delete=models.CASCADE)
    auto_dealer = models.ForeignKey('AutoDealer', on_delete=models.CASCADE)
    bought_quantity = models.IntegerField()
    car_price = models.FloatField()
    deal_sum = models.FloatField()


class Offers(Activeness):
    max_price = models.FloatField()
    car_model = models.ForeignKey('MarketAvailableCars', on_delete=models.CASCADE)


class PromoDiscounts(Activeness):
    promo_name = models.CharField(max_length=100)
    promo_description = models.TextField()
    promo_cars = models.ManyToManyField('MarketAvailableCars')
    promo_aims = models.ManyToManyField('AutoDealer')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_size = models.FloatField()

    class Meta:
        abstract = True


class DealersPromo(PromoDiscounts):
    promo_aims = models.ManyToManyField('CarBuyers')
    promo_cars = models.ManyToManyField('DealerCarPark')


class SellersPromo(PromoDiscounts):
    promo_cars = models.ManyToManyField('SellersCarPark')



