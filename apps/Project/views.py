from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, View

"""
---------------------------------------------------------------------- Lista de proyectos
"""


class ListProjectsView(TemplateView):
    template_name = 'Project/list_Projects.html'
    success_url = 'login'

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect(self.success_url)
    #
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Proyectos'
        return context



"""
---------------------------------------------------------------------- Procesamiento rápido
"""


class ProcesamientoView(View):

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            # Tomamos los archivos
            files = request.FILES

            files_bib = []

            # Iteramos los archivos para revalidar con el formato bib, sino, se omite el archivo
            for file_key, file_obj in files.items():
                if file_obj.name.endswith('.bib'):
                    files_bib.append(file_obj)

            if files_bib:
                print(files_bib)
            #     # Analizar los archivos por trozos o completo???
            #     # Por trozos es más complejo; por completo es más fácil
            #     for file in files_bib:
            #         # Procesar el archivo en trozos
            #         with file.open() as f:
            #             while True:
            #                 chunk = f.read(1024)  # Leer 1KB de datos a la vez
            #                 if not chunk:
            #                     break

                # with open('output_file', 'ab') as output_file:
                #     output_file.write(chunk)
            else:
                # Si no se encontraron archivos válidos en el formato BIB, devuelve un mensaje de error
                return JsonResponse({'error': 'No se encontraron archivos válidos en formato .bib'})

            return JsonResponse({'message': 'Archivos recibidos correctamente'})

        except Exception as e:
            print("An exception occurred: ", e)

            return JsonResponse({'error': 'Ocurrió un error al procesar los archivos'})




