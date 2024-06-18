from django.urls import path
from .views import RegisterUserView, CustomPasswordResetView

urlpatterns = [
    # modulos/inicio
    path('register/', RegisterUserView.as_view(), name='register'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
]