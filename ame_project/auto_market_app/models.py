from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser, AbstractBaseUser, UnicodeUsernameValidator, PermissionsMixin
from .ameuser_manager import AmeUserManager


class AmeUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"),
                              blank=False,
                              null=False,
                              unique=True,
                              error_messages={
                                  "unique": _("A user with that email already exists."),
                              }
                              )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    is_staff = models.BooleanField(default=False)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    USER_TYPE_CHOICES = [
        ("DEALER", "Dealer"),
        ("SELLER", "Seller"),
        ("BUYER", "Buyer")
    ]
    user_type = models.CharField(max_length=50,
                                 choices=USER_TYPE_CHOICES,
                                 blank=False,
                                 null=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = AmeUserManager()


class BaseActiveStatusModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AutoDealerModel(BaseActiveStatusModel):
    name = models.CharField(max_length=100)
    home_country = CountryField()
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.OneToOneField('AmeUserModel', on_delete=models.CASCADE)


class BaseAutoSpecificationsModel(models.Model):
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


class DealerSearchCarSpecificationsModel(BaseAutoSpecificationsModel, BaseActiveStatusModel):
    dealer = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    min_year_of_production = models.IntegerField()


class MarketAvailableCarsModel(BaseAutoSpecificationsModel, BaseActiveStatusModel):
    brand_name = models.CharField(max_length=100)
    car_model_name = models.CharField(max_length=100)
    year_of_production = models.IntegerField()
    demand_level = models.DecimalField(max_digits=5, decimal_places=2)


class DealerSuitableCarModelsModel(BaseActiveStatusModel):
    dealer = models.ManyToManyField('AutoDealerModel')
    car_model = models.ManyToManyField('MarketAvailableCarsModel')


class BaseCurrentCarParkModel(models.Model):
    car_model_id = models.ForeignKey('MarketAvailableCarsModel', on_delete=models.CASCADE)
    available_number = models.IntegerField()
    car_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerCarParkModel(BaseCurrentCarParkModel, BaseActiveStatusModel):
    pass


class AutoSellersModel(BaseActiveStatusModel):
    name = models.CharField(max_length=100)
    year_of_creation = models.IntegerField()
    clients_number = models.IntegerField()
    user = models.OneToOneField('AmeUserModel', on_delete=models.CASCADE)


class SellersCarParkModel(BaseCurrentCarParkModel, BaseActiveStatusModel):
    pass


class BaseSalesHistoryModel(models.Model):
    date = models.DateField(auto_now_add=True)
    buyer = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    sold_cars_quantity = models.IntegerField()
    deal_sum = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerSalesHistoryModel(BaseSalesHistoryModel):
    buyer = models.ForeignKey('CarBuyersModel', on_delete=models.CASCADE)


class SellerSalesHistoryModel(BaseSalesHistoryModel):
    pass


class CarBuyersModel(BaseActiveStatusModel):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    drivers_license_number = models.CharField(max_length=100)
    user = models.OneToOneField('AmeUserModel', on_delete=models.CASCADE)


class CarBuyersHistoryModel(models.Model):
    bought_car_model = models.ForeignKey('MarketAvailableCarsModel', on_delete=models.CASCADE)
    auto_dealer = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    bought_quantity = models.IntegerField()
    car_price = models.DecimalField(max_digits=12, decimal_places=2)
    deal_sum = models.DecimalField(max_digits=12, decimal_places=2)
    buyer = models.ForeignKey('CarBuyersModel', on_delete=models.CASCADE)


class OffersModel(BaseActiveStatusModel):
    max_price = models.DecimalField(max_digits=12, decimal_places=2)
    car_model = models.ForeignKey('MarketAvailableCarsModel', on_delete=models.CASCADE)
    buyer = models.ForeignKey('CarBuyersModel', on_delete=models.CASCADE)


class BasePromoModel(BaseActiveStatusModel):
    promo_name = models.CharField(max_length=100)
    promo_description = models.TextField()
    promo_cars = models.ManyToManyField('MarketAvailableCarsModel')
    promo_aims = models.ManyToManyField('AutoDealerModel')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_size = models.DecimalField(max_digits=5, decimal_places=2)
    source = models.ForeignKey('AutoSellersModel', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DealersPromoModel(BasePromoModel):
    promo_aims = models.ManyToManyField('CarBuyersModel')
    promo_cars = models.ManyToManyField('DealerCarParkModel')
    source = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)


class SellersPromoModel(BasePromoModel):
    promo_cars = models.ManyToManyField('SellersCarParkModel')




