import mo_parsing
from mo_sql_parsing import parse, normal_op
import clasificador as c
import traceback
import sys
# import exceptionsDef


create_table = "CREATE TABLE Persona (" \
               "real NUMBER(4,2) UNIQUE NULL CHECK (NOT REal <= 0 AND REAL < 20 AND real != 10)," \
               "ent INT CHECK (ent > 12 and ent < 50)," \
               "string VARCHAR(15) UNIQUE NOT NULL," \
               "fec1 DATE UNIQUE NOT NULL, " \
               "fec2 TIMESTAMP(2) UNIQUE NOT NULL)"

#CHECK (string LIKE 'C%' and LENGTH(string) > 5 and LENGTH(string) < 10)
select1 = "SELECT ent FROM Persona"
select2 = "SELECT ent, real FROM Persona"
select3 = "SELECT string, string FROM Persona WHERE string = aaaaaa "


def get_columnas(sentencia_parsed):
    nombre_cols = list()
    cols = sentencia_parsed.get("select")
    if not isinstance(cols, list):
        cols = [cols]
    for col in cols:
        nombre_cols.append(col.get("value").lower())

    return nombre_cols


def poblador_tablas(sentencias_create, sentencia_select):
    """Dada una o varias tablas y una o varias sentencias select, ...

    :param sentencias_create: conjunto de sentencias create table
    :param sentencia_select: una sentencia select
    :return:
    """
    # tablas_restricciones = {tabla1: [
    #                    {col1: ["nullable", "unique", {min:0, max:10, eq: None, neq: 5, scale: 0, tipo: int}]},
    #                    {col2: ["primary key", {min: 5, max:10, eq: None, neq: None, like: '___-_%', tipo: varchar}]}
    #                    ]}
    tablas_restricciones = {}
    tablas_datos = {}
    tablas = sentencias_create.split(";")

    try:
        select_parsed = parse(sentencia_select, calls=normal_op)  # Parsea la consulta select
        where_restr = select_parsed.get("where")

        for tabla in tablas:
            tabla_parsed = parse(tabla, calls=normal_op)
            nombre_tabla = tabla_parsed.get("create table").get("name").lower()

            tablas_restricciones.update({nombre_tabla: {}})
            tablas_datos.update({nombre_tabla: {}})

            # datos: diccionario con un array de datos generados aleatoriamente asociado a cada columna
            # restricciones: diccionario con un array de restricciones asociado a cada columna
            datos, restricciones = c.clasificar_tipo(tabla_parsed.get("create table").get("columns"), where_restr)

            tablas_restricciones.get(nombre_tabla).update(restricciones)
            tablas_datos.get(nombre_tabla).update(datos)

        nombre_cols = get_columnas(select_parsed)  # Agrega a una lista todas las columnas de la consulta
        nombre_tabla = select_parsed.get("from").lower()  # Identifica la tabla consultada

        value_list = list()
        pos = 0
        for i in range(0, 10):
            for data in tablas_datos.get(nombre_tabla).values():
                value_list.append(data[pos])
            values = tuple(value_list)
            print("INSERT INTO", nombre_tabla, "VALUES", values)
            value_list.clear()
            pos += 1

        print(tablas_datos)
        print(tablas_restricciones)

    except mo_parsing.exceptions.ParseException as err:
        traceback.print_exc()
        print("Error, excepción al hacer el parse:\n", err)

    except IndentationError as err:
        traceback.print_exc()
        print("Error, excepción debido a indexación incorrecta:\n", err)

    except AttributeError as err:
        traceback.print_exc()
        print("Error, excepción en la referencia al valor del atributo:\n", err)

    except KeyError as err:
        traceback.print_exc()
        print("Error, excepción en el acceso a diccionario, la clave no está definida:\n", err)

    except TypeError as err:
        traceback.print_exc()
        print("Error, dato de tipo inapropiado:\n", err)

    except IndexError as err:
        traceback.print_exc()
        print("Error, el índice no existe:\n", err)

    except NameError as err:
        traceback.print_exc()
        print("Error, el nombre local o global no esta definido:\n", err)

    except ValueError as err:
        traceback.print_exc()
        print("Error, función/operación con valor inapropiado:\n", err)

    finally:
        print("Fin de la ejecución.\n")


poblador_tablas(create_table, select3)
