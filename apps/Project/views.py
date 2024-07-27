import json
import re
import sys
import time
import itertools


from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, IntegrityError
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, View, DetailView, DeleteView, UpdateView, CreateView
from django.contrib import messages
from django.db.models import F, Value, TextField, CharField, Case, Value, When
from django.db.models.functions import Coalesce

from main import settings
from .models import ProjectFile, Project, Report, ProjectFiles, ProjectFilesEntries, Base
from .Mixins import AccessOwnerMixin
from .forms import ProjectForm

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
---------------------------------------------------------------------- Creación de un proyecto
"""


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.id_usuario = self.request.user  # Asignamos el usuario actual al proyecto
        form.instance.prj_description = self.request.POST['prj_description'] if self.request.POST['prj_description'] else 'Sin descripción.'
        form.instance.prj_autosave = True  # Esto es para indicar que el usuario si guardó el proyecto

        try:
            response = super().form_valid(form)

            # Devolvemos la URL de redirección como parte de la respuesta JSON
            redirect_url = self.get_success_url()
            return JsonResponse({'redirect_url': redirect_url})
        except IntegrityError:
            return JsonResponse({'error': 'Ya existe un proyecto con este nombre.'})

    def form_invalid(self, form):
        # INTENTAR ENVIAR LOS ERRORES POR EL TÍTULO REPETIDO
        # errors = form.errors.as_json()
        # return JsonResponse({'errors': errors}, status=400)
        return HttpResponseRedirect(reverse_lazy('list_projects'))

    def get_success_url(self):
        # Redirigimos a la vista de gestión/edición del proyecto recién creado
        return reverse_lazy('manage_project', kwargs={'pk': self.object.pk})


"""
---------------------------------------------------------------------- Update de la variable de un ProjectFile  
"""


class UpdateProjectFilesView(LoginRequiredMixin, AccessOwnerMixin, UpdateView):
    model = ProjectFiles

    def post(self, request, *args, **kwargs):
        projectFile_id = kwargs['pk']  # Obtenemos el id del proyecto del parámetro kwargs de la url
        try:
            projectFile = ProjectFiles.objects.get(id=projectFile_id)
            projectFile.pf_search_criteria = self.request.POST['pf_search_criteria']
            projectFile.save()  # Guardamos

            return JsonResponse({'message': 'Variable actualizada.'})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Proyecto de archivo no encontrado.'})


"""
---------------------------------------------------------------------- Update de un proyecto
"""


class UpdateProjectView(LoginRequiredMixin, AccessOwnerMixin, UpdateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):

        try:
            project = self.get_object()

            for field, value in form.cleaned_data.items():
                # Obtenemos el valor sin alterar del campo iterado
                current_value = getattr(project, field)
                # Consultamos si hubo algún cambio
                if value != current_value:
                    # __dict__ nos devuelve un diccionario de los atributos de la instancia project,
                    # entonces modificamos el campo para actualizarlo
                    project.__dict__[field] = value

            project.save()

            return JsonResponse({'message': 'Proyecto actualizado.'})
        except IntegrityError:
            return JsonResponse({'error': 'Nombre ya en uso.'})

    def form_invalid(self, form):
        # En caso de errores de validación, devolvemos un JSON con los errores
        errors = form.errors.as_json()
        print(errors)
        return JsonResponse({'errors': json.loads(errors)})


"""
---------------------------------------------------------------------- Gestión o edición de los archivos del proyecto
"""


class ManageProjectView(LoginRequiredMixin, AccessOwnerMixin, DetailView):
    template_name = 'Project/edit_project.html'
    model = Project
    success_url = reverse_lazy('manage_project')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.object

        # Obtenemos los archivos asociados a este proyecto
        # Annotate es para agregrar una nueva columna (search_criteria)
        # Coalesce es una función que devuelve el registro no nulo, sino, devolverá N/A
        # El ouutpt_fuield es para validación de que es un tipo string
        project_files = project.files.annotate(
            search_criteria=Coalesce(F('pf_search_criteria'), Value('N/A'), output_field=TextField()),
        ).values('id', 'name_file', 'search_criteria')

        # Lista para almacenar todas las entradas de archivos
        all_entries = []
        for project_file in project_files:
            # Obtener el objeto Base correspondiente
            project_file_obj = Base.objects.get(id=project_file['id'])
            # Modificamos el nombre del archivo utilizando get_name_split()
            project_file['name_file'] = project_file_obj.get_name_split()

            # Llamamos nomás los 30 primeros registros
            all_entries.append(ProjectFilesEntries.objects.filter(id_project_files_id=project_file['id']).order_by('id')[:30])

        context['project_files'] = project_files
        context['all_entries'] = all_entries

        context['title'] = 'Gestión de Proyecto'
        return context


"""
---------------------------------------------------------------------- Eliminación de un archivo de un proyecto
"""


class DeleteProjectFileView(LoginRequiredMixin, AccessOwnerMixin, DeleteView):
    model = ProjectFiles

    def form_valid(self, form):
        projectFile = get_object_or_404(ProjectFiles, pk=self.kwargs['pk'])
        try:
            # Borramos priimero el archivo y luego el objeto
            projectFile.delete_File()
            projectFile.delete()

            return JsonResponse({'message': 'Archivo eliminado.'})
        except Exception as e:
            return JsonResponse({'error': 'Ocurrió un error.'})


"""
---------------------------------------------------------------------- Eliminación de un REPORTE de un proyecto
"""


class DeleteProjectReportView(LoginRequiredMixin, AccessOwnerMixin, DeleteView):
    model = Report

    def form_valid(self, form):
        report = get_object_or_404(Report, pk=self.kwargs['pk'])
        try:
            # Borramos priimero el archivo y luego el objeto
            report.delete_File()
            report.delete()

            return JsonResponse({'message': 'Reporte eliminado.'})

        except Exception as e:
            return JsonResponse({'error': 'Ocurrió un error.'})


"""
---------------------------------------------------------------------- Eliminación de un proyectos
"""


class DeleteProjectView(LoginRequiredMixin, AccessOwnerMixin, DeleteView):
    model = Project

    def form_valid(self, form):
        try:
            # Obtenemos el objeto a eliminar
            project = self.get_object()

            # Eliminamos todos los archivos asociados
            project.deleteFiles()

            # Eliminamos el objeto
            project.delete()

            # Devolvemos una respuesta JSON indicando éxito
            return JsonResponse({'message': 'Proyecto eliminado.'})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Error: Proyecto no encontrado.'})


"""
---------------------------------------------------------------------- Detalle de un reporte
"""


class ReportDetailView(LoginRequiredMixin, AccessOwnerMixin, DetailView):
    template_name = 'Project/detail_report.html'
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Reporte de proceso'

        # Obtener la URL anterior (referer)
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            context['previous_page_url'] = referer
        else:
            # Si no hay URL anterior, regresar a la lista de proyectos
            context['previous_page_url'] = reverse('list_projects')

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
---------------------------------------------------------------------- Detalle de un reporte
"""


class ListReportsView(LoginRequiredMixin, ListView):
    template_name = 'Project/list_reports.html'
    model = Report
    context_object_name = 'reports'

    def get_queryset(self):
        # Obtenemos el proyecto
        project = get_object_or_404(Project, id=self.kwargs['pk'])
        # Filtramos los reportes de este proyecto
        return Report.objects.filter(id_project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['pk'])
        context['title'] = 'Reportes'
        return context


"""
---------------------------------------------------------------------- Procesado
"""


class AddFileView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            start_time = time.time()  # Tiempo de inicio de procesamiento

            files = request.FILES

            files_bib = []  # Guardaremos todos los file acá
            # Iteramos los archivos para revalidar con el formato bib, sino, se omite el archivo
            for file_key, file_obj in files.items():
                if file_obj.name.endswith('.bib'):
                    files_bib.append(file_obj)

            if files_bib:
                all_entries = []  # Lista para almacenar todos los entries de todos los archivos
                project_id = kwargs['pk']

                project = Project.objects.get(pk=project_id)

                for file in files_bib:
                    obj = ProjectFile()
                    file_dec = obj.decode_file(file)

                    name_date = datetime.now().strftime("%H%M%S")
                    fileName = f'({self.request.user.id})_{name_date}___{file.name}'

                    # Guardar el archivo en 'media/files/bib'
                    file_path = os.path.join(settings.MEDIA_ROOT, 'files', 'bib', fileName)
                    with open(file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)

                    newFile = ProjectFiles.objects.create(
                        id_project=project,
                        name_file=fileName,
                    )

                    fields = ['title', 'author', 'year', 'keywords', 'journal',
                              'volume', 'number', 'pages', 'doi']

                    entries = []  # Almacenamos los entrys del file
                    count = 0
                    with transaction.atomic():
                        for entry in obj.read_bibtext_with_regex(file_dec, 30):
                            entry_dict = {field: entry.get(field, 'N/A') for field in fields}
                            entries.append(entry_dict)

                            newEntrie = ProjectFilesEntries.objects.create(
                                id_project_files=newFile,
                                pfe_title=entry.get('title', 'N/A'),
                                pfe_authors=entry.get('author', 'N/A'),
                                pfe_year=entry.get('year', 'N/A'),
                                pfe_keywords=entry.get('keywords', 'N/A'),
                                pfe_journal=entry.get('journal', 'N/A'),
                                pfe_volume=entry.get('volume', 'N/A'),
                                pfe_number=entry.get('number', 'N/A'),
                                pfe_pages=entry.get('pages', 'N/A'),
                                pfe_doi=entry.get('doi', 'N/A'),
                            )
                            count += 1

                            if count >= 30:
                                break

                        all_entries.append({'key': newFile.id, 'entries': entries, 'name': file.name})

                formatted_time = Report.generate_timestamp(start_time)  # Tiempo formateado

                return JsonResponse({'entries': all_entries, 'message': 'Todo bien', 'time_elapsed': formatted_time})
            else:
                return JsonResponse({'message': 'No se encontraron archivos .bib válidos'}, status=400)

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

            transaction.rollback()  # Rollback de la transacción en caso de error

            return JsonResponse({'error': 'Ocurrió un error en el servidor!',
                                 'error_message': str(e)}, status=500)


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

                # Crear el proyecto con un título y descripción predeterminados
                new_project = Project.objects.create(
                    id_usuario=request.user,
                    prj_name=f'Proyecto recuperado [{name_date}]',
                    prj_description='Sin descripción.',
                )

                purge = PurgeData()

                for file in files_bib:

                    obj_entries = ProjectFile()

                    file_decode = obj_entries.decode_file(file)

                    name_date2 = datetime.now().strftime("%H%M%S")
                    fileName = f'({request.user.id})_{name_date2}___{file.name}'

                    # Guardar el archivo en 'media/files/bib'
                    file_path = os.path.join(settings.MEDIA_ROOT, 'files', 'bib', fileName)
                    with open(file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)

                    newFile = ProjectFiles.objects.create(
                        id_project=new_project,
                        name_file=fileName,
                    )

                    obj_entries.extract_data_file(file_decode)
                    purge.black_sheeps_ids += obj_entries.black_sheeps_ids

                    # obj_entries.unificar_entradas(file_decode, purge)

                    for entry in obj_entries.read_bibtext(file_decode):
                        # purge = PurgeData()
                        # Obtengo el tipo de entrada y lo acumulo en el diccionario (conteo de tipos de entrada)
                        type_entry = obj_entries.get_type_entry(entry)

                        if type_entry not in purge.count_entry_type_all:
                            purge.count_entry_type_all[type_entry] = 1
                        else:
                            purge.count_entry_type_all[type_entry] += 1

                        formatedEntry = purge.format_bibtext_entry(entry)

                        # escribir todas las entradas formateadas de una vez al final
                        with open(file_Path, 'a', encoding="utf8") as f:
                            f.write(formatedEntry)

                        newEntrie = ProjectFilesEntries.objects.create(
                            id_project_files=newFile,
                            pfe_title=entry.get('title', 'N/A'),
                            pfe_authors=entry.get('author', 'N/A'),
                            pfe_year=entry.get('year', 'N/A'),
                            pfe_keywords=entry.get('keywords', 'N/A'),
                            pfe_journal=entry.get('journal', 'N/A'),
                            pfe_volume=entry.get('volume', 'N/A'),
                            pfe_number=entry.get('number', 'N/A'),
                            pfe_pages=entry.get('pages', 'N/A'),
                            pfe_doi=entry.get('doi', 'N/A'),
                        )
                        print(purge.contArt - 1)

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

                # Crear el reporte asociado a este proyecto
                newReport = Report.objects.create(
                    id_project=new_project,
                    name_file=name_File,
                    articles=purge.count_entry_type_all.get('article', 0),
                    conferences=purge.count_entry_type_all.get('conference', 0),
                    papers=purge.count_entry_type_all.get('paper', 0),
                    books=purge.count_entry_type_all.get('book', 0),
                    others=purge.count_entry_type_all.get('others', 0),
                    rep_n_articles_files=purge.sheeps_ids,
                    rep_n_processed=purge.contArt - 1,
                    rep_n_duplicate=len(purge.black_sheeps_ids),
                    rep_duration_seg=elapsed_time,
                    rep_n_files=len(files_bib),
                    rep_size_file=size_File_bytes,
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



"""
---------------------------------------------------------------------- Procesamiento rápido
"""


class ProcesamientoView2(LoginRequiredMixin, View):
    model = Project

    def post(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        try:
            project = Project.objects.get(pk=project_id)

            # Recogemos los archivos guardados
            projectFiles = project.files.all()

            start_time = time.time()  # Tiempo de inicio de procesamiento

            # Nombre y dirección de guardado del archivo
            name_date = datetime.now().strftime("%Y%m%d%H%M%S")
            name_File = f'merged_{name_date}.bib'
            file_Path = os.path.join(settings.MEDIA_BIB, name_File)

            purge = PurgeData()
            print("Antes de sumar", len(purge.black_sheeps_ids))
            print("Antes de sumar", purge.black_sheeps_ids)

            print("Cantidad de archivos", len(projectFiles))

            for projectFile in projectFiles:
                projectFile_path = os.path.join(settings.MEDIA_BIB, projectFile.name_file)
                # Abrir el archivo en modo lectura
                with open(projectFile_path, 'r', encoding='utf-8') as file:
                    # Leer el contenido del archivo
                    file_content = file.read()

                obj_entries = ProjectFile()

                # file_decode = obj_entries.decode_file(file)

                obj_entries.extract_data_file(file_content)
                print("Antes de sumar", len(purge.black_sheeps_ids))
                purge.black_sheeps_ids += obj_entries.black_sheeps_ids
                print("Depsues de sumar", len(purge.black_sheeps_ids))

                for entry in obj_entries.read_bibtext(file_content):
                    # Obtengo el tipo de entrada y lo acumulo en el diccionario (conteo de tipos de entrada)
                    type_entry = obj_entries.get_type_entry(entry)

                    if type_entry not in purge.count_entry_type_all:
                        purge.count_entry_type_all[type_entry] = 1
                    else:
                        purge.count_entry_type_all[type_entry] += 1

                    formatedEntry = purge.format_bibtext_entry(entry)

                    # escribir todas las entradas formateadas de una vez al final
                    with open(file_Path, 'a', encoding="utf8") as f:
                        f.write(formatedEntry)

                print("*" * 50)
                print("Obejas: ", obj_entries.num_sheeps)
                print("Obejas blancas: ", obj_entries.num_white_sheeps)
                print("Obejas negras: ", obj_entries.num_black_sheeps)

                # if obj_entries.num_black_sheeps > 0:
                #     filePath_black = os.path.join(settings.MEDIA_BIB, f'BSHEEP_{name_date}_{file.name}.txt')
                #     with open(filePath_black, 'w') as f:
                #         for id_ in obj_entries.black_sheeps_ids:
                #             f.write(id_ + "\n")

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

            # minu = int(elapsed_time // 60)
            # sec = int(elapsed_time % 60)

            # formatted_time = f"{minu:02}:{sec:02} seg"  # Tiempo formateado

            # data = {
            #     'count_typeEnt': purge.count_entry_type_all,
            #     'count_entries': purge.sheeps_ids,
            #     'count_process': purge.contArt - 1,
            #     'count_duplicated': len(purge.black_sheeps_ids),
            #     'count_files': len(projectFiles),
            #     'name_file': name_File,
            #     # 'size_file': f'000000 MB',
            #     # 'url_file': f'0000000',
            #     'size_file': f'{size_File:.2f} MB',
            #     'url_file': f'{settings.MEDIA_URL}/files/bib/{name_File}',
            #     'elapsed_time': formatted_time,
            # }

            print('Cantidad de n dup: ', len(purge.black_sheeps_ids))
            # Crear el reporte asociado a este proyecto
            newReport = Report.objects.create(
                id_project=project,
                name_file=name_File,
                articles=purge.count_entry_type_all.get('article', 0),
                conferences=purge.count_entry_type_all.get('conference', 0),
                papers=purge.count_entry_type_all.get('paper', 0),
                books=purge.count_entry_type_all.get('book', 0),
                others=purge.count_entry_type_all.get('others', 0),
                rep_n_articles_files=purge.sheeps_ids,
                rep_n_processed=purge.contArt - 1,
                rep_n_duplicate=len(purge.black_sheeps_ids),
                rep_duration_seg=elapsed_time,
                rep_n_files=len(projectFiles),
                rep_size_file=size_File_bytes,
            )

            # Redirigimos a la vista de detalle del reporte
            return JsonResponse({'redirect_url': reverse('report_detail', kwargs={'pk': newReport.id})})

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

