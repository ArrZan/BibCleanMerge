from django.shortcuts import redirect
from .models import Project, ProjectFiles, ProjectFilesEntries, Report


class AccessOwnerMixin:
    # Mixin para limitar el acceso de los proyectos únicamente para su propietario
    # Si se va a usar colaboradores, hay que cambiar esto o adaptarlo con los roles o permisos
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.check_permissions(obj):
            return redirect('list_projects')  # Redirige si no tiene permisos

        return super().dispatch(request, *args, **kwargs)

    def check_permissions(self, obj):
        # Si es una instancia de Project
        if isinstance(obj, Project):
            return self.request.user == obj.id_usuario
        # o si es una instancia de ProjectFiles o Report
        elif isinstance(obj, (ProjectFiles, Report)):
            return self.request.user == obj.id_project.id_usuario
        # o si es una instancia de ProjectFilesEntries
        elif isinstance(obj, ProjectFilesEntries):
            return self.request.user == obj.id_project_files.id_project.id_usuario
        else:
            return True  # Si el tipo de objeto no se especifica, permitir acceso por defecto
