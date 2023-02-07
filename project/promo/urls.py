from rest_framework import routers

from .views import (DealerPromoCRUDView, DealerPromoReadOnlyView,
                    SellerPromoCRUDView, SellerPromoReadOnlyView)

promo_router = routers.DefaultRouter()
promo_router.register(r'my_seller_promo', SellerPromoCRUDView, basename='my-spromo')
promo_router.register(r'my_dealer_promo', DealerPromoCRUDView, basename='my-dpromo')
promo_router.register(r'dealer_promos', DealerPromoReadOnlyView, basename='dealer-promo')
promo_router.register(r'seller_promos', SellerPromoReadOnlyView, basename='seller-promo')
urlpatterns = promo_router.urls
