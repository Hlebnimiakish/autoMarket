from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator

from .custom_user_manager import CustomUserManager


class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    email: models.EmailField = models.EmailField(_("email"),
                                                 blank=False,
                                                 null=False,
                                                 unique=True,
                                                 error_messages={
                                                     "unique": _("A user with that email already exists."),
                                                 }
                                                 )
    username_validator = UnicodeUsernameValidator()
    username: models.CharField = models.CharField(
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
    date_joined: models.DateTimeField = models.DateTimeField(_("date joined"), default=timezone.now)
    is_staff: models.BooleanField = models.BooleanField(default=False)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    USER_TYPE_CHOICES = [
        ("DEALER", "Dealer"),
        ("SELLER", "Seller"),
        ("BUYER", "Buyer")
    ]
    user_type: models.CharField = models.CharField(max_length=50,
                                                   choices=USER_TYPE_CHOICES,
                                                   blank=False,
                                                   null=False)
    is_verified: models.BooleanField = models.BooleanField(default=False)
    is_active: models.BooleanField = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = CustomUserManager()


class BaseActiveStatusModel(models.Model):
    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AutoDealerModel(BaseActiveStatusModel):
    name: models.CharField = models.CharField(max_length=100)
    home_country: CountryField = CountryField()
    balance: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    user: models.OneToOneField = models.OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class BaseAutoSpecificationsModel(BaseActiveStatusModel):
    TRANSMISSION_CHOICES = [
                            ("MANUAL", "Manual"),
                            ("AUTO", "Auto"),
                            ("ROBOTIC", "Robotic")
                            ]
    transmission: models.CharField = models.CharField(max_length=50,
                                                      choices=TRANSMISSION_CHOICES,
                                                      default=None)
    BODY_TYPE_CHOICES = [
                        ("COUPE", "Coupe"),
                        ("SEDAN", "Sedan"),
                        ("HATCHBACK", "Hatchback"),
                        ("SUV", "SUV"),
                        ("MINIVAN", "Minivan")
                        ]
    body_type: models.CharField = models.CharField(max_length=50,
                                                   choices=BODY_TYPE_CHOICES,
                                                   default=None)
    ENGINE_FUEL_TYPE_CHOICES = [
                                ("GASOLINE", "Gasoline"),
                                ('DIESEL', "Diesel"),
                                ("GAS", "Gas")
                                ]
    engine_fuel_type: models.CharField = models.CharField(max_length=50,
                                                          choices=ENGINE_FUEL_TYPE_CHOICES,
                                                          default=None)
    engine_volume: models.FloatField = models.FloatField()
    DRIVE_UNIT_CHOICES = [
                        ("FRONT", "Front"),
                        ("BACK", "Back"),
                        ("FULL", "Full")
                        ]
    drive_unit: models.CharField = models.CharField(max_length=50,
                                                    choices=DRIVE_UNIT_CHOICES,
                                                    default=None)
    safe_controls: models.BooleanField = models.BooleanField(default=False)
    parking_help: models.BooleanField = models.BooleanField(default=False)
    climate_controls: models.BooleanField = models.BooleanField(default=False)
    multimedia: models.BooleanField = models.BooleanField(default=False)
    additional_safety: models.BooleanField = models.BooleanField(default=False)
    other_additions: models.BooleanField = models.BooleanField(default=False)
    color: models.CharField = models.CharField(max_length=100)

    class Meta:
        abstract = True


class DealerSearchCarSpecificationModel(BaseAutoSpecificationsModel):
    dealer: models.ForeignKey = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    min_year_of_production: models.IntegerField = models.IntegerField()


class MarketAvailableCarModel(BaseAutoSpecificationsModel):
    brand_name: models.CharField = models.CharField(max_length=100)
    car_model_name: models.CharField = models.CharField(max_length=100)
    year_of_production: models.IntegerField = models.IntegerField()
    demand_level: models.DecimalField = models.DecimalField(max_digits=5, decimal_places=2, blank=True)


class DealerSuitableCarModel(BaseActiveStatusModel):
    dealer: models.ManyToManyField = models.ManyToManyField('AutoDealerModel')
    car_model: models.ManyToManyField = models.ManyToManyField('MarketAvailableCarModel')


class BaseCurrentCarParkModel(BaseActiveStatusModel):
    car_model_id: models.ForeignKey = models.ForeignKey('MarketAvailableCarModel', on_delete=models.CASCADE)
    available_number: models.IntegerField = models.IntegerField()
    car_price: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerCarParkModel(BaseCurrentCarParkModel):
    dealer: models.OneToOneField = models.OneToOneField('AutoDealerModel', on_delete=models.CASCADE)


class AutoSellerModel(BaseActiveStatusModel):
    name: models.CharField = models.CharField(max_length=100)
    year_of_creation: models.IntegerField = models.IntegerField()
    clients_number: models.IntegerField = models.IntegerField(null=True, blank=True)
    user: models.OneToOneField = models.OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class SellerCarParkModel(BaseCurrentCarParkModel):
    seller: models.OneToOneField = models.OneToOneField('AutoSellerModel', on_delete=models.CASCADE)
    pass


class BaseSalesHistoryModel(models.Model):
    date: models.DateField = models.DateField(auto_now_add=True)
    buyer: models.ForeignKey = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    selling_price: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    sold_cars_quantity: models.IntegerField = models.IntegerField()
    deal_sum: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerSalesHistoryModel(BaseSalesHistoryModel):
    buyer: models.ForeignKey = models.ForeignKey('CarBuyerModel', on_delete=models.CASCADE)


class SellerSalesHistoryModel(BaseSalesHistoryModel):
    pass


class CarBuyerModel(BaseActiveStatusModel):
    firstname: models.CharField = models.CharField(max_length=100)
    lastname: models.CharField = models.CharField(max_length=100)
    balance: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    drivers_license_number: models.CharField = models.CharField(max_length=100)
    user: models.OneToOneField = models.OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class CarBuyerHistoryModel(models.Model):
    bought_car_model: models.ForeignKey = models.ForeignKey('MarketAvailableCarModel', on_delete=models.CASCADE)
    auto_dealer: models.ForeignKey = models.ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    bought_quantity: models.IntegerField = models.IntegerField()
    car_price: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    deal_sum: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    buyer: models.ForeignKey = models.ForeignKey('CarBuyerModel', on_delete=models.CASCADE)


class OfferModel(BaseActiveStatusModel):
    max_price: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    car_model: models.ForeignKey = models.ForeignKey('MarketAvailableCarModel', on_delete=models.CASCADE)
    creator: models.OneToOneField = models.OneToOneField('CarBuyerModel', on_delete=models.CASCADE)


class BasePromoModel(BaseActiveStatusModel):
    promo_name: models.CharField = models.CharField(max_length=100)
    promo_description: models.TextField = models.TextField()
    start_date: models.DateTimeField = models.DateTimeField()
    end_date: models.DateTimeField = models.DateTimeField()
    discount_size: models.DecimalField = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        abstract = True


class DealerPromoModel(BasePromoModel):
    promo_aims: models.ManyToManyField = models.ManyToManyField('CarBuyerModel')
    promo_cars: models.ManyToManyField = models.ManyToManyField('DealerCarParkModel')
    creator: models.OneToOneField = models.OneToOneField('AutoDealerModel', on_delete=models.CASCADE)


class SellerPromoModel(BasePromoModel):
    promo_cars: models.ManyToManyField = models.ManyToManyField('SellerCarParkModel')
    promo_aims: models.ManyToManyField = models.ManyToManyField('AutoDealerModel')
    creator: models.OneToOneField = models.OneToOneField('AutoSellerModel', on_delete=models.CASCADE)
