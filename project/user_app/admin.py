from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUserModel, MarketAvailableCarModel, DealerSearchCarSpecificationModel, \
    SellerCarParkModel, DealerCarParkModel, OfferModel, DealerPromoModel, SellerPromoModel
from .custom_user_form import CustomUserCreationForm, CustomUserChangeForm


class AmeUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUserModel
    list_display = ('email', 'username', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('email', 'username', 'is_staff', "is_verified")
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active',
                       'user_type', 'is_verified')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(CustomUserModel, AmeUserAdmin)

admin.site.register(MarketAvailableCarModel)

admin.site.register(DealerSearchCarSpecificationModel)

admin.site.register(DealerCarParkModel)

admin.site.register(SellerCarParkModel)

admin.site.register(OfferModel)

admin.site.register(DealerPromoModel)

admin.site.register(SellerPromoModel)
