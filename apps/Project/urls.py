from django.urls import path
from .views import ListProjectsView, ProcesamientoView


urlpatterns = [
    # modulos/inicio
    path('list/', ListProjectsView.as_view(), name='list_projects'),
    path('fast_process/', ProcesamientoView.as_view(), name='fast_process'),
]