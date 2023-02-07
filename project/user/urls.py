from django.urls import include, path
from rest_framework import routers

from .views import (AutoDealerCreateView, AutoDealerReadOnlyView,
                    AutoDealerRUDView, AutoSellerCreateView,
                    AutoSellerReadOnlyView, AutoSellerRUDView,
                    CarBuyerCreateView, CarBuyerReadOnlyView, CarBuyerRUDView,
                    CustomUserCreationView, SelfUserProfileRUDView,
                    UserLoginView, UserLogoutView)

profile_RO_router = routers.DefaultRouter()
profile_RO_router.register(r'dealers', AutoDealerReadOnlyView, basename='dealer')
profile_RO_router.register(r'sellers', AutoSellerReadOnlyView, basename='seller')
profile_RO_router.register(r'buyers', CarBuyerReadOnlyView, basename='buyer')

urlpatterns = [
    path('registration/',
         CustomUserCreationView.as_view(),
         name='registration'),
    path('my_user_page/',
         SelfUserProfileRUDView.as_view(),
         name='user'),
    path('login/',
         UserLoginView.as_view(),
         name='login'),
    path('logout/',
         UserLogoutView.as_view(),
         name='logout'),
    path('create_dealer_profile/',
         AutoDealerCreateView.as_view(),
         name='dealer-creation'),
    path('create_seller_profile/',
         AutoSellerCreateView.as_view(),
         name='seller-creation'),
    path('create_buyer_profile/',
         CarBuyerCreateView.as_view(),
         name='buyer-creation'),
    path('my_dealer_profile/',
         AutoDealerRUDView.as_view(),
         name='dealer-profile'),
    path('my_seller_profile/',
         AutoSellerRUDView.as_view(),
         name='seller-profile'),
    path('my_buyer_profile/',
         CarBuyerRUDView.as_view(),
         name='buyer-profile'),
    path('', include(profile_RO_router.urls))
]
