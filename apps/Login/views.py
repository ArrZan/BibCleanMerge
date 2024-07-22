from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages

from django.http import JsonResponse
from django.utils import timezone

from .models import User
from django.views.generic import CreateView, UpdateView, TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from apps.Login.Mixins import ReturnHomeMixin
from apps.Login.forms import CustomUserCreationForm, CustomUserUpdateForm

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

        # Autenticar al usuario: se añade el request ya el axes lo requiere
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)

        return response



class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class UpdateUserView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/../../templates/user/update_user.html'
    model = User
    form_class = CustomUserUpdateForm

    def form_valid(self, form):
        if form.has_changed():
            messages.success(self.request, 'Los datos se actualizaron correctamente.')
            return super().form_valid(form)
        else:
            messages.warning(self.request, 'No se realizaron cambios.')
            return super().form_invalid(form)

    # el usuario solo pueda actualizar su propio perfil
    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_save'] = self.request.path
        context['title'] = 'Actualizar datos'
        context['action'] = 'update'
        return context


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'user/password_change.html'

    def get_success_url(self):
        return reverse_lazy('update_user', args=[self.request.user.id]) # Esta funcion permite lo qye es volver a
        # editar los datos personales con el id del usuario que se ha logueado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_changed'] = self.request.session.get('password_changed', False)
        return context

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user.username)
        user.created_by_admin = False
        user.save()

        messages.success(self.request, 'Cambio de contraseña exitoso')
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed'] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)



def account_locked(request):
    return render(request, 'registration/account_locked.html')