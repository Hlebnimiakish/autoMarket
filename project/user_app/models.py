from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import (BooleanField, CharField, DateField,
                              DateTimeField, DecimalField, EmailField,
                              FloatField, ForeignKey, IntegerField,
                              ManyToManyField, OneToOneField, TextField)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from .custom_user_manager import ActiveOnlyManager, CustomUserManager


class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    email: EmailField = EmailField(_("email"),
                                   blank=False,
                                   null=False,
                                   unique=True,
                                   error_messages={
                                       "unique": _("A user with that email already exists."),
                                   }
                                   )
    username_validator = UnicodeUsernameValidator()
    username: CharField = CharField(
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
    date_joined: DateTimeField = DateTimeField(_("date joined"), default=timezone.now)
    is_staff: BooleanField = BooleanField(default=False)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    USER_TYPE_CHOICES = [
        ("DEALER", "Dealer"),
        ("SELLER", "Seller"),
        ("BUYER", "Buyer")
    ]
    user_type: CharField = CharField(max_length=50,
                                     choices=USER_TYPE_CHOICES,
                                     blank=False,
                                     null=False)
    is_verified: BooleanField = BooleanField(default=False)
    is_active: BooleanField = BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = CustomUserManager()


class BaseModel(models.Model):
    is_active: BooleanField = BooleanField(default=True)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    objects = ActiveOnlyManager()

    class Meta:
        abstract = True


class AutoDealerModel(BaseModel):
    name: CharField = CharField(max_length=100)
    home_country: CountryField = CountryField()
    balance: DecimalField = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    user: OneToOneField = OneToOneField('CustomUserModel', on_delete=models.CASCADE)


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


class DealerSearchCarSpecificationModel(BaseAutoSpecificationModel):
    dealer: ForeignKey = ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    min_year_of_production: IntegerField = IntegerField()


class MarketAvailableCarModel(BaseAutoSpecificationModel):
    brand_name: CharField = CharField(max_length=100)
    car_model_name: CharField = CharField(max_length=100)
    year_of_production: IntegerField = IntegerField()
    demand_level: DecimalField = DecimalField(max_digits=5, decimal_places=2, blank=True)


class DealerSuitableCarModel(BaseModel):
    dealer: ManyToManyField = ManyToManyField('AutoDealerModel')
    car_model: ManyToManyField = ManyToManyField('MarketAvailableCarModel')


class BaseCurrentCarParkModel(BaseModel):
    car_model_id: ForeignKey = ForeignKey('MarketAvailableCarModel', on_delete=models.CASCADE)
    available_number: IntegerField = IntegerField()
    car_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerCarParkModel(BaseCurrentCarParkModel):
    dealer: OneToOneField = OneToOneField('AutoDealerModel', on_delete=models.CASCADE)


class AutoSellerModel(BaseModel):
    name: CharField = CharField(max_length=100)
    year_of_creation: IntegerField = IntegerField()
    clients_number: IntegerField = IntegerField(null=True, blank=True)
    user: OneToOneField = OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class SellerCarParkModel(BaseCurrentCarParkModel):
    seller: OneToOneField = OneToOneField('AutoSellerModel', on_delete=models.CASCADE)
    pass


class BaseSalesHistoryModel(BaseModel):
    date: DateField = DateField(auto_now_add=True)
    buyer: ForeignKey = ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    selling_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    sold_cars_quantity: IntegerField = IntegerField()
    deal_sum: DecimalField = DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class DealerSalesHistoryModel(BaseSalesHistoryModel):
    buyer: ForeignKey = ForeignKey('CarBuyerModel', on_delete=models.CASCADE)


class SellerSalesHistoryModel(BaseSalesHistoryModel):
    pass


class CarBuyerModel(BaseModel):
    firstname: CharField = CharField(max_length=100)
    lastname: CharField = CharField(max_length=100)
    balance: DecimalField = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    drivers_license_number: CharField = CharField(max_length=100)
    user: OneToOneField = OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class CarBuyerHistoryModel(BaseModel):
    bought_car_model: ForeignKey = ForeignKey('MarketAvailableCarModel', on_delete=models.CASCADE)
    auto_dealer: ForeignKey = ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    bought_quantity: IntegerField = IntegerField()
    car_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    deal_sum: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    buyer: ForeignKey = ForeignKey('CarBuyerModel', on_delete=models.CASCADE)
    date: DateField = DateField(auto_now_add=True)


class OfferModel(BaseModel):
    max_price: DecimalField = DecimalField(max_digits=12, decimal_places=2)
    car_model: ForeignKey = ForeignKey('MarketAvailableCarModel', on_delete=models.CASCADE)
    creator: OneToOneField = OneToOneField('CarBuyerModel', on_delete=models.CASCADE)


class BasePromoModel(BaseModel):
    promo_name: CharField = CharField(max_length=100)
    promo_description: TextField = TextField()
    start_date: DateTimeField = DateTimeField()
    end_date: DateTimeField = DateTimeField()
    discount_size: DecimalField = DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        abstract = True


class DealerPromoModel(BasePromoModel):
    promo_aims: ManyToManyField = ManyToManyField('CarBuyerModel')
    promo_cars: ManyToManyField = ManyToManyField('DealerCarParkModel')
    creator: OneToOneField = OneToOneField('AutoDealerModel', on_delete=models.CASCADE)


class SellerPromoModel(BasePromoModel):
    promo_cars: ManyToManyField = ManyToManyField('SellerCarParkModel')
    promo_aims: ManyToManyField = ManyToManyField('AutoDealerModel')
    creator: OneToOneField = OneToOneField('AutoSellerModel', on_delete=models.CASCADE)
