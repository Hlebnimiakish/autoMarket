from rest_framework import routers

from .views import OfferCRUDView, OfferForDealerView

offer_router = routers.DefaultRouter()
offer_router.register('offers', OfferForDealerView, basename='offer')
offer_router.register('my_offer', OfferCRUDView, basename='my-offer')
urlpatterns = offer_router.urls
