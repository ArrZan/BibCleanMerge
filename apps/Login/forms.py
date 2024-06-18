from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

"""
---------------------------------------------------------------------- Formulario de usuario
"""


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2','profile_picture')
