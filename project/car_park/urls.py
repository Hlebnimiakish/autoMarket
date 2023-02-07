from rest_framework import routers

from .views import DealerAutoParkView, SellerAutoParkView

auto_park_router = routers.DefaultRouter()
auto_park_router.register(r'dealer_auto_park', DealerAutoParkView, basename='dealer-park')
auto_park_router.register(r'seller_auto_park', SellerAutoParkView, basename='seller-park')
urlpatterns = auto_park_router.urls
