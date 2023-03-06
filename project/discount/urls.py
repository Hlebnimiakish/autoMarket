from django.urls import include, path
from rest_framework import routers

from .views import (AllCurrentDiscountLevelsView, MyCurrentDiscountLevelsView,
                    SellerDiscountLevelsView, SellerDiscountsCreateView,
                    SellerDiscountsRUDView)

discount_router = routers.DefaultRouter()
discount_router.register('all_seller_discounts',
                         SellerDiscountLevelsView,
                         basename='sellers-discounts')
discount_router.register('my_current_seller_discounts',
                         AllCurrentDiscountLevelsView,
                         basename='my-current-seller-discounts')
discount_router.register('my_current_dealer_levels',
                         MyCurrentDiscountLevelsView,
                         basename='my-current-dealer-discounts')


urlpatterns = [
    path('', include(discount_router.urls)),
    path('my_discount_levels',
         SellerDiscountsRUDView.as_view(),
         name='my-discount-levels'),
    path('create_discount_levels',
         SellerDiscountsCreateView.as_view(),
         name='create-discount-levels')
]
