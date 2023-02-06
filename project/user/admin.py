from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .custom_user_form import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUserModel


class CustomUserAdmin(UserAdmin):
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


admin.site.register(CustomUserModel, CustomUserAdmin)
