from rest_framework import routers

from .views import OfferCRUDView, OfferForDealerView

offer_router = routers.DefaultRouter()
offer_router.register(r'offers', OfferForDealerView, basename='offer')
offer_router.register(r'my_offer', OfferCRUDView, basename='my_offer')
urlpatterns = offer_router.urls
