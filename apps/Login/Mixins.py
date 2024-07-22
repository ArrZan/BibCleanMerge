from django.shortcuts import redirect


class ReturnHomeMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('list_projects')

        return super().dispatch(request, *args, **kwargs)
