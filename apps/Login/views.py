from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import CreateView

from apps.Login.forms import CustomUserCreationForm

"""
---------------------------------------------------------------------- Logear Usuario
"""


class LoginUserView(LoginView):
    template_name = 'Login/login.html'
    success_url = 'inicio'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio de sesión'
        return context


    # def post(self, request):
    #     form = self.get_form()
    #     if form.is_valid():
    #         username = self.request.POST['username']
    #         password = self.request.POST['password']
    #
    #         user = authenticate(request, username=username, password=password)
    #
    #         if user is not None:
    #             exists_student = Estudiante.objects.filter(user_ptr=user).exists()
    #
    #             if exists_student:
    #                 login(request, user)
    #                 return redirect(self.success_url)
    #             else:
    #                 form.add_error(None, "Nombre de usuario o contraseña incorrectos.")
    #                 return self.form_invalid(form)
    #         else:
    #             form.add_error(None, "Nombre de usuario o contraseña incorrectos.")
    #             return self.form_invalid(form)
    #
    #     return self.form_invalid(form)
    #
    # def form_invalid(self, form):
    #     return render(self.request, self.template_name, {'form': form})


"""
---------------------------------------------------------------------- Registrar usuario
"""


class RegisterUserView(CreateView):
    model = User
    template_name = "Login/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect('explorarProyectos')
    #
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de usuario'

        return context

    # def form_valid(self, form):
    #
    #     return HttpResponseRedirect(self.success_url)
    #
    # def form_invalid(self, form):
    #     context = self.get_context_data(form=form)
    #
    #     return self.render_to_response(context)
