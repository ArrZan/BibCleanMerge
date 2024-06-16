import os
from datetime import datetime

from django.db import models

from bibtexparser import bibdatabase as bd

import bibtexparser as bparser

import re


# class Project(models.Model):
#     id_project = models.IntegerField(primary_key=True)
#     id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
#     prj_name = models.CharField(max_length=50)
#     prj_description = models.CharField(max_length=255)
#     prj_n_articles = models.IntegerField()
#     prj_date = models.DateField()


class ProjectFiles(models.Model):
    # id_project_files = models.AutoField(primary_key=True)
    # id_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # pf_name_file = models.CharField(max_length=100)
    # pf_p_articles = models.IntegerField()
    # pf_p_conferences = models.IntegerField()
    # pf_p_papers = models.IntegerField()
    # pf_p_books = models.IntegerField()
    # pf_p_others = models.IntegerField()
    # pf_n_entries_file = models.IntegerField()

    # def __str__(self):
    #     return self.pf_name_file

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


