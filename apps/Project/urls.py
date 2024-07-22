from django.urls import path
from .views import (ListProjectsView, ProcesamientoView, CreateProjectView, ManageProjectView,
                    ReportDetailView, DeleteProjectView, AutoSaveProjectView, UpdateProjectView,
                    AddFileView, UpdateProjectFilesView, DeleteProjectFileView, ListReportsView)


urlpatterns = [
    # Proyecto
    path('list/', ListProjectsView.as_view(), name='list_projects'),
    path('create/', CreateProjectView.as_view(), name='create_project'),
    path('edit_project/<int:pk>/', ManageProjectView.as_view(), name='manage_project'),
    path('update_project/<int:pk>/', UpdateProjectView.as_view(), name='update_project'),
    path('addFile/<int:pk>/', AddFileView.as_view(), name='add_files_project'),
    path('editVarFile/<int:pk>/', UpdateProjectFilesView.as_view(), name='edit_var_projectfiles'),
    path('delete/<int:pk>/', DeleteProjectView.as_view(), name='delete_project'),
    path('deleteFile/<int:pk>/', DeleteProjectFileView.as_view(), name='delete_projectfiles'),
    path('autosave/<int:project_id>/', AutoSaveProjectView.as_view(), name='autosave_project'),
    path('reports/<int:pk>/', ListReportsView.as_view(), name='list_reports'),


    # Procesamiento rápido
    path('fast_process/', ProcesamientoView.as_view(), name='fast_process'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),




]