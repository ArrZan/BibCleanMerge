from django.shortcuts import redirect
from django.http import Http404


class ReturnHomeMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('list_projects')

        return super().dispatch(request, *args, **kwargs)


class AccessProjectMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.check_permissions(obj):
            return redirect('list_projects')
            # raise Http404("No tienes permisos para editar este objeto.")

        return super().dispatch(request, *args, **kwargs)

    def check_permissions(self, obj):
        if not self.request.user == obj.id_usuario:
            return False

        return True
