import re
import sys
import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, View

from apps.Project.models import ProjectFiles, ProjectFile
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
                # print(purge.entradas_unicas)

                # size_File = os.path.getsize(file_Path)  # Tamaño de archivo
                # size_File /= (1024 * 1024)  # Tamaño de archivo en MB

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
                    'size_file': f'000000 MB',
                    'url_file': f'0000000',
                    # 'size_file': f'{size_File:.2f} MB',
                    # 'url_file': f'{settings.MEDIA_URL}/files/bib/{name_File}',
                    'elapsed_time': formatted_time,
                }

                # Guardar count_entry_type en la sesión
                request.session['dataSet'] = data

            else:
                # Si no se encontraron archivos válidos en el formato BIB, devuelve un mensaje de error
                return JsonResponse({'error': 'No hay archivos subidos o no tienen el formato bib!'})

            return JsonResponse({'redirect_url': reverse('report')})

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


class ReportsTempView(TemplateView):
    template_name = 'Project/detail_report.html'

    # success_url = 'login'

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect(self.success_url)
    #
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte'
        context['dataReport'] = self.request.session.get('dataSet', {})
        return context
