import re

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
            # Tomamos los archivos del POST
            files = request.FILES

            files_bib = []  # Guardaremos todos los file acá
            # Iteramos los archivos para revalidar con el formato bib, sino, se omite el archivo
            for file_key, file_obj in files.items():
                if file_obj.name.endswith('.bib'):
                    files_bib.append(file_obj)

            # Si existen archivos..
            if files_bib:
                # Nombre y dirección de guardado del archivo
                name_date = datetime.now().strftime("%Y%m%d%H%M%S")
                nameFile = f'merged_{name_date}.bib'
                filePath = os.path.join(settings.MEDIA_BIB, nameFile)

                # dict de metricas de los tipos de entrada
                count_entry_type_all = {'article': 0,
                                        'book': 0,
                                        'conference': 0,
                                        'others': 0,
                                        }

                count_entry_all = 0  # contador de los entry por regex
                black_sheeps_ids = []  # lista de todas las obejas
                bib_database_all = []  # lista de entries (diccionarios)

                for file in files_bib:
                    filePath_black = os.path.join(settings.MEDIA_BIB, f'BSHEEP_{name_date}_{file.name}.txt')
                    obj_entries = ProjectFile(file)

                    # list_entry_id_all += obj_entries.sheeps_ids
                    bib_database_all.append(obj_entries.bib_database.entries)
                    count_entry_all += obj_entries.num_sheeps

                    for entry in obj_entries.bib_database.entries:
                        # Obtengo el tipo de entrada y lo acumulo en el diccionario
                        type_entry = obj_entries.get_type_entry(entry)
                        count_entry_type_all[type_entry] += 1

                        # Guardamos el id del entry
                        obj_entries.save_id_entry(entry)

                    black_sheeps_ids += (obj_entries.obtain_black_sheeps())

                    print("*" * 50)
                    print("Obejas: ", obj_entries.num_sheeps)
                    print("Obejas blancas: ", len(obj_entries.white_sheeps_ids))
                    print("Obejas negras: ", obj_entries.num_black_sheeps)

                    if obj_entries.num_black_sheeps > 0:
                        with open(filePath_black, 'w') as f:
                            for id_ in obj_entries.black_sheeps_ids:
                                f.write(id_ + "\n")

                print("*" * 50)
                print("*" * 50)
                print("*" * 50)
                print("Conteo GENERAL")
                # Esto es para TESTING (BORRAR)
                for entry_type, count in count_entry_type_all.items():
                    print(f'{entry_type}: {count}')

                # Le da una estructura general a los entry's
                contTitle = 1
                for entries in bib_database_all:
                    for entry in entries:
                        formatedEntry = ProcesamientoView.format_bibtext_entry(entry, contTitle)
                        contTitle += 1

                        with open(filePath, 'a', encoding="utf8") as f:
                            f.write(formatedEntry)

                data = {
                    'count_typeEnt': count_entry_type_all,
                    'count_entries': count_entry_all,
                    'count_process': contTitle - 1,
                    'count_duplicated': len(black_sheeps_ids),
                    'count_files': len(files_bib),
                    'name_file': nameFile,
                    'url_file': f'{settings.MEDIA_URL}/files/bib/{nameFile}'
                }

                # Guardar count_entry_type en la sesión
                request.session['dataSet'] = data

            else:
                # Si no se encontraron archivos válidos en el formato BIB, devuelve un mensaje de error
                return JsonResponse({'error': 'No hay archivos subidos o no tienen el formato bib!'})

            return JsonResponse({'redirect_url': reverse('report')})

        except Exception as e:
            print("An exception occurred: ", e)

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
