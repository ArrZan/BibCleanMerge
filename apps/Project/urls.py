from django.urls import path
from .views import (ListProjectsView, ProcesamientoView, CreateProjectView, EditProjectView,
                    ReportDetailView, DeleteProjectView, AutoSaveProjectView, UpdateProjectView)


urlpatterns = [
    # Proyecto
    path('list/', ListProjectsView.as_view(), name='list_projects'),
    path('create/', CreateProjectView.as_view(), name='create_project'),
    path('edit_project/<int:pk>/', EditProjectView.as_view(), name='edit_project'),
    path('update_project/<int:pk>/', UpdateProjectView.as_view(), name='update_project'),
    path('delete/<int:pk>/', DeleteProjectView.as_view(), name='delete_project'),
    path('autosave/<int:project_id>/', AutoSaveProjectView.as_view(), name='autosave_project'),


    # Procesamiento rápido
    path('fast_process/', ProcesamientoView.as_view(), name='fast_process'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),




]