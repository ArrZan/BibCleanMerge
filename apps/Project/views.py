import re
import sys
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, View, DetailView, DeleteView, UpdateView, CreateView
from django.contrib import messages

from apps.Login.Mixins import AccessProjectMixin
from apps.Project.forms import ProjectForm
from apps.Project.models import ProjectFile, Project, Report
from main import settings

# Importanción de librería para parsear los archivos bib
import bibtexparser as bparser
import unidecode as ud
import os
from datetime import datetime

from apps.Project.libs import PurgeData

"""
---------------------------------------------------------------------- Lista de proyectos
"""


class ListProjectsView(LoginRequiredMixin, ListView):
    template_name = 'Project/list_Projects.html'
    model = Project

    def get_queryset(self):
        return Project.objects.filter(id_usuario=self.request.user.id).order_by('-prj_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Proyectos'
        return context


"""
---------------------------------------------------------------------- Creación de un proyecto
"""


class CreateProjectView(LoginRequiredMixin, CreateView):
    template_name = 'Project/list_Projects.html'
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.id_usuario = self.request.user  # Asignamos el usuario actual al proyecto
        form.instance.prj_autosave = True  # Esto es para indicar que el usuario si guardó el proyecto

        return super().form_valid(form)

    def get_success_url(self):
        # Redirigimos a la vista de gestión/edición del proyecto recién creado
        return reverse_lazy('edit_project', kwargs={'pk': self.object.pk})


"""
---------------------------------------------------------------------- Gestión o edición de un proyecto
"""


class EditProjectView(LoginRequiredMixin, DetailView):
    template_name = 'Project/edit_project.html'
    model = Project
    fields = ['prj_name', 'prj_description']  # Campos del modelo que incluimos en el formulario
    success_url = reverse_lazy('edit_project')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestión de Proyecto'
        return context


"""
---------------------------------------------------------------------- Eliminación de un proyectos
"""


class DeleteProjectView(LoginRequiredMixin, AccessProjectMixin, DeleteView):
    model = Project

    def form_valid(self, form):
        try:
            # Obtenemos el objeto a eliminar
            project = self.get_object()

            # Eliminamos el objeto
            project.delete()

            # Devolvemos una respuesta JSON indicando éxito
            return JsonResponse({'message': 'Proyecto eliminado.'})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Error: Proyecto no encontrado.'}, status=404)


"""
---------------------------------------------------------------------- Autoguardado de un proyecto
"""


class AutoSaveProjectView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs['project_id']  # Obtenemos el id del proyecto del parámetro kwargs de la url
        try:
            project = Project.objects.get(id=project_id)
            project.prj_autosave = True  # Actualiza el campo autoguardado a True
            project.save()  # Guardamos
            return JsonResponse({'message': 'Proyecto guardado.'})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Proyecto no encontrado.'}, status=404)


"""
---------------------------------------------------------------------- Detalle de un reporte
"""


class ReportDetailView(LoginRequiredMixin, AccessProjectMixin, DetailView):
    template_name = 'Project/detail_report.html'
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Reporte de proceso'
        return context

    def check_permissions(self, obj):
        report = self.get_object()
        # Preguntamos si tiene permismo ese usuario a ese reporte
        # Si se desea controlar grupos para un proyecto, esto debe de cambiar
        # Implicaría revisar si ese usuario es colaborador de ese proyecto
        if not self.request.user.id == report.id_project.id_usuario.id:
            return False
        return True


"""
---------------------------------------------------------------------- Procesamiento rápido
"""


class ProcesamientoView(LoginRequiredMixin, View):

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            start_time = time.time()  # Tiempo de inicio de procesamiento

            # Tomamos los archivos del POST
            files = request.FILES

            files_bib = []  # Guardaremos todos los file acá
            # Iteramos los archivos para revalidar con el formato bib, sino, se omite el archivo
            for file_key, file_obj in files.items():
                if file_obj.name.endswith('.bib'):
                    files_bib.append(file_obj)

            # Si existen archivos...
            if files_bib:
                # Nombre y dirección de guardado del archivo
                name_date = datetime.now().strftime("%Y%m%d%H%M%S")
                name_File = f'merged_{name_date}.bib'
                file_Path = os.path.join(settings.MEDIA_BIB, name_File)

                purge = PurgeData()

                for file in files_bib:

                    obj_entries = ProjectFile()
                    file_decode = obj_entries.decode_file(file)

                    obj_entries.extract_data_file(file_decode)
                    purge.black_sheeps_ids += obj_entries.black_sheeps_ids

                    obj_entries.unificar_entradas(file_decode, purge)

                    # for entry in obj_entries.read_bibtext(file_decode):
                    #     purge = PurgeData()
                    #     # Obtengo el tipo de entrada y lo acumulo en el diccionario (conteo de tipos de entrada)
                    #     type_entry = obj_entries.get_type_entry(entry)
                    #
                    #     if type_entry not in count_entry_type_all:
                    #         count_entry_type_all[type_entry] = 1
                    #     else:
                    #         count_entry_type_all[type_entry] += 1
                    #
                    #     formatedEntry = purge.format_bibtext_entry(entry, contArt)
                    #
                    #     # escribir todas las entradas formateadas de una vez al final
                    #     with open(file_Path, 'a', encoding="utf8") as f:
                    #         f.write(formatedEntry)
                    #
                    #     contArt += 1

                    print("*" * 50)
                    print("Obejas: ", obj_entries.num_sheeps)
                    print("Obejas blancas: ", obj_entries.num_white_sheeps)
                    print("Obejas negras: ", obj_entries.num_black_sheeps)

                    if obj_entries.num_black_sheeps > 0:
                        filePath_black = os.path.join(settings.MEDIA_BIB, f'BSHEEP_{name_date}_{file.name}.txt')
                        with open(filePath_black, 'w') as f:
                            for id_ in obj_entries.black_sheeps_ids:
                                f.write(id_ + "\n")

                    purge.sheeps_ids += obj_entries.num_sheeps
                    purge.white_sheeps_ids += obj_entries.num_white_sheeps

                print("*" * 50)
                print("*" * 50)
                print("*" * 50)
                print("Conteo GENERAL")
                # Esto es para TESTING (BORRAR)
                for entry_type, count in purge.count_entry_type_all.items():
                    print(f'{entry_type}: {count}')

                print("*" * 50)
                print("Obejas: ", purge.sheeps_ids)
                print("Obejas blancas: ", purge.white_sheeps_ids)
                print("Obejas negras: ", len(purge.black_sheeps_ids))
                print("*" * 50)
                print("Entradas únicas: ")

                for entry, value in purge.entradas_unicas.items():
                    with open(file_Path, 'a', encoding="utf8") as f:
                        f.write(f'{entry}: {value}\n')

                size_File_bytes = os.path.getsize(file_Path)  # Tamaño de archivo
                size_File = size_File_bytes / (1024 * 1024)  # Tamaño de archivo en MB

                end_time = time.time()  # Tiempo de finalización de procesamiento
                elapsed_time = end_time - start_time  # Calcular tiempo transcurrido en segundos

                minu = int(elapsed_time // 60)
                sec = int(elapsed_time % 60)

                formatted_time = f"{minu:02}:{sec:02} seg"  # Tiempo formateado

                data = {
                    'count_typeEnt': purge.count_entry_type_all,
                    'count_entries': purge.sheeps_ids,
                    'count_process': purge.contArt - 1,
                    'count_duplicated': len(purge.black_sheeps_ids),
                    'count_files': len(files_bib),
                    'name_file': name_File,
                    # 'size_file': f'000000 MB',
                    # 'url_file': f'0000000',
                    'size_file': f'{size_File:.2f} MB',
                    'url_file': f'{settings.MEDIA_URL}/files/bib/{name_File}',
                    'elapsed_time': formatted_time,
                }

                # Guardar count_entry_type en la sesión
                # request.session['dataSet'] = data

                # Crear el proyecto con un título y descripción predeterminados
                new_project = Project.objects.create(
                    id_usuario=request.user,
                    prj_name='Proyecto',
                    prj_description='Sin descripción.',
                )

                # Crear el reporte asociado a este proyecto
                newReport = Report.objects.create(
                    id_project=new_project,
                    rep_p_articles=purge.count_entry_type_all.get('article', 0),
                    rep_p_conferences=purge.count_entry_type_all.get('conference', 0),
                    rep_p_papers=purge.count_entry_type_all.get('paper', 0),
                    rep_p_books=purge.count_entry_type_all.get('book', 0),
                    rep_p_others=purge.count_entry_type_all.get('others', 0),
                    rep_n_articles_files=purge.sheeps_ids,
                    rep_n_processed=purge.contArt - 1,
                    rep_n_duplicate=len(purge.black_sheeps_ids),
                    rep_duration_seg=elapsed_time,
                    rep_n_files=len(files_bib),
                    rep_size_file=size_File_bytes,
                    rep_name_file_merged=name_File
                )

                # Redirigimos a la vista de detalle del reporte
                return JsonResponse({'redirect_url': reverse('report_detail', kwargs={'pk': newReport.id})})

            else:
                # Si no se encontraron archivos válidos en el formato BIB, devuelve un mensaje de error
                return JsonResponse({'error': 'No hay archivos subidos o no tienen el formato bib!'})

            # return JsonResponse({'redirect_url': reverse('report')})

        except Exception as e:
            # Depuración
            tipo_excepcion, valor_excepcion, tb = sys.exc_info()
            print(f"Tipo de excepción: {tipo_excepcion}")
            print(f"Valor de la excepción: {valor_excepcion}")
            print("Traceback:")
            traceback_details = {
                'filename': tb.tb_frame.f_code.co_filename,
                'line': tb.tb_lineno,
                'name': tb.tb_frame.f_code.co_name,
            }
            for name, value in traceback_details.items():
                print(f"  {name}: {value}")

            return JsonResponse({'error': 'Ocurrió un error en el servidor!',
                                 'error_message': str(e)}, status=500)


