from contextlib import suppress

from django.db.models import Manager, Model, QuerySet


class ActiveOnlyManager(Manager):
    def get_queryset(self) -> QuerySet[Model]:  # type: ignore[override]
        return super().get_queryset().filter(is_active=True)

    def get_or_none(self, *args, **kwargs) -> Model | None:
        qs = None
        with suppress(self.model.DoesNotExist):
            qs = self.get_queryset().get(*args, **kwargs)
        return qs
