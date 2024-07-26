from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

from django.conf import settings
from django.conf.urls import handler404, handler500

from apps.Login.views import LoginUserView, Error404View, Error500View

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


# Esto servirá únicamente cuando el servidor esté en despliegue (DEBUG=False)
handler404 = Error404View.as_view()
handler500 = Error500View.as_view()
