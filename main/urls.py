from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static

from main import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url="/login/")),
    path('login/', include('apps.Login.urls')),
    path('project/', include('apps.Project.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
