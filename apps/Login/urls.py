from django.urls import path
from .views import RegisterUserView, CustomPasswordResetView, UpdateUserView, UserPasswordChangeView, account_locked

urlpatterns = [
    # modulos/inicio
    path('register/', RegisterUserView.as_view(), name='register'),
    path('update_user/<int:pk>', UpdateUserView.as_view(), name='update_user'),
    path('password_change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('account_locked/', account_locked, name='account_locked'),
]