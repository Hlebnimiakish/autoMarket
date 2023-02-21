from django.urls import include, path
from rest_framework import routers

from .views import (DealerSearchCarSpecificationCreateView,
                    DealerSearchCarSpecificationRUDView,
                    DealerSearchCarSpecificationView,
                    DealerSuitableCarFrontView, DealerSuitableCarOwnView)

car_spec_router = routers.DefaultRouter()
car_spec_router.register('suitable_cars',
                         DealerSuitableCarFrontView,
                         basename='suitable-car')
car_spec_router.register('my_suitable_cars',
                         DealerSuitableCarOwnView,
                         basename='my-suitable-car')

urlpatterns = [
    path('my_car_specification/',
         DealerSearchCarSpecificationRUDView.as_view(),
         name='my-spec'),
    path('dealer_car_specifications/',
         DealerSearchCarSpecificationView.as_view(),
         name='dealer-specs'),
    path('create_car_specification/',
         DealerSearchCarSpecificationCreateView.as_view(),
         name='create-spec'),
    path('', include(car_spec_router.urls))
]
