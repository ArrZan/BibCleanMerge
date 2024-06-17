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

import apps.Project.libs as lb

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

# Abreviatura de palabras keywords
kw = 'keywords'
kwp = 'keywords-plus'
kwa = 'author_keywords'

tempKeys = {}  # Diccionario de los keywords por cada iteración del entry
listaKeys = {}  # Lista de los keywords sin repetir y contadas
listKw = {}  # Lista de keywords
listKwp = {}  # Lista de keywords plus
listKwa = {}  # Lista de author keywords


class ProcesamientoView(View):
    @staticmethod
    def format_bibtext_entry(entry, contTitle):
        # field, format, wrap or not
        field_order = [(u'author', '{{{0}}},\n', True),
                       (u'title', '{{{0}}},\n', True),
                       (u'journal', '{{{0}}},\n', True),
                       (u'volume', '{{{0}}},\n', True),
                       (u'number', '{{{0}}},\n', True),
                       (u'pages', '{{{0}}},\n', True),
                       (u'year', '{{{0}}},\n', True),
                       (u'doi', '{{{0}}},\n', False)]

        keys = set(entry.keys())
        extra_fields = keys.difference([f[0] for f in field_order])

        # No necesitamos esto en el entry
        extra_fields.remove('ENTRYTYPE')
        extra_fields.remove('ID')

        # Construimos la cadena de entrada y añadimos el código ordenado por año
        # ENTRYTYPE
        s = '@{type}{{{id},\ncode={{{code}}},\n\n'.format(type=entry['ENTRYTYPE'],
                                                          id=entry['ID'], code=contTitle)

        for field, fmt, wrap in field_order:
            if field in entry:
                # Este código comentado era para añadir un contador al título,
                # como ya lo pusimos en código, comento esto.
                if field == 'title':
                    s += lb.union(field, '{0} {1}'.format(contTitle, entry[field]))
                else:
                    s1 = '{0}='.format(field)
                    s2 = fmt.format(entry[field])
                    s3 = '{0}{1}'.format(s1, s2)
                    s += s3 + '\n'

        keyword = 0
        keywords_plus = 0
        author_keywords = 0

        # Aquí almacenamos todos los valores de los campos de un entry
        for field in extra_fields:
            if field in entry:

                if field != kw and field != kwp and field != kwa:
                    s += lb.union(field, entry[field])
                else:
                    if field == kw:
                        keyword = 1
                    elif field == kwp:
                        keywords_plus = 1
                    elif field == kwa:
                        author_keywords = 1

                    tempKeys[field] = entry[field]

        # Si no existe ningún tipo de keyword, entonces se crean los 3 campos
        if (keyword + keywords_plus + author_keywords) == 0:
            s += lb.union(kw, " ")  # Keywords
            s += lb.union(kwp, " ")  # keywords-plus
            s += lb.union(kwa, " ")  # author_keywords

        elif keyword == 0 and keywords_plus == 0 and author_keywords == 1:
            s += lb.union(kw, " ")
            s += lb.union(kwp, tempKeys[kwa])
            s += lb.union(kwa, " ")

        elif keyword == 0 and keywords_plus == 1 and author_keywords == 0:
            s += lb.union(kw, " ")
            s += lb.union(kwp, entry[kwp])
            s += lb.union(kwa, " ")

        elif keyword == 0 and keywords_plus == 1 and author_keywords == 1:
            s += lb.union(kw, " ")
            s += lb.union(kwp, tempKeys[kwp] + " ; " + tempKeys[kwa])
            s += lb.union(kwa, entry[kwa])

        elif keyword == 1 and keywords_plus == 0 and author_keywords == 0:
            s += lb.union(kw, " ")
            s += lb.union(kwp, tempKeys[kw])
            s += lb.union(kwa, " ")

        elif keyword == 1 and keywords_plus == 0 and author_keywords == 1:
            s += lb.union(kw, entry[kw])
            s += lb.union(kwp, tempKeys[kw] + " ; " + tempKeys[kwa])
            s += lb.union(kwa, entry[kwa])

        elif keyword == 1 and keywords_plus == 1 and author_keywords == 0:
            s += lb.union(kw, entry[kw])
            s += lb.union(kwp, tempKeys[kwp] + " ; " + tempKeys[kw])
            s += lb.union(kwa, " ")

        elif keyword == 1 and keywords_plus == 1 and author_keywords == 1:
            s += lb.union(kw, entry[kw])
            s += lb.union(kwp, tempKeys[kw] + " ; " + tempKeys[kwp] + " ; " + tempKeys[kwa])
            s += lb.union(kwa, entry[kwa])

        s += '\n}\n\n'
        return s

    # @staticmethod
    # def post(request, *args, **kwargs):
    #     # try:
    #     # Tomamos los archivos del POST
    #     files = request.FILES
    #
    #     files_bib = []  # Guardaremos todos los file acá
    #     # Iteramos los archivos para revalidar con el formato bib, sino, se omite el archivo
    #     for file_key, file_obj in files.items():
    #         if file_obj.name.endswith('.bib'):
    #             files_bib.append(file_obj)
    #
    #     # Si existen archivos..
    #     if files_bib:
    #         # Nombre y dirección de guardado del archivo
    #         name_date = datetime.now().strftime("%Y%m%d%H%M%S")
    #         nameFile = f'merged_{name_date}.bib'
    #         filePath = os.path.join(settings.MEDIA_BIB, nameFile)
    #
    #         # Guardamos todos las metricas de los datos
    #         count_entry_type_all = {'article': 0,
    #                                 'book': 0,
    #                                 'conference': 0,
    #                                 'others': 0,
    #                                 }
    #
    #         list_entry_all = []
    #         bib_database_all = []
    #
    #         for file in files_bib:
    #             fileBytes = file.read()
    #
    #             file_content = fileBytes.decode('utf-8')
    #             bib_database = bparser.loads(file_content)
    #
    #             # Sacamos una lista completa de todos las entradas con regex
    #             list_entry_id = re.findall(r'@\w+\{\s*(\S.+),', file_content)
    #
    #             obj_entries = ProjectFiles()
    #
    #             # Esta función es para sacar las cantidades de los tipos de entry
    #             count_entry_type = obj_entries.get_numbers_standard_types(bib_database.entries)
    #
    #             # ACUMULACIONES DE LOS ARCHIVOS
    #             for key, value in count_entry_type.items():
    #                 count_entry_type_all[key] += value
    #
    #             list_entry_all += list_entry_id
    #             bib_database_all.append(bib_database.entries)
    #
    #         print("*" * 50)
    #         print("*" * 50)
    #         print("*" * 50)
    #         print("Conteo GENERAL")
    #         # Esto es para TESTING (BORRAR)
    #         for entry_type, count in count_entry_type_all.items():
    #             print(f'{entry_type}: {count}')
    #
    #         # Hacemos una copia de lista extraída
    #         list_not_ID = list_entry_all.copy()
    #
    #         for entries in bib_database_all:
    #             for entry in entries:
    #                 entry_id = entry.get('ID', '')
    #
    #                 # Removemos de la copia los valores existentes del entrie y dejamos los que tienen inconsistencias
    #                 if entry_id in list_entry_all:
    #                     list_not_ID.remove(entry_id)
    #
    #         # Le da una estructura general a los entry's
    #         contTitle = 1
    #         for entries in bib_database_all:
    #             for entry in entries:
    #                 formatedEntry = ProcesamientoView.format_bibtext_entry(entry, contTitle)
    #                 contTitle += 1
    #
    #                 with open(filePath, 'a', encoding="utf8") as f:
    #                     f.write(formatedEntry)
    #
    #         data = {
    #             'count_typeEnt': count_entry_type_all,
    #             'count_entries': len(list_entry_all),
    #             'count_process': contTitle - 1,
    #             'count_duplicated': len(list_not_ID),
    #             'count_files': len(files_bib),
    #             'name_file': nameFile,
    #             'url_file': f'{settings.MEDIA_URL}/files/bib/{nameFile}'
    #         }
    #
    #         # Guardar count_entry_type en la sesión
    #         request.session['dataSet'] = data
    #
    #
    #     else:
    #         # Si no se encontraron archivos válidos en el formato BIB, devuelve un mensaje de error
    #         return JsonResponse({'error': 'No se encontraron archivos válidos en formato .bib'})
    #
    #     return JsonResponse({'redirect_url': reverse('report')})
    # #
    # # except Exception as e:
    # #     print("An exception occurred: ", e)
    # #
    # #     return JsonResponse({'error': 'Ocurrió un error al procesar los archivos'})

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

                # dict de metricas de los tipos de entrada
                count_entry_type_all = {}

                sheeps_ids = 0  # contador de los entry por regex
                white_sheeps_ids = 0  # contador de los entry por regex
                black_sheeps_ids = []  # lista de todas las obejas negras
    #               bib_database_all = []  # lista de entries (diccionarios)

                contTitle = 1
                for file in files_bib:

                    obj_entries = ProjectFile()
                    file_decode = obj_entries.decode_file(file)

                    obj_entries.extract_data_file(file_decode)
                    black_sheeps_ids += obj_entries.black_sheeps_ids

                    list_formated = {}
                    for entry in obj_entries.read_bibtext(file_decode):
                        # Obtengo el tipo de entrada y lo acumulo en el diccionario (conteo de tipos de entrada)
                        type_entry = obj_entries.get_type_entry(entry)

                        if type_entry not in count_entry_type_all:
                            count_entry_type_all[type_entry] = 1
                        else:
                            count_entry_type_all[type_entry] += 1

                        formatedEntry = ProcesamientoView.format_bibtext_entry(entry, contTitle)
                        # list_formated[contTitle] = ProcesamientoView.format_bibtext_entry(entry, contTitle)

                        # escribir todas las entradas formateadas de una vez al final
                        with open(file_Path, 'a', encoding="utf8") as f:
                            f.write(formatedEntry)

                        contTitle += 1


                    print("*" * 50)
                    print("Obejas: ", obj_entries.num_sheeps)
                    print("Obejas blancas: ", obj_entries.num_white_sheeps)
                    print("Obejas negras: ", obj_entries.num_black_sheeps)

                    if obj_entries.num_black_sheeps > 0:
                        filePath_black = os.path.join(settings.MEDIA_BIB, f'BSHEEP_{name_date}_{file.name}.txt')
                        with open(filePath_black, 'w') as f:
                            for id_ in obj_entries.black_sheeps_ids:
                                f.write(id_ + "\n")

                    sheeps_ids += obj_entries.num_sheeps
                    white_sheeps_ids += obj_entries.num_white_sheeps

                print("*" * 50)
                print("*" * 50)
                print("*" * 50)
                print("Conteo GENERAL")
                # Esto es para TESTING (BORRAR)
                for entry_type, count in count_entry_type_all.items():
                    print(f'{entry_type}: {count}')

                print("*" * 50)
                print("Obejas: ", sheeps_ids)
                print("Obejas blancas: ", white_sheeps_ids)
                print("Obejas negras: ", len(black_sheeps_ids))

                size_File = os.path.getsize(file_Path)  # Tamaño de archivo
                size_File /= (1024 * 1024)  # Tamaño de archivo en MB

                end_time = time.time()  # Tiempo de finalización de procesamiento
                elapsed_time = end_time - start_time  # Calcular tiempo transcurrido en segundos

                minu = int(elapsed_time // 60)
                sec = int(elapsed_time % 60)

                formatted_time = f"{minu:02}:{sec:02} seg"  # Tiempo formateado

                data = {
                    'count_typeEnt': count_entry_type_all,
                    'count_entries': sheeps_ids,
                    'count_process': contTitle - 1,
                    'count_duplicated': len(black_sheeps_ids),
                    'count_files': len(files_bib),
                    'name_file': name_File,
                    'size_file': f'{size_File:.2f} MB',
                    'url_file': f'{settings.MEDIA_URL}/files/bib/{name_File}',
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
