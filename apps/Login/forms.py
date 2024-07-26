import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User

"""
---------------------------------------------------------------------- Formulario de usuario
"""


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2','profile_picture')

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email','profile_picture']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise ValidationError('El nombre no debe contener números.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z]+$', last_name):
            raise ValidationError('El apellido no debe contener números.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not forms.EmailField().clean(email):
            raise ValidationError('Introduce una dirección de correo electrónico válida.')
        return email

