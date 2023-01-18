from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AmeUserModel
from .ameuser_form import CustomUserCreationForm, CustomUserChangeForm


class AmeUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = AmeUserModel
    list_display = ('email', 'username', 'is_staff', 'is_active',)
    list_filter = ('email', 'username', 'is_staff', )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
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


admin.site.register(AmeUserModel, AmeUserAdmin)
