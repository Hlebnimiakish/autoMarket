from django.db import models
from django.db.models import ForeignKey, IntegerField, JSONField, OneToOneField
from root.common.models import BaseModel


class RegularCustomerDiscountLevelsModel(BaseModel):
    seller: OneToOneField = OneToOneField('user.AutoSellerModel', on_delete=models.CASCADE)
    purchase_number_discount_map: JSONField = JSONField(default=dict, null=False, blank=False)


class CurrentDiscountLevelPerDealerModel(BaseModel):
    seller: ForeignKey = ForeignKey('user.AutoSellerModel', on_delete=models.CASCADE)
    dealer: ForeignKey = ForeignKey('user.AutoDealerModel', on_delete=models.CASCADE)
    current_discount: IntegerField = IntegerField(null=False, blank=False)
    current_purchase_number: IntegerField = IntegerField(null=False, blank=False)
