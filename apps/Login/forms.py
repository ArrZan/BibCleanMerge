from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
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
        # Validación para asegurarse de que no haya números en el first_name
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("El nombre no puede contener números.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Validación para asegurarse de que no haya números en el last_name
        if any(char.isdigit() for char in last_name):
            raise forms.ValidationError("El apellido no puede contener números.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validaciones para el campo 'email'
        # Ejemplo: Verificar que sea un formato de email válido
        if not email:
            raise forms.ValidationError("Debe proporcionar una dirección de correo electrónico.")
        return email

