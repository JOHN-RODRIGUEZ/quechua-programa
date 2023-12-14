import re
import sys
from enum import Enum

# Diccionario de palabras reservadas
PALABRAS_RESERVADAS = {
    "mainq": "PALABRA RESERVADA",
    "sichus": "PALABRA RESERVADA",
    "then": "PALABRA RESERVADA",
    "manachayqa": "PALABRA RESERVADA",
    "end": "PALABRA RESERVADA",
    "do": "PALABRA RESERVADA",
    "chaykama": "PALABRA RESERVADA",
    "repeat": "PALABRA RESERVADA",
    "until": "PALABRA RESERVADA",
    "cin": "PALABRA RESERVADA",
    "qawawchy": "PALABRA RESERVADA",
    "floatq": "PALABRA RESERVADA",
    "intq": "PALABRA RESERVADA",
    "boolq": "PALABRA RESERVADA"
}

# Definir patrones para los tokens
PATRONES_TOKEN = {
    'operador': r"\-\*|/\*|\*/|\*|/",
    'parentesis': r"[()]",
    'coma': r",",
    'punto_y_coma': r";",
    'comentario_de_linea': r"//.*",
    'comentario_de_bloque': r"/\*.*?\*/",
    'entero': r"\b\d+\b(?!\.)",
    'real': r"\b\d+\.\d+\b|\b\d+\.\b|\b\.\d+\b",
    'identificador': r"\b[a-zA-Z_0-9][a-zA-Z0-9_]*\b",
    'llave_abierta': r"\{",
    'llave_cerrada': r"\}",
    'porcentaje': r"\%",
    'simbolos': r'>=|>|<=|<|==|!=|:=|=|--|-|\+\+|\+',
    'incremento': r"\+\+",
    'decremento': r"\-\-",
    'mayor_que': r">",
    'mayor_igual': r">=",
    'igual': r"=",
    'igual_igual': r"==",
    'menor': r"<",
    'menor_igual': r"<=",
    'diferente_de': r"!=",
    'asignacion': r":=",
}

# Enumeración para los tipos de token
class TipoToken(Enum):
    PALABRA_RESERVADA = 1
    OPERADOR = 2
    PARENTESIS = 3
    COMA = 4
    PUNTO_Y_COMA = 5
    COMENTARIO_DE_LINEA = 6
    COMENTARIO_DE_BLOQUE = 7
    ENTERO = 8
    REAL = 9
    IDENTIFICADOR = 10
    INCREMENTO = 11
    DECREMENTO = 12
    LLAVE_ABIERTA = 13
    LLAVE_CERRADA = 14
    MAYOR_QUE = 15
    MAYOR_IGUAL = 16
    IGUAL = 17
    IGUAL_IGUAL = 18
    MENOR = 19
    MENOR_IGUAL = 20
    DIFERENTE_DE = 21
    ASIGNACION = 22

def eliminar_comentarios(contenido_archivo):
    # Eliminar comentarios de línea
    contenido_archivo = re.sub(r"//.*", "", contenido_archivo)
    # Eliminar comentarios de bloque
    contenido_archivo = re.sub(r"/\*.*?\*/", "", contenido_archivo, flags=re.DOTALL)

    return contenido_archivo

def obtener_tokens(nombre_archivo):
    try:
        with open(nombre_archivo) as archivo:
            contenido_archivo = archivo.read()

        contenido_archivo #= eliminar_comentarios(contenido_archivo)

        tokens = []
        errores = []

        for numero_linea, linea in enumerate(contenido_archivo.split('\n'), start=1):
            numero_columna = 1

            while linea:
                match = None

                for token_nombre, patron in PATRONES_TOKEN.items():
                    regex = re.compile(patron)
                    match = regex.match(linea)

                    if match:
                        valor = match.group(0)
                        linea = linea[len(valor):]
                        if token_nombre == 'identificador':
                            if valor in PALABRAS_RESERVADAS:
                                tokens.append((valor.lower(), TipoToken.PALABRA_RESERVADA, numero_linea, numero_columna))
                            else:
                                if re.match(r"^\d", valor): # Verificar si el identificador comienza con un número
                                    for i, c in enumerate(valor):
                                        if not c.isdigit():
                                            break
                                    tokens.append((valor[:i], TipoToken.ENTERO, numero_linea, numero_columna))
                                    tokens.append((valor[i:], TipoToken.IDENTIFICADOR, numero_linea, numero_columna + i))
                                else:
                                    tokens.append((valor, TipoToken.IDENTIFICADOR, numero_linea, numero_columna))

                        elif token_nombre in ['real', 'entero']:
                            patron_entero = r"\b\d+\b(?!\.)"
                            patron_real = r"\b\d+\.\d*\b|\b\d*\.\d+\b"
                            if re.match(patron_entero, valor):
                                tokens.append((valor, TipoToken.ENTERO, numero_linea, numero_columna))
                            elif re.match(patron_real, valor):
                                if "." in valor:
                                    partes = valor.split(".")
                                    if len(partes) == 2 and partes[1].isdigit():
                                        tokens.append((valor, TipoToken.REAL, numero_linea, numero_columna))
                                    else:
                                        errores.append((valor, numero_linea, numero_columna))
                                else:
                                    tokens.append((valor, TipoToken.ENTERO, numero_linea, numero_columna))
                            else:
                                errores.append((valor, numero_linea, numero_columna))
                            numero_columna += len(valor)
                            break
                        else:
                            if token_nombre == 'simbolos':
                                if valor == '>=':
                                    tokens.append((valor, TipoToken.MAYOR_IGUAL, numero_linea, numero_columna))
                                elif valor == '>':
                                    tokens.append((valor, TipoToken.MAYOR_QUE, numero_linea, numero_columna))
                                elif valor == '=':
                                    tokens.append((valor, TipoToken.IGUAL, numero_linea, numero_columna))
                                elif valor == '==':
                                    tokens.append((valor, TipoToken.IGUAL_IGUAL, numero_linea, numero_columna))
                                elif valor == '<':
                                    tokens.append((valor, TipoToken.MENOR, numero_linea, numero_columna))
                                elif valor == '<=':
                                    tokens.append((valor, TipoToken.MENOR_IGUAL, numero_linea, numero_columna))
                                elif valor == '!=':
                                    tokens.append((valor, TipoToken.DIFERENTE_DE, numero_linea, numero_columna))
                                elif valor == ':=':
                                    tokens.append((valor, TipoToken.ASIGNACION, numero_linea, numero_columna))
                                elif valor == '--':
                                    tokens.append((valor, TipoToken.DECREMENTO, numero_linea, numero_columna))
                                elif valor == '-':
                                    tokens.append((valor, TipoToken.OPERADOR, numero_linea, numero_columna))
                                elif valor == '++':
                                    tokens.append((valor, TipoToken.INCREMENTO, numero_linea, numero_columna))
                                elif valor == '+':
                                    tokens.append((valor, TipoToken.OPERADOR, numero_linea, numero_columna))
                                else:
                                    tokens.append((valor, TipoToken.SIMBOLOS, numero_linea, numero_columna))
                            else:
                                tokens.append((valor, TipoToken[token_nombre.upper()], numero_linea, numero_columna))
                        numero_columna += len(valor)
                        break

                if not match:
                    if linea[0] != '\n':
                        errores.append((linea[0], numero_linea, numero_columna))
                    linea = linea[1:]
                    numero_columna += 1

        # Escribir errores en archivo
        with open(f"errores.txt", "w") as archivo_errores:
            print("\n\n\n -------------- ERRORES ---------------- \n\n\n")
            for error in errores:
                if error[0].strip():
                    archivo_errores.write(f"Error lexico en la linea {error[1]}, columna {error[2]}: {error[0]} \n")
                    print(f"Error lexico en la linea {error[1]}, columna {error[2]}: {error[0]} \n")
        return tokens
    
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no existe")
        
def obtener_tokens_comentarios(nombre_archivo):
    try:
        with open(nombre_archivo) as archivo:
            contenido_archivo = archivo.read()

        contenido_archivo = eliminar_comentarios(contenido_archivo)

        tokens = []
        errores = []

        for numero_linea, linea in enumerate(contenido_archivo.split('\n'), start=1):
            numero_columna = 1

            while linea:
                match = None

                for token_nombre, patron in PATRONES_TOKEN.items():
                    regex = re.compile(patron)
                    match = regex.match(linea)

                    if match:
                        valor = match.group(0)
                        linea = linea[len(valor):]
                        if token_nombre == 'identificador':
                            if valor in PALABRAS_RESERVADAS:
                                tokens.append((valor.lower(), TipoToken.PALABRA_RESERVADA, numero_linea, numero_columna))
                            else:
                                if re.match(r"^\d", valor): # Verificar si el identificador comienza con un número
                                    for i, c in enumerate(valor):
                                        if not c.isdigit():
                                            break
                                    tokens.append((valor[:i], TipoToken.ENTERO, numero_linea, numero_columna))
                                    tokens.append((valor[i:], TipoToken.IDENTIFICADOR, numero_linea, numero_columna + i))
                                else:
                                    tokens.append((valor, TipoToken.IDENTIFICADOR, numero_linea, numero_columna))

                        elif token_nombre in ['real', 'entero']:
                            patron_entero = r"\b\d+\b(?!\.)"
                            patron_real = r"\b\d+\.\d*\b|\b\d*\.\d+\b"
                            if re.match(patron_entero, valor):
                                tokens.append((valor, TipoToken.ENTERO, numero_linea, numero_columna))
                            elif re.match(patron_real, valor):
                                if "." in valor:
                                    partes = valor.split(".")
                                    if len(partes) == 2 and partes[1].isdigit():
                                        tokens.append((valor, TipoToken.REAL, numero_linea, numero_columna))
                                    else:
                                        errores.append((valor, numero_linea, numero_columna))
                                else:
                                    tokens.append((valor, TipoToken.ENTERO, numero_linea, numero_columna))
                            else:
                                errores.append((valor, numero_linea, numero_columna))
                            numero_columna += len(valor)
                            break
                        else:
                            if token_nombre == 'simbolos':
                                if valor == '>=':
                                    tokens.append((valor, TipoToken.MAYOR_IGUAL, numero_linea, numero_columna))
                                elif valor == '>':
                                    tokens.append((valor, TipoToken.MAYOR_QUE, numero_linea, numero_columna))
                                elif valor == '=':
                                    tokens.append((valor, TipoToken.IGUAL, numero_linea, numero_columna))
                                elif valor == '==':
                                    tokens.append((valor, TipoToken.IGUAL_IGUAL, numero_linea, numero_columna))
                                elif valor == '<':
                                    tokens.append((valor, TipoToken.MENOR, numero_linea, numero_columna))
                                elif valor == '<=':
                                    tokens.append((valor, TipoToken.MENOR_IGUAL, numero_linea, numero_columna))
                                elif valor == '!=':
                                    tokens.append((valor, TipoToken.DIFERENTE_DE, numero_linea, numero_columna))
                                elif valor == ':=':
                                    tokens.append((valor, TipoToken.ASIGNACION, numero_linea, numero_columna))
                                elif valor == '--':
                                    tokens.append((valor, TipoToken.DECREMENTO, numero_linea, numero_columna))
                                elif valor == '-':
                                    tokens.append((valor, TipoToken.OPERADOR, numero_linea, numero_columna))
                                elif valor == '++':
                                    tokens.append((valor, TipoToken.INCREMENTO, numero_linea, numero_columna))
                                elif valor == '+':
                                    tokens.append((valor, TipoToken.OPERADOR, numero_linea, numero_columna))
                                else:
                                    tokens.append((valor, TipoToken.SIMBOLOS, numero_linea, numero_columna))
                            else:
                                tokens.append((valor, TipoToken[token_nombre.upper()], numero_linea, numero_columna))
                        numero_columna += len(valor)
                        break

                if not match:
                    if linea[0] != '\n':
                        errores.append((linea[0], numero_linea, numero_columna))
                    linea = linea[1:]
                    numero_columna += 1


        # Escribir resultados en archivo
        with open("resultados.txt", "w") as archivo_resultados:
            archivo_resultados.write("{:<20} | {:<20} | {:<20} | {:<20}\n".format("Token", "Tipo", "Linea", "Columna"))
            archivo_resultados.write("-" * 21 + "|" + "-" * 22 + "|" +  "-" * 22 + "|" + "-" * 12 + "\n")
            for token in tokens:
                valor, tipo, numero_linea, numero_columna = token
                archivo_resultados.write("{:<20} | {:<20} | {:<20} | {:<20}\n".format(valor, tipo.name.replace('TipoToken.', ''), numero_linea, numero_columna))

        return tokens
    
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no existe")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        nombre_archivo = sys.argv[1]
        
        tokens = obtener_tokens_comentarios(nombre_archivo)
        obtener_tokens(nombre_archivo)
        
        print("\n\n ------------------ ANALISIS LEXICO -------------------------- \n\n\n")
        for token in tokens:
            valor, tipo, numero_linea, numero_columna = token
            print("{:<20} | {:<20} | {:<20} | {:<20}\n".format(valor, tipo.name.replace('TipoToken.', ''), numero_linea, numero_columna))

    else:
        print("Debe proporcionar el nombre de un archivo como argumento.")