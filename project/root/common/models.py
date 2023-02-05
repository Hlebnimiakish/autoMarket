from django.db import models
from django.db.models import BooleanField, DateTimeField

from .model_manager import ActiveOnlyManager


class BaseModel(models.Model):
    is_active: BooleanField = BooleanField(default=True)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    objects = ActiveOnlyManager()

    class Meta:
        abstract = True
