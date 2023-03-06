from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import (BooleanField, CharField, DateTimeField,
                              DecimalField, EmailField, ForeignKey,
                              IntegerField, OneToOneField)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from root.common.models import BaseModel

from .custom_user_manager import CustomUserManager


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


class AutoDealerModel(BaseModel):
    name: CharField = CharField(max_length=100)
    home_country: CountryField = CountryField()
    balance: DecimalField = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    user: OneToOneField = OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class AutoSellerModel(BaseModel):
    name: CharField = CharField(max_length=100)
    year_of_creation: IntegerField = IntegerField()
    clients_number: IntegerField = IntegerField(null=True, blank=True)
    user: OneToOneField = OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class CarBuyerModel(BaseModel):
    firstname: CharField = CharField(max_length=100)
    lastname: CharField = CharField(max_length=100)
    balance: DecimalField = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    drivers_license_number: CharField = CharField(max_length=100)
    user: OneToOneField = OneToOneField('CustomUserModel', on_delete=models.CASCADE)


class DealerFromSellerPurchaseNumber(BaseModel):
    seller: ForeignKey = ForeignKey('AutoSellerModel', on_delete=models.CASCADE)
    dealer: ForeignKey = ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    purchase_number: IntegerField = IntegerField(blank=True)


class BuyerFromDealerPurchaseNumber(BaseModel):
    buyer: ForeignKey = ForeignKey('CarBuyerModel', on_delete=models.CASCADE)
    dealer: ForeignKey = ForeignKey('AutoDealerModel', on_delete=models.CASCADE)
    purchase_number: IntegerField = IntegerField(blank=True)
