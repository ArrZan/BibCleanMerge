import os
from datetime import datetime

from django.db import models

from bibtexparser import bibdatabase as bd

import bibtexparser as bparser

import re

from unidecode import unidecode

from apps.Login.models import User
from apps.Project.libs import PurgeData
from main import settings


class Project(models.Model):
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    prj_name = models.CharField(max_length=50)
    prj_description = models.TextField(default='Sin descripción', null=True, blank=True)
    prj_date = models.DateField(auto_now_add=True)  # Permite agregar la fecha actual al registrar
    prj_last_modified = models.DateField(auto_now=True)  # Permite agregar la fecha al modificar
    prj_autosave = models.BooleanField(default=False)  # Nos permite saber si el proyecto se autoguardó

    def __str__(self):
        return self.prj_name

    def get_last_report(self):

        if self.reports.values():
            reports = self.reports.values('rep_name_file_merged', 'rep_n_articles_files', 'id').last()
            reports['rep_name_file_merged'] = f'{settings.MEDIA_URL}/files/bib/{reports['rep_name_file_merged']}'
            reports['disabled'] = ''
        else:
            reports = {
                'rep_name_file_merged': '#',
                'rep_n_articles_files': 0,
                'id': 0,
                'disabled': 'btn-a-disabled',
            }

        return reports


class ProjectFiles(models.Model):
    id_project_files = models.AutoField(primary_key=True)
    id_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    pf_name_file = models.CharField(max_length=100)
    pf_p_articles = models.IntegerField()
    pf_p_conferences = models.IntegerField()
    pf_p_papers = models.IntegerField()
    pf_p_books = models.IntegerField()
    pf_p_others = models.IntegerField()
    pf_n_entries_file = models.IntegerField()

    def __str__(self):
        return self.pf_name_file


# class ProjectFilesEntries(models.Model):
#     id_project_files_entries = models.AutoField(primary_key=True)
#     id_project_files = models.ForeignKey(ProjectFiles, on_delete=models.CASCADE)
#     pfe_title = models.CharField(max_length=100)
#     pfe_authors = models.CharField(max_length=255)
#     pfe_journal = models.CharField(max_length=255)
#     pfe_volume = models.IntegerField()
#     pfe_keywords = models.TextField()
#     pfe_number = models.IntegerField()
#     pfe_pages = models.IntegerField()
#     pfe_year = models.IntegerField()
#     pfe_doi = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.pfe_title
#

class Report(models.Model):
    id_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    rep_p_articles = models.IntegerField()
    rep_p_conferences = models.IntegerField()
    rep_p_papers = models.IntegerField()
    rep_p_books = models.IntegerField()
    rep_p_others = models.IntegerField()
    rep_n_articles_files = models.IntegerField()
    rep_n_processed = models.IntegerField()
    rep_n_duplicate = models.IntegerField()
    rep_n_files = models.IntegerField()
    rep_duration_seg = models.IntegerField()
    rep_size_file = models.IntegerField()
    rep_name_file_merged = models.CharField(max_length=100)
    rep_date = models.DateField(auto_now_add=True)  # Permite agregar la fecha actual al registrar

    def __str__(self):
        return f"Report {self.id} for Project {self.id_project.prj_name}"

    def get_formated_duration(self):
        minu = int(self.rep_duration_seg // 60)
        sec = int(self.rep_duration_seg % 60)

        return f"{minu:02}:{sec:02} seg"  # Tiempo formateado

    def get_file_path(self):
        if self.rep_name_file_merged:
            return f'{settings.MEDIA_URL}/files/bib/{self.rep_name_file_merged}'
        else:
            return None

    def get_size(self):
        if self.rep_size_file:
            size = self.rep_size_file / (1024 * 1024)
            return f'{size:.2f} MB'  # Tamaño de archivo en MB
        else:
            return

    def get_count_types(self):
        data = {}

        if self.rep_p_articles:
            data['article'] = self.rep_p_articles

        if self.rep_p_books:
            data['book'] = self.rep_p_books

        if self.rep_p_conferences:
            data['conference'] = self.rep_p_conferences

        if self.rep_p_others:
            data['others'] = self.rep_p_others

        return data


class ProjectFile:
    def __init__(self):
        self.sheeps_ids = []
        self.white_sheeps_ids = []
        self.black_sheeps_ids = []
        self.num_sheeps = 0
        self.num_white_sheeps = 0
        self.num_black_sheeps = 0
        self.exist_b_sheep = False

        self.type_counts = {
            'article': 0,
            'book': 0,
            'conference': 0,
            'booklet': 0,
            'inbook': 0,
            'incollection': 0,
            'inproceedings': 0,
            'manual': 0,
            'mastersthesis': 0,
            'misc': 0,
            'phdthesis': 0,
            'proceedings': 0,
            'techreport': 0,
            'unpublished': 0,
        }

    @staticmethod
    def decode_file(file):
        fileBytes = file.read()
        # Decodificamos el archivo para pasarle un regex y sacar el número total de entry's
        return fileBytes.decode('utf-8')

    @staticmethod
    def read_bibtext(file_decode):
        bib_database = bparser.loads(file_decode)

        # Generador
        for entry in bib_database.entries:
            yield entry

    def extract_data_file(self, file_decode):
        self.get_sheeps(file_decode)
        self.get_white_sheeps(file_decode)

        self.num_sheeps = len(self.sheeps_ids)
        self.num_white_sheeps = len(self.white_sheeps_ids)
        self.num_black_sheeps = self.num_sheeps - self.num_white_sheeps

        self.exist_b_sheep = True if self.num_black_sheeps > 0 else False

        self.obtain_black_sheeps()

    def get_type_entry(self, entry):
        entry_type = entry.get('ENTRYTYPE', '').lower()

        self.type_counts[entry_type] += 1

        if entry_type == 'article' or entry_type == 'book' or entry_type == 'conference':
            return entry_type
        else:
            return 'others'

    def get_white_sheeps(self, file_decode):
        for entry in self.read_bibtext(file_decode):
            entry_id = entry.get('ID', '')
            self.white_sheeps_ids.append(entry_id)

    def obtain_black_sheeps(self):
        if self.exist_b_sheep:
            set_S = set([sheep.group(1) for sheep in self.sheeps_ids])

            set_WS = set(self.white_sheeps_ids)

            self.black_sheeps_ids = list(set_S.difference(set_WS))

    def get_sheeps(self, decode_file):
        self.sheeps_ids = list(re.finditer(r'@\w+\{\s*(\S.+),', decode_file))

    def unificar_entradas(self, file_decode, Obj_PurgeData):

        for entry in self.read_bibtext(file_decode):
            # Obtengo el tipo de entrada y lo acumulo en el diccionario (conteo de tipos de entrada)
            type_entry = self.get_type_entry(entry)

            if type_entry not in Obj_PurgeData.count_entry_type_all:
                Obj_PurgeData.count_entry_type_all[type_entry] = 1
            else:
                Obj_PurgeData.count_entry_type_all[type_entry] += 1

            # Se controla lo que son el título y autor, se los convierte a minúscula
            # para evitar problemas en la comparación
            title = entry['title'].lower()
            title = self.replace_slash(title)
            author = entry['author'].lower()
            print(unidecode(author))
            author = self.replace_slash(author)

            # Lo guardamos en una tupla para meterlo como clave en el diccionario
            clave = (title, author, entry['year'])

            # Si no está la clave, esta ingresa como única junto con el entry
            if clave not in Obj_PurgeData.entradas_unicas:
                # Obj_PurgeData.entradas_unicas[clave] = entry
                Obj_PurgeData.entradas_unicas[clave] = 1
            else:
                # Si es una clave repetida, se los manda a combinar
                # Obj_PurgeData.entradas_unicas[clave] = self.combinar_entradas(Obj_PurgeData.entradas_unicas[clave], entry)
                Obj_PurgeData.entradas_unicas[clave] += 1

            Obj_PurgeData.contArt += 1

    def combinar_entradas(self, e1, e2):
        # Combina las dos entradas añadiendo los campos faltantes de e1 con los de e2
        for key, value in e2.items():
            if key not in e1 or not e1[key]:
                e1[key] = value
            elif key == 'keywords':
                keywords_e1 = set(e1[key].split(', '))
                keywords_e2 = set(e2[key].split(', '))
                combined_keywords = self.normalizar_keywords(', '.join(keywords_e1.union(keywords_e2)),
                                                             keywords_e1.union(keywords_e2))
                e1[key] = combined_keywords.title()
        return e1

    def normalizar_keywords(self, keywords, expanded_keywords):
        # Convierte las keywords a minúsculas, expande abreviaturas,
        # elimina espacios adicionales y las ordena alfabéticamente
        if isinstance(keywords, str):
            keywords = keywords.split(',')
        keywords_normalizadas = set()
        for kw in keywords:
            kw_normalizada = re.sub(r'\s+', ' ', kw.strip().lower())
            kw_normalizada = re.sub(r'[^\w\s]+$', '', kw_normalizada)
            kw_expandidas = self.expandir_abreviatura(kw_normalizada, expanded_keywords)
            keywords_normalizadas.add(kw_expandidas)
        return ', '.join(sorted(keywords_normalizadas))

    @staticmethod
    def expandir_abreviatura(keyword, expanded_keywords):
        # Expande las abreviaturas en las keywords
        for expanded in expanded_keywords:
            if keyword == ''.join([word[0] for word in expanded.split()]):
                return expanded
        return keyword

    @staticmethod
    def replace_slash(string):
        return string.replace('\n', ' ')

    def clean_black_sheep(self, entries, content):
        # Sacamos una lista completa de todos las entradas con regex
        list_entry_id = re.findall(r'@\w+\{\s*(\S.+),', content)

        # Hacemos una copia de lista extraída
        list_not_ID = list_entry_id.copy()

        for entry in entries:
            entry_id = entry.get('ID', '')

            # Removemos de la copia los valores existentes del entrie y dejamos los que tienen inconsistencias
            if entry_id in list_entry_id:
                list_not_ID.remove(entry_id)

        # Esto es para TESTING (BORRAR)
        name_date = datetime.now().strftime("%Y%m%d%H%M%S")
        from main import settings
        filePath = os.path.join(settings.MEDIA_BIB, f'list_ovejas_negras_{name_date}.txt')

        # Esto es para TESTING (BORRAR)
        print("Cantidad de id's: ", len(list_entry_id))
        print("Contador de objeas negras: ", len(list_not_ID))
        print("Lista de obejas negras: \n", list_not_ID)
        with open(filePath, 'w') as f:
            for id_ in list_not_ID:
                f.write(id_ + "\n")

        return f"""Cantidad de id's: {len(list_entry_id)}\nConteo de los tipos: {len(entries)}\nContador de objeas negras: {len(list_not_ID)}\nLista de obejas negras: {list_not_ID}
        """

    # def get_numbers_standard_types(self, entries):
    #     # Creamos un diccionario con los standar type y un contador en 0
    #     type_counts = {'article': 0,
    #                    'book': 0,
    #                    'conference': 0,
    #                    'others': 0,
    #                    }
    #
    #     # Iteramos los entries del parser
    #     for entry in entries:
    #         entry_type = entry.get('ENTRYTYPE', '').lower()
    #
    #         # Sacamos la cantidad por cada tipo de entry (books, article, conferences, etc)
    #         if entry_type in type_counts:
    #             type_counts[entry_type] += 1
    #         else:
    #             type_counts['others'] += 1
    #
    #     # Esto es para TESTING (BORRAR)
    #     for entry_type, count in type_counts.items():
    #         print(f'{entry_type}: {count}')
    #
    #     return type_counts
    #