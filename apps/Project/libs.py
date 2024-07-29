
class PurgeData:
    def __init__(self):
        self.entradas_unicas = {}

        self.sheeps_ids = 0  # contador de los entry por regex
        self.duplicate_sheeps = 0
        self.white_sheeps_ids = 0  # contador de los entry por regex
        self.black_sheeps_ids = []  # lista de todas las obejas negras
        self.contArt = 1  # Contador de los entry's
        self.count_entry_type_all = {}

    def format_bibtext_entry(self, entry):
        tempKeys = {}  # Diccionario de los keywords por cada iteración del entry

        # Definir los tipos de keywords si no están definidos
        kw = 'keywords'
        kwp = 'keywords-plus'
        kwa = 'author_keywords'

        # Definir el orden de los campos y el formato
        field_order = [
            ('author', '{{{0}}},\n', True),
            ('title', '{{{0}}},\n', True),
            ('journal', '{{{0}}},\n', True),
            ('volume', '{{{0}}},\n', True),
            ('number', '{{{0}}},\n', True),
            ('pages', '{{{0}}},\n', True),
            ('year', '{{{0}}},\n', True),
            ('doi', '{{{0}}},\n', False)
        ]

        # Crear un conjunto con todos los keys del entry
        keys = set(entry.keys())

        # Sacar los campos extras entre la diferencia de las keys y los key del field_order
        extra_fields = keys.difference([f[0] for f in field_order])

        # Remover 'ENTRYTYPE' y 'ID' de los extras si están presentes
        if 'ENTRYTYPE' in extra_fields:
            extra_fields.remove('ENTRYTYPE')
        if 'ID' in extra_fields:
            extra_fields.remove('ID')

        # Construir la cadena de entrada
        s = '@{type}{{{id},\ncode={{{code}}},\n\n'.format(type=entry['ENTRYTYPE'],
                                                          id=entry['ID'], code=self.contArt)

        for field, fmt, wrap in field_order:
            if field in entry:
                # Este código comentado era para añadir un contador al título,
                # como ya lo pusimos en código, comento esto.
                if field == 'title':
                    s += self.union(field, '{0} {1}'.format(self.contArt, entry[field]))
                else:
                    s += '{0}={1}\n'.format(field, fmt.format(entry[field]))

        # Manejar tipos de keywords
        keyword = 0
        keywords_plus = 0
        author_keywords = 0

        # Aquí almacenamos todos los valores de los campos de un entry
        for field in extra_fields:
            # Convertir field a minúsculas
            field = field.lower()

            # Si el campo está en el entry
            if field in entry:

                # Si no es un keyword, se añade el campo con su valor
                if field != kw and field != kwp and field != kwa:
                    s += self.union(field, entry[field])
                else:

                    if field == kw:
                        keyword = 1
                    elif field == kwp:
                        keywords_plus = 1
                    elif field == kwa:
                        author_keywords = 1

                    tempKeys[field] = entry[field]

        # Agregar campos de keywords si no existen
        if (keyword + keywords_plus + author_keywords) == 0:
            s += self.union(kw, " ")
            s += self.union(kwp, " ")
            s += self.union(kwa, " ")
        elif keyword == 0 and keywords_plus == 0 and author_keywords == 1:
            s += self.union(kw, " ")
            s += self.union(kwp, tempKeys[kwa])
            s += self.union(kwa, " ")

        elif keyword == 0 and keywords_plus == 1 and author_keywords == 0:
            s += self.union(kw, " ")
            s += self.union(kwp, entry[kwp])
            s += self.union(kwa, " ")

        elif keyword == 0 and keywords_plus == 1 and author_keywords == 1:
            s += self.union(kw, " ")
            s += self.union(kwp, tempKeys[kwp] + " ; " + tempKeys[kwa])
            s += self.union(kwa, entry[kwa])

        elif keyword == 1 and keywords_plus == 0 and author_keywords == 0:
            s += self.union(kw, " ")
            s += self.union(kwp, tempKeys[kw])
            s += self.union(kwa, " ")

        elif keyword == 1 and keywords_plus == 0 and author_keywords == 1:
            s += self.union(kw, entry[kw])
            s += self.union(kwp, tempKeys[kw] + " ; " + tempKeys[kwa])
            s += self.union(kwa, entry[kwa])

        elif keyword == 1 and keywords_plus == 1 and author_keywords == 0:
            s += self.union(kw, entry[kw])
            s += self.union(kwp, tempKeys[kwp] + " ; " + tempKeys[kw])
            s += self.union(kwa, " ")

        elif keyword == 1 and keywords_plus == 1 and author_keywords == 1:
            s += self.union(kw, entry[kw])
            s += self.union(kwp, tempKeys[kw] + " ; " + tempKeys[kwp] + " ; " + tempKeys[kwa])
            s += self.union(kwa, entry[kwa])

        s += '\n}\n\n'

        self.contArt += 1

        return s

    @staticmethod
    def separatedKeywords(lista):
        # Separamos los keywords
        if "," in lista:
            lista = lista.replace(",", ";")
        if "\n" in lista:
            lista = lista.replace("\n", "")

        lista = lista.split(";")

        cont = 0
        for word in lista:
            ban = False
            try:

                if len(word) > 1:
                    while not ban:
                        if " " == word[0]:
                            lista[cont] = word[1:]
                            word = word[1:]

                        elif " " == word[-1]:
                            lista[cont] = word[0:-2]
                            word = word[0:-2]
                        else:
                            ban = True
                    cont += 1
            except:
                print(lista)

        return lista

    def keyDel(self, list1, list2):
        # Con esto generamos una lista sin duplicados
        if list1:
            listTemp = self.separatedKeywords(list1)
            for sentence in listTemp:
                if sentence.upper() not in list2:
                    list2[sentence.upper()] = 1
                else:
                    list2[sentence.upper()] = list2[sentence.upper()] + 1
            return list2

    @staticmethod
    def union(key, entrykey):
        # Unimos un campo (author, year, title) con su contenido
        s1 = '{0}='.format(key)
        s3 = '{0}{{{1}}},'.format(s1, entrykey)
        return s3 + '\n'
