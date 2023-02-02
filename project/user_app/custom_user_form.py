from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUserModel


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUserModel
        fields = ('email', 'username', 'password', 'user_type', 'is_active', 'is_verified')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUserModel
        fields = ('email', 'username', 'user_type', 'is_verified', 'is_active')
