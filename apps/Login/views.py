from django.contrib.auth.views import LoginView, PasswordResetView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import CreateView

from apps.Login.Mixins import ReturnHomeMixin
from apps.Login.forms import CustomUserCreationForm

"""
---------------------------------------------------------------------- Registrar usuario
"""


class LoginUserView(ReturnHomeMixin, LoginView):
    extra_context = {'title': 'BibCleanMerge - Inicio de sesión'}


"""
---------------------------------------------------------------------- Registrar usuario
"""


class RegisterUserView(ReturnHomeMixin, CreateView):
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('list_projects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de usuario'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        return response


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
