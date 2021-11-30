import constantes
import generador_datos as gd

# <----GENERAL---->
def restricciones_sql(parameters, column):
    """Comprueba las restricciones SQL.

    :param parameters: parámetros del tipo de dato.
    :param column: restricciones de la columna.
    :return: lista con las restricciones. El último elemento de la lista es un diccionario con las restricciones check.
    """

    restricciones_list = []
    check = column.get("check") if "check" in column else {}
    if ("nullable" in column and column.get("nullable")) or "nullable" not in column:
        restricciones_list.append("nullable")
    if "unique" in column:  # De momento no afecta
        restricciones_list.append("unique")
    if "primary key" in column:  # De momento no afecta
        restricciones_list.append("primary key")
    if "foreign key" in column:  # De momento no afecta
        restricciones_list.append("foreign key")
    if "default" in column:  # De momento no afecta
        restricciones_list.append({"default", column.get("default").get("literal")})

    restricciones_list.append({})
    if parameters[0] == "Number" or parameters[0] == "String":
        restricciones_list[-1].update(comprobar_restricciones_check(parameters, check))
    else:  # parameters[0] == "Fecha"
        # POR EL MOMENTO LAS FECHAS NO POSEEN RESTRICCIONES CHECK
        restricciones_list[-1].update({"sec_precision": parameters[1], "es_date": parameters[2]})

    return restricciones_list


def get_index(comparison, comparison_key, _not):
    """
    :param comparison: diccionario con la comparación
    :param comparison_key: palabra clave de la comparación
    :param _not: palabra clave de la comparación asociada al not
    :return: indice que indica en que posición se sitúa el número a comparar
    """
    return 1 if _not is None and isinstance(comparison.get(comparison_key)[1], int) else (
        1 if _not is not None and isinstance(comparison.get(comparison_key).get(_not)[1], int) else 0)


# <----RESTRICCIONES CHECK---->
def comprobar_restricciones_check(parameters, check):
    """Comprueba las restricciones CHECK

        :param parameters: tipo de dato Number: ["Number", precision, escala]
                           tipo de dato String: ["String", varying, max_size]
        :param check: campo check de la sentencia parseada
        :return: diccionario con el número máximo, mínimo equal y not equal si se específica
        """

    _max = gd.max_number(parameters[1], parameters[2]) if parameters[0] == "Number" else parameters[2]
    _min = -_max if parameters[0] == "Number" else (1 if parameters[1] is True else parameters[2])
    _eq = None
    _neq = None
    _not = None
    _like = None
    _scale = None if parameters[0] == "String" else parameters[2]

    if check == {}:
        return {"min": _min, "max": _max, "eq": _eq, "neq": _neq, "like": _like, "scale": _scale}

    operator = list(check.keys())[0].lower()  # primer operador que aparece en el check

    # Crea una lista con la/las comparación/comparaciones
    if operator == "and" or operator == "or":
        comparisons = check.get(operator)
    else:
        comparisons = [check]

    for comparison in comparisons:

        comparison_key = list(comparison.keys())[0]
        if comparison_key == "not":
            _not = list(comparison.get("not").keys())[0]  # _not contiene: "lte", "gt"...

        if comparison_key == "eq":
            _eq = comparison.get("eq")[get_index(comparison, comparison_key, None)]
        elif comparison_key == "neq":
            _neq = comparison.get("neq")[get_index(comparison, comparison_key, None)]
        elif comparison_key == "gt" or _not == "gt":
            if _not == "gt":
                # mínimo entre _max y el contenido del comparador
                _max = min(_max, comparison.get("gt")[get_index(comparison, comparison_key, _not)] - 1)
            else:
                # máximo entre _min y el contenido del comparador
                _min = max(_min, comparison.get("gt")[get_index(comparison, comparison_key, None)] + 1)
        elif comparison_key == "gte" or _not == "gte":
            if _not == "gte":
                _max = min(_max, comparison.get("gte")[get_index(comparison, comparison_key, _not)])
            else:
                _min = max(_min, comparison.get("gte")[get_index(comparison, comparison_key, None)])
        elif comparison_key == "lt" or _not == "lt":
            if _not == "lt":
                _min = max(_min, comparison.get("not").get("lt")[get_index(comparison, comparison_key, _not)] + 1)
            else:
                _max = min(_max, comparison.get("lt")[get_index(comparison, comparison_key, None)] - 1)
        elif comparison_key == "lte" or _not == "lte":
            if _not == "lte":
                _min = max(_min, comparison.get("not").get("lte")[get_index(comparison, comparison_key, _not)] + 1)
            else:
                _max = min(_max, comparison.get("lte")[get_index(comparison, comparison_key, None)] - 1)
        elif comparison_key == "like":
            _like = comparison.get("like")[1].get("literal")
        _not = None

    return {"min": _min, "max": _max, "eq": _eq, "neq": _neq, "like": _like, "scale": _scale}


# <----INICIO---->
def clasificar_tipo(columnas):
    """Detecta los tipo de datos de las columnas y delega la generación del tipo de dato detectado.

    :param columnas: columnas de una tabla
    :return: col_data: diccionario con los datos generados de cada columna
             col_restrictions: diccionario con las restricciones de cada columna.
    """

    col_data = {}
    col_restrictions = {}

    for column in columnas:
        col_name = column.get("name").lower()
        data_type = list(column.get("type").keys())[0].lower()  # number
        parameters = list(column.get("type").values())  # [[5, 0]]

        if data_type in constantes.ENTEROS or data_type in constantes.REALES:
            data_type_param = []
            if data_type in constantes.ENTEROS:
                data_type_param.append(38) if parameters[0] == {} else data_type_param.append(parameters[0])
                data_type_param.append(0)
            else:
                data_type_param = [10, 4] if data_type == "float" or data_type == "real" else (
                    [38, 127] if parameters[0] == {} else (
                        [parameters[0], 0] if isinstance(parameters[0], int) else (
                            [parameters[0][0], parameters[0][1]]
                        )
                    )
                )
            data_type_param.insert(0, "Number")
            restricciones = restricciones_sql(data_type_param, column)
            restricciones[-1].update({"tipo": data_type})
            col_restrictions.update({col_name: restricciones})

            numbers = []
            for i in range(10):
                numbers.append(gd.generate_number(restricciones[-1]))
            col_data.update({col_name: numbers})

        elif data_type in constantes.STRINGS:
            # char y nchar tienen un tamaño por defecto de 1
            max_size = 1 if parameters[0] == {} else parameters[0]
            varying = False if data_type == "char" or data_type == "nchar" else True

            data_type_param = ["String", varying, max_size]
            restricciones = restricciones_sql(data_type_param, column)
            restricciones[-1].update({"tipo": data_type})
            col_restrictions.update({col_name: restricciones})

            data = []
            for i in range(10):
                data.append(gd.generate_string(restricciones[-1]))
            col_data.update({col_name: data})

        elif data_type in constantes.FECHA:

            es_date = 1 if data_type == "date" else 0
            sec_precision = 0 if parameters[0] == {} else parameters[0]

            data_type_param = ["Fecha", sec_precision, es_date]

            # restricciones = ['unique', {'sec_precision': 2, 'es_date': 0}]
            restricciones = restricciones_sql(data_type_param, column)

            # 'fec2': ['unique', {'sec_precision': 2, 'es_date': 0, 'tipo': 'timestamp'}]
            restricciones[-1].update({"tipo": data_type})
            col_restrictions.update({col_name: restricciones})

            fechas = []
            for i in range(10):
                # restricciones[0] = sec_precision, restricciones[1]= es_date, restricciones[2] = data_type
                fechas.append(gd.gen_fecha(restricciones))
            col_data.update({col_name: fechas})
        else:
            raise ValueError
            # print("Ha habido un error en la clasificación de tipo de datos.")
    return col_data, col_restrictions
