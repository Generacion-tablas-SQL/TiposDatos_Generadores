
import random
from random import randint

# Para estos generadores de los diferentes tipos de datos tenemos en cuenta las restricciones de tipo:
# *UNIQUE, PRIMARY KEY, REFERENCES , *NOT NULL, *CHECK Y LENGTH


# Generador de números enteros
# id = INT or INTEGER
# opt1 = null or nullable
# opt2 = unique (no implementado )

def generate_int(id, opt1, opt2):

    if(eval("id.lower() == 'integer' or id.lower() == 'int'")):
        if(not eval("opt1.lower() == 'nullable' or opt1.lower() == 'null'" )):
            n = random.randint(0,500)
            print(n)


#generate_int("INT", "", "")
generate_int("INT", "NULL", "")
#generate_int("INTEGER")
#generate_int("inTeGer")
#generate_int("integer")









