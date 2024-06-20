from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

from django.conf import settings

from apps.Login.views import LoginUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url="accounts/login")),
    path('accounts/login/', LoginUserView.as_view(), name='custom_login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/registration/', include('apps.Login.urls')),
    path('project/', include('apps.Project.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
