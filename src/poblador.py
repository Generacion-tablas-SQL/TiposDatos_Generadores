from mo_sql_parsing import parse, normal_op
import clasificador as c

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
    # variable para almacenar en un diccionario las restricciones de cada tabla
    tablas_restricciones = {}
    # variable para almacenar en un diccionario los datos generados en cada columna de cada tabla
    tablas_datos = {}

    # Parsear las sentencias CREATE TABLE
    tablas = sentencias_create.split(";")
    tablas_parsed = [parse(x, calls=normal_op) for x in tablas]

    # Parsear la sentencia SELECT
    select_parsed = parse(sentencia_select, calls=normal_op)  # Parsea la consulta select

    # Seleccionar las tablas que aparecen en la sentencia SELECT para luego iterar sobre ellas
    # Así evitamos analizar las tablas con las que no vamos a trabajar
    tablas_select = list()
    _from = select_parsed.get("from")
    if not isinstance(_from, list):
        _from = [_from]
    if len(_from) > 1:
        tablas_select = [x.get("join").lower() for x in _from[1:]]
    tablas_select.insert(0, _from[0].lower())

    # Analizar los joins
    joins = dict()
    if len(_from) > 1:
        num_elems = 2
        # pos = 0
        for join in _from[1:]:
            key = tuple([tablas_select[x] for x in range(0, num_elems)])
            # tablas_select[pos], tablas_select[pos + 1]
            joins.update({key: [join.get("on").get("op"), join.get("on")
                         .get("args")[0], join.get("on").get("args")[1]]})
            num_elems += 1
            # pos += 1

    for tabla_s in tablas_select:
        tablas_restricciones.update({tabla_s: {}})
        tablas_datos.update({tabla_s: {}})

        # Buscar las tabla en tablas_parsed cuyos nombres coincidan con tabla_s.
        # Así no iteramos sobre tablas no necesarias
        tablas = list()
        for tabla_p in tablas_parsed:
            aux = tabla_p.get("create table")
            if aux.get("name").lower() == tabla_s:
                tablas.append(aux)
                break
        if len(tablas) == 0:
            raise Exception("La tabla no existe")

        # datos: diccionario con un array de datos generados aleatoriamente asociado a cada columna
        # restricciones: diccionario con un array de restricciones asociado a cada columna
        # datos, restricciones = c.clasificar_tipo(tabla.get("columns"), _from, select_parsed.get("where"))
        datos, restricciones = c.clasificar_tipo(tabla_s, tablas, joins, select_parsed.get("where"))

        tablas_restricciones.get(tabla_s).update(restricciones)
        tablas_datos.get(tabla_s).update(datos)

    # nombre_tabla = select_parsed.get("from").lower()  # Identifica la tabla consultada

    insert_list = list()
    value_list = list()

    for tabla_s in tablas_select:
        num_filas = 500
        for data in tablas_datos.get(tabla_s).values():
            num_filas = min(num_filas, len(data))

        for i in range(0, num_filas):
            for data in tablas_datos.get(tabla_s).values():
                if len(data) > i:
                    value_list.append(data[i])
                else:
                    break
            if len(value_list) != 0:
                values = tuple(value_list)
                insert_list.append("INSERT INTO " + tabla_s + " VALUES " + str(values))
                value_list.clear()

    return insert_list
