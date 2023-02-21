from rest_framework import routers

from .views import (DealerPromoCRUDView, DealerPromoReadOnlyView,
                    SellerPromoCRUDView, SellerPromoReadOnlyView)

promo_router = routers.DefaultRouter()
promo_router.register('my_seller_promo', SellerPromoCRUDView, basename='my-seller-promo')
promo_router.register('my_dealer_promo', DealerPromoCRUDView, basename='my-dealer-promo')
promo_router.register('dealer_promos', DealerPromoReadOnlyView, basename='dealer-promo')
promo_router.register('seller_promos', SellerPromoReadOnlyView, basename='seller-promo')
urlpatterns = promo_router.urls
