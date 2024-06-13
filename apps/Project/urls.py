from django.urls import path
from .views import ListProjectsView, ProcesamientoView, ReportsTempView


urlpatterns = [
    # modulos/inicio
    path('list/', ListProjectsView.as_view(), name='list_projects'),
    path('fast_process/', ProcesamientoView.as_view(), name='fast_process'),
    path('report/', ReportsTempView.as_view(), name='report'),
]