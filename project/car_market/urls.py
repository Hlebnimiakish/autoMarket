from rest_framework import routers

from .views import MarketAvailableCarModelView

car_market_router = routers.DefaultRouter()
car_market_router.register(r'car_model', MarketAvailableCarModelView, basename='car')
urlpatterns = car_market_router.urls
