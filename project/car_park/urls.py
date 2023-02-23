from rest_framework import routers

from .views import (DealerAutoParkFrontView, DealerOwnAutoParkReadView,
                    SellerAutoParkFrontView, SellerOwnAutoParkReadView)

auto_park_router = routers.DefaultRouter()
auto_park_router.register('dealer_auto_park',
                          DealerAutoParkFrontView,
                          basename='dealer-park')
auto_park_router.register('seller_auto_park',
                          SellerAutoParkFrontView,
                          basename='seller-park')
auto_park_router.register('my_seller_auto_park',
                          SellerOwnAutoParkReadView,
                          basename='my-seller-park')
auto_park_router.register('my_dealer_auto_park',
                          DealerOwnAutoParkReadView,
                          basename='my-dealer-park')
urlpatterns = auto_park_router.urls
