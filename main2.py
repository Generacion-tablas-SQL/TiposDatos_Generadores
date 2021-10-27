import constantes
import random
# from mo_sql_parsing import format


def number_of_digits(precision):  # precision 3 --> max_num = 999
    max_num = 9
    aux = 9
    if precision == 1:
        return 9
    while precision > 1:
        precision -= 1
        aux *= 10
        max_num = max_num + aux
    return max_num


# sentencia_tablas4 = """CREATE TABLE Persona (
#   Id INTEGER CHECK (Id > 50) ,
#   Nombre VARCHAR(30) ,
#   CONSTRAINT NombreLargo CHECK (LENGTH(Nombre) > 5)
# );"""

# print(parse(sentencia_tablas4))

# salida: {'create table': {'name': 'Persona', 'columns': [
# {'name': 'id', 'type': {'integer': {}}, 'option': {'check': {'gt': ['Id', 50]}}},
# {'name': 'nombre', 'type': {'varchar': 30}}],
# 'constraint': {'name': 'NombreLargo', 'check': {'gt': [{'length': 'Nombre'}, 5]}}}}

# generate_int({'name': 'id', 'type': {'integer': {}}, 'option': {'check': {'gt': ['Id', 50]}}},
# "{'name': 'NombreLargo', 'check': {'gt': [{'length': 'Nombre'}, 5]}}}")
def generate_int2(column, constraint):
    data_type = column.get("type")
    key = list(data_type.keys())
    restriction = list(data_type.values())

    if key[0] not in constantes.ENTEROS:
        return "Este tipo de datos no es un entero"
    else:
        if key[0] != "number" and str(restriction[0]) != "{}":
            return "Este tipo de datos no soporta parámetros"
        if key[0] == "number" and str(restriction[0]) == "{}":
            return "Este tipo de datos es un número real"
        if key[0] == "number" and len(restriction) == 2 and restriction[1] != 0:
            return "Este tipo de datos es un número real"
        if key[0] == "number":
            return random.randint(0, number_of_digits(restriction[0]))
        return random.randint(0, number_of_digits(38))  # int, integer y smallint tienen una precision de 38


print(generate_int2({'name': 'id', 'type': {'integer': {}}, 'option': {'check': {'gt': ['Id', 50]}}},
                    "{'name': 'NombreLargo', 'check': {'gt': [{'length': 'Nombre'}, 5]}}}"))