# Abreviatura de palabras keywords
kw = 'keywords'
kwp = 'keywords-plus'
kwa = 'author_keywords'


class PurgeData:
    entradas_unicas = {}

    sheeps_ids = 0  # contador de los entry por regex
    white_sheeps_ids = 0  # contador de los entry por regex
    black_sheeps_ids = []  # lista de todas las obejas negras
    contArt = 1  # Contador de los entry's
    count_entry_type_all = {}

    def format_bibtext_entry(self, entry, cont):
        tempKeys = {}  # Diccionario de los keywords por cada iteración del entry

        # field, format, wrap or not
        field_order = [(u'author', '{{{0}}},\n', True),
                       (u'title', '{{{0}}},\n', True),
                       (u'journal', '{{{0}}},\n', True),
                       (u'volume', '{{{0}}},\n', True),
                       (u'number', '{{{0}}},\n', True),
                       (u'pages', '{{{0}}},\n', True),
                       (u'year', '{{{0}}},\n', True),
                       (u'doi', '{{{0}}},\n', False)]

        # Creamos un conjunto con todos los key del entry
        keys = set(entry.keys())

        # Se sacan los campos extras entre la diferencia de las keys y los key del field_order
        extra_fields = keys.difference([f[0] for f in field_order])

        # No necesitamos esto en los extras
        extra_fields.remove('ENTRYTYPE')
        extra_fields.remove('ID')

        # Construimos la cadena de entrada y añadimos el código ordenado por año
        # ENTRYTYPE
        s = '@{type}{{{id},\ncode={{{code}}},\n\n'.format(type=entry['ENTRYTYPE'],
                                                          id=entry['ID'], code=cont)

        for field, fmt, wrap in field_order:
            if field in entry:
                # Este código comentado era para añadir un contador al título,
                # como ya lo pusimos en código, comento esto.
                if field == 'title':
                    s += self.union(field, '{0} {1}'.format(cont, entry[field]))
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
            # Manejamos únicamente minúsculas
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

        # Si no existe ningún tipo de keyword, entonces se crean los 3 campos
        if (keyword + keywords_plus + author_keywords) == 0:
            s += self.union(kw, " ")  # Keywords
            s += self.union(kwp, " ")  # keywords-plus
            s += self.union(kwa, " ")  # author_keywords

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
