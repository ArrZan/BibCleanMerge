# Separamos los keywords
def separatedKeywords(lista):
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


# Con esto generamos una lista sin duplicados
def keyDel(list1, list2):
    if list1:
        listTemp = separatedKeywords(list1)
        for sentence in listTemp:
            if sentence.upper() not in list2:
                list2[sentence.upper()] = 1
            else:
                list2[sentence.upper()] = list2[sentence.upper()] + 1
        return list2


# Unimos un campo (author, year, title) con su contenido
def union(key, entrykey):
    s1 = '{0}='.format(key)
    s3 = '{0}{{{1}}},'.format(s1, entrykey)
    return s3 + '\n'
