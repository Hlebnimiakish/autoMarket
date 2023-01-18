from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import AmeUserModel


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = AmeUserModel
        fields = ('email', 'username', 'password', 'user_type', 'is_active', 'is_verified')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = AmeUserModel
        fields = ('email', 'username', 'user_type', 'is_verified', 'is_active')
