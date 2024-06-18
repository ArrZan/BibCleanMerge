from django.urls import path
from .views import ListProjectsView, ProcesamientoView, ReportsTempView, ReportDetailView


urlpatterns = [
    # modulos/inicio
    path('list/', ListProjectsView.as_view(), name='list_projects'),
    path('fast_process/', ProcesamientoView.as_view(), name='fast_process'),
    path('report/', ReportsTempView.as_view(), name='report'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
]