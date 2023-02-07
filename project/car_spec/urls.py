from django.urls import include, path
from rest_framework import routers

from .views import (DealerSearchCarSpecificationCreateView,
                    DealerSearchCarSpecificationRUDView,
                    DealerSearchCarSpecificationView, DealerSuitableCarView)

car_spec_router = routers.DefaultRouter()
car_spec_router.register(r'suitable_cars', DealerSuitableCarView, basename='suitable_car')

urlpatterns = [
    path('my_car_specification/',
         DealerSearchCarSpecificationRUDView.as_view(),
         name='my_spec'),
    path('dealer_car_specifications/',
         DealerSearchCarSpecificationView.as_view(),
         name='dealer_specs'),
    path('create_car_specification/',
         DealerSearchCarSpecificationCreateView.as_view(),
         name='create_spec'),
    path('', include(car_spec_router.urls))
]
