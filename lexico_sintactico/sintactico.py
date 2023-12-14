from anytree import Node, RenderTree

# Clase Token para representar los tokens generados por el analizador léxico
class Token:
    def __init__(self, tipo_token, valor, numero_linea, numero_columna):
        self.tipo_token = tipo_token
        self.valor = valor
        self.numero_linea = numero_linea
        self.numero_columna = numero_columna

# Función para leer los tokens desde el archivo
def leer_tokens(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        # Ignorar las dos primeras líneas
        archivo.readline()
        archivo.readline()
        # Leer los tokens desde el archivo
        tokens = []
        for linea in archivo:
            valor, tipo_token, numero_linea, numero_columna = linea.strip().split('|')
            tokens.append(Token(tipo_token.strip(), valor.strip(), int(numero_linea.strip()), int(numero_columna.strip())))
        return tokens

# Clase para representar el árbol sintáctico
class NodoSintaxis:
    def __init__(self, valor, hijos=None):
        self.valor = valor
        self.hijos = hijos if hijos else []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

# Clase para el analizador sintáctico
class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.indice_token_actual = 0
        self.errores = []

    def analizar(self):
            # Comprobar si el programa comienza con 'main'
            if self.token_actual().valor == 'main':
                self.consumir_token()
                if self.token_actual().valor == '{':
                    self.consumir_token()
                    nodo_programa = self.programa()
                    if self.token_actual().tipo_token != 'EOF':
                        self.error("Token inesperado al final del programa.")
                    return nodo_programa
                else:
                    self.error(f"Se esperaba 'Llave que abre' en la linea {self.token_actual().numero_linea}")
                    nodo_programa = self.programa()
                    if self.token_actual().tipo_token != 'EOF':
                        self.error("Token inesperado al final del programa.")
                    return nodo_programa
            else:
                self.error(f"Se esperaba 'main' en la linea {self.token_actual().numero_linea}")
                if self.token_actual().valor == '{':
                    nodo_programa = self.programa()
                    if self.token_actual().tipo_token != 'EOF':
                        self.error("Token inesperado al final del programa.")
                    return nodo_programa
                else:
                    self.error(f"Se esperaba 'Llave que abre' en la linea {self.token_actual().numero_linea}")
                    nodo_programa = self.programa()
                    if self.token_actual().tipo_token != 'EOF':
                        self.error("Token inesperado al final del programa.")
                    return nodo_programa

    def token_actual(self):
        if self.indice_token_actual < len(self.tokens):
            return self.tokens[self.indice_token_actual]
        else:
            return Token('EOF', '', len(self.tokens) + 3, 1)  # Agregar columna 1 para EOF

    def consumir_token(self):
        self.indice_token_actual += 1

    def error(self, mensaje):
        token_actual = self.token_actual()
        mensaje_error = f"Error de sintaxis en la línea {token_actual.numero_linea}, columna {token_actual.numero_columna}: {mensaje}"
        self.errores.append(mensaje_error)

    def programa(self):
        nodo_lista_declaracion = self.lista_declaracion()
        return NodoSintaxis('<programa>', [nodo_lista_declaracion])

    def lista_declaracion(self):
        nodo_lista_declaracion = NodoSintaxis('<lista_declaracion>')
        while self.token_actual().tipo_token != 'EOF':
            if self.token_actual().valor in ['intq', 'realq', 'voidq', 'floatq']:
                nodo_declaracion = NodoSintaxis('<declaracion>')
                nodo_decl = self.declaracion()
                nodo_lista_declaracion.agregar_hijo(nodo_decl)
            elif self.token_actual().valor in ['sichus', 'chaykama', 'do', 'qawachy', 'cinq', 'until']:
                nodo_declaracion = NodoSintaxis('<declaracion>')
                nodo_lista_declaracion.agregar_hijo(nodo_declaracion)
                nodo_do = self.lista_sentencias()
                nodo_declaracion.agregar_hijo(nodo_do)
            elif self.token_actual().tipo_token == 'IDENTIFICADOR':
                nodo_declaracion = NodoSintaxis('<declaracion>')
                nodo_lista_declaracion.agregar_hijo(nodo_declaracion)
                nodo_do = self.lista_sentencias()
                nodo_declaracion.agregar_hijo(nodo_do)
            self.consumir_token()
        return nodo_lista_declaracion
    
    def declaracion(self):
        nodo_declaracion = NodoSintaxis('<declaracion>')
        if self.token_actual().valor in ['intq', 'floatq', 'voidq', 'realq']:
            tipo_variable = self.token_actual().valor  # Obtener el tipo de variable
            self.consumir_token()
            if self.token_actual().tipo_token == 'IDENTIFICADOR':
                nodo_tipo = NodoSintaxis('<tipo>', [NodoSintaxis(tipo_variable)])  # Agregar el nodo <tipo>
                nodo_declaracion_variable = NodoSintaxis('<declaracion_variable>', [nodo_tipo])  # Agregar nodo <tipo> antes de <identificador>
                while self.token_actual().tipo_token == 'IDENTIFICADOR':
                    nodo_identificador = NodoSintaxis('<identificador>', [NodoSintaxis(self.token_actual().valor)])
                    nodo_declaracion_variable.agregar_hijo(nodo_identificador)
                    self.consumir_token()
                    if self.token_actual().valor == ',':
                        self.consumir_token()
                nodo_declaracion.agregar_hijo(nodo_declaracion_variable)
                if self.token_actual().valor == ';':
                    self.consumir_token()
                    nodo_declaracion_variable.agregar_hijo(NodoSintaxis(';'))
                    if self.token_actual().valor in ['intq','floatq','voidq']:
                        self.indice_token_actual = self.indice_token_actual -1
                    else:
                        self.indice_token_actual = self.indice_token_actual -1
                else:
                    self.error(f"Se esperaba ';' en la línea {self.token_actual().numero_linea}.")
            else:
                self.error(f"Se esperaba un identificador en la línea {self.token_actual().numero_linea}.")
        else:
            self.error(f"Declaración inválida en la línea {self.token_actual().numero_linea}.")
        return nodo_declaracion

    def lista_sentencias(self):
        nodo_lista_sentencias = NodoSintaxis('<lista_sentencias>')
        while self.token_actual().tipo_token != 'EOF' and self.token_actual().valor != 'end':
            if self.token_actual().valor in ['sichus', 'chaykama', 'do', 'cinq', 'qawachy', 'IDENTIFICADOR']:
                nodo_sent = NodoSintaxis('<sentencia>')
                nodo_lista_sentencias.agregar_hijo(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
            elif  self.token_actual().valor in ['intq','floatq']:
                nodo_sent = NodoSintaxis('<lista_declaracion>')
                nodo_lista_sentencias.agregar_hijo(nodo_sent)                
                nodo_sentencia = self.declaracion()
                nodo_sent.agregar_hijo(nodo_sentencia)  
            elif  self.token_actual().tipo_token in ['IDENTIFICADOR']:
                nodo_sent = NodoSintaxis('<sentencia>')
                nodo_lista_sentencias.agregar_hijo(nodo_sent)                
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)                
            else:
                self.error(f"Sentencia inválida en la línea {self.token_actual().numero_linea}.")
                self.consumir_token()
        return nodo_lista_sentencias

    def sentencia(self):
        if self.token_actual().valor == 'sichus':
            return self.seleccion()
        elif self.token_actual().valor == 'chaykama':
            return self.iteracion()
        elif self.token_actual().valor == 'do':
            return self.repeticion()
        elif self.token_actual().valor == 'cinq':
            return self.sent_in()
        elif self.token_actual().valor == 'qawachy':
            return self.sent_out()
        elif self.token_actual().tipo_token == 'IDENTIFICADOR':
            return self.asignacion()
        else:
            self.error(f"Sentencia inválida en la línea {self.token_actual().numero_linea}.")
            self.consumir_token()

    def asignacion(self):
        nodo_asignacion = NodoSintaxis('<asignacion>')
        nodo_identificador = NodoSintaxis('<identificador>', [NodoSintaxis(self.token_actual().valor)])
        nodo_asignacion.agregar_hijo(nodo_identificador)
        self.consumir_token()
        if self.token_actual().valor in ['=', '+=', '-=', '*=', '/=', '%=']:
            nodo_asignacion_op = NodoSintaxis('<asignacion_op>', [NodoSintaxis(self.token_actual().valor)])
            nodo_asignacion.agregar_hijo(nodo_asignacion_op)
            self.consumir_token()
            nodo_sent_expresion = self.sent_expresion()
            nodo_asignacion.agregar_hijo(nodo_sent_expresion)
        else:
            self.error(f"Operador de asignación inválido en la línea {self.token_actual().numero_linea}.")
        return nodo_asignacion

    def sent_expresion(self):
        nodo_sent_expresion = NodoSintaxis('<sent_expresion>')
        if self.token_actual().valor != ';':
            nodo_expresion = self.expresion()
            nodo_sent_expresion.agregar_hijo(nodo_expresion)
        if self.token_actual().valor == ';':
            self.consumir_token()
            nodo_sent_expresion.agregar_hijo(NodoSintaxis(';'))
        else:
            self.error(f"Se esperaba ';' en la línea {self.token_actual().numero_linea}.")
        return nodo_sent_expresion

    def seleccion(self):
        nodo_seleccion = NodoSintaxis('<seleccion>')
        self.consumir_token()
        nodo_if = NodoSintaxis('sichus')
        nodo_seleccion.agregar_hijo(nodo_if)
        nodo_expresion = self.expresion()
        nodo_seleccion.agregar_hijo(nodo_expresion)
        while self.token_actual().tipo_token in ['IDENTIFICADOR'] or self.token_actual().valor in ['qawachy','cinq','sichus','do','chaykama','intq','floatq']:
            nodo_sent = NodoSintaxis('<sentencia>')
            nodo_seleccion.agregar_hijo(nodo_sent)
            if self.token_actual().tipo_token in ['IDENTIFICADOR']:
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
            if self.token_actual().valor in ['qawachy','cinq','sichus','do','chaykama']:
                nodo_sent = NodoSintaxis('<sentencia>')
                nodo_seleccion.agregar_hijo(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
            #else:
              #  nodo_declaracion = self.declaracion()
               # nodo_seleccion.agregar_hijo(nodo_declaracion)
        #nodo_sentencia = self.sentencia()
        #nodo_seleccion.agregar_hijo(nodo_sentencia)
        if self.token_actual().valor == 'manachayqa':
            nodo_else = NodoSintaxis('manachayqa')
            nodo_sent = NodoSintaxis('<sentencia>')
            nodo_seleccion.agregar_hijo(nodo_else)
            nodo_else.agregar_hijo(nodo_sent)
            self.consumir_token()
            nodo_sentencia_else = self.sentencia()
            nodo_sent.agregar_hijo(nodo_sentencia_else)
            #nodo_seleccion.agregar_hijo(nodo_sentencia_else)
        if self.token_actual().valor == 'end':
            nodo_end = NodoSintaxis('end')
            nodo_seleccion.agregar_hijo(nodo_end)
            self.consumir_token()
        else:
            self.error(f"Se esperaba 'end' en la línea {self.token_actual().numero_linea}.")
        return nodo_seleccion

    def iteracion(self):
        nodo_iteracion = NodoSintaxis('<iteracion>')
        nodo_while = NodoSintaxis('chaykama')
        nodo_iteracion.agregar_hijo(nodo_while)
        self.consumir_token()
        nodo_expresion = self.expresion()
        nodo_iteracion.agregar_hijo(nodo_expresion)
        if self.token_actual().valor == '{':
            self.consumir_token()
        else:
            self.error(f"Se esperaba 'LLAVE_ABRE' en la línea {self.token_actual().numero_linea}.")
        while self.token_actual().tipo_token in ['IDENTIFICADOR'] or self.token_actual().valor in ['qawachy','cinq','sichus','do','chaykama','intq','floatq']:
            nodo_sent = NodoSintaxis('')
            nodo_iteracion.agregar_hijo(nodo_sent)
            if self.token_actual().tipo_token in ['IDENTIFICADOR']:
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
            if self.token_actual().valor in ['qawachy','cinq','sichus','do','chaykama']:
                nodo_sent = NodoSintaxis('<sentencia>')
                nodo_iteracion.agregar_hijo(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
        #nodo_sent = NodoSintaxis('<sentencia>')
        #nodo_iteracion.agregar_hijo(nodo_sent)
        #nodo_sentencia = self.sentencia()
        #nodo_sent.agregar_hijo(nodo_sentencia)
        if self.token_actual().valor == '}':
            self.consumir_token()
        else:
            self.error(f"Se esperaba 'LLAVE_CIERRA' en la línea {self.token_actual().numero_linea}.")

        return nodo_iteracion

    def repeticion(self):
        nodo_repeticion = NodoSintaxis('<repeticion>')
        nodo_do = NodoSintaxis('do')
        nodo_repeticion.agregar_hijo(nodo_do)
        self.consumir_token()
        while self.token_actual().tipo_token in ['IDENTIFICADOR'] or self.token_actual().valor in ['qawachy','cinq','sichus','do','chaykama','intq','floatq']:

            if self.token_actual().tipo_token in ['IDENTIFICADOR']:
                nodo_sent = NodoSintaxis('<sentencia>')
                nodo_repeticion.agregar_hijo(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
            if self.token_actual().valor in ['qawachy','cinq','sichus','do','chaykama']:
                nodo_sent = NodoSintaxis('<sentencia>')
                nodo_repeticion.agregar_hijo(nodo_sent)
                nodo_sentencia = self.sentencia()
                nodo_sent.agregar_hijo(nodo_sentencia)
            else:
                nodo_declaracion = self.declaracion()
                nodo_repeticion.agregar_hijo(nodo_declaracion)
        if self.token_actual().valor == 'until':
            nodo_until = NodoSintaxis('until')
            nodo_repeticion.agregar_hijo(nodo_until)
            self.consumir_token()
            nodo_expresion = self.expresion()
            nodo_repeticion.agregar_hijo(nodo_expresion)
            if self.token_actual().valor == ';':
                self.consumir_token()
            else:
                self.error(f"Se esperaba ';' en la línea {self.token_actual().numero_linea}.")
        else:
            self.error(f"Se esperaba 'until' en la línea {self.token_actual().numero_linea}.")
        return nodo_repeticion

    def sent_in(self):
        nodo_sent_in = NodoSintaxis('<sent_in>')
        nodo_in = NodoSintaxis('cinq')
        nodo_sent_in.agregar_hijo(nodo_in)
        self.consumir_token()
        if self.token_actual().tipo_token == 'IDENTIFICADOR':
            nodo_identificador = NodoSintaxis('<identificador>', [NodoSintaxis(self.token_actual().valor)])
            nodo_sent_in.agregar_hijo(nodo_identificador)
            self.consumir_token()
        else:
            self.error(f"Se esperaba un identificador en la línea {self.token_actual().numero_linea}.")
        if self.token_actual().valor == ';':
            self.consumir_token()
            nodo_sent_in.agregar_hijo(NodoSintaxis(';'))
        else:
            self.error(f"Se esperaba ';' en la línea {self.token_actual().numero_linea}.")
        return nodo_sent_in

    def sent_out(self):
        nodo_sent_out = NodoSintaxis('<sent_out>')
        nodo_cout = NodoSintaxis('qawachy')
        nodo_sent_out.agregar_hijo(nodo_cout)
        self.consumir_token()
        nodo_expresion = self.expresion()
        nodo_sent_out.agregar_hijo(nodo_expresion)
        if self.token_actual().valor == ';':
            nodo_sent_out.agregar_hijo(NodoSintaxis(';'))
            self.consumir_token()
        else:
            self.error(f"Se esperaba ';' en la línea {self.token_actual().numero_linea}.")
        return nodo_sent_out

    def expresion(self):
        
        nodo_expresion = NodoSintaxis('<expresion>')
        nodo_expresion_simple_1 = self.expresion_simple()
        nodo_expresion.agregar_hijo(nodo_expresion_simple_1)
        if self.token_actual().valor in ['<=', '<', '>', '>=', '==', '!=']:
            nodo_relacion_op = NodoSintaxis('<relacion_op>', [NodoSintaxis(self.token_actual().valor)])
            nodo_expresion.agregar_hijo(nodo_relacion_op)
            self.consumir_token()
            nodo_expresion_simple_2 = self.expresion_simple()
            nodo_expresion.agregar_hijo(nodo_expresion_simple_2)
        return nodo_expresion

    def expresion_simple(self):
        nodo_expresion_simple = NodoSintaxis('<expresion_simple>')
        nodo_termino_1 = self.termino()
        nodo_expresion_simple.agregar_hijo(nodo_termino_1)
        while self.token_actual().valor in ['+', '-', '++', '--']:
            nodo_suma_op = NodoSintaxis('<suma_op>', [NodoSintaxis(self.token_actual().valor)])
            nodo_expresion_simple.agregar_hijo(nodo_suma_op)
            self.consumir_token()
            nodo_termino_2 = self.termino()
            nodo_expresion_simple.agregar_hijo(nodo_termino_2)
        return nodo_expresion_simple

    def termino(self):
        nodo_termino = NodoSintaxis('<termino>')
        nodo_factor_1 = self.factor()
        nodo_termino.agregar_hijo(nodo_factor_1)
        while self.token_actual().valor in ['*', '/', '%']:
            nodo_mult_op = NodoSintaxis('<mult_op>', [NodoSintaxis(self.token_actual().valor)])
            nodo_termino.agregar_hijo(nodo_mult_op)
            self.consumir_token()
            nodo_factor_2 = self.factor()
            nodo_termino.agregar_hijo(nodo_factor_2)
        return nodo_termino

    def factor(self):
        nodo_factor = NodoSintaxis('<factor>')
        if self.token_actual().valor == '(':
            self.consumir_token()
            nodo_factor.agregar_hijo(NodoSintaxis('('))
            nodo_expresion = self.expresion()
            nodo_factor.agregar_hijo(nodo_expresion)
            if self.token_actual().valor == ')':
                nodo_factor.agregar_hijo(NodoSintaxis(')'))
                self.consumir_token()
            else:
                self.error(f"Se esperaba ')' en la línea {self.token_actual().numero_linea}.")
        elif self.token_actual().tipo_token in ['ENTERO', 'REAL']:
            nodo_numero = NodoSintaxis('<numero>', [NodoSintaxis(self.token_actual().valor)])
            nodo_factor.agregar_hijo(nodo_numero)
            self.consumir_token()
        elif self.token_actual().tipo_token == 'IDENTIFICADOR':
            nodo_identificador = NodoSintaxis('<identificador>', [NodoSintaxis(self.token_actual().valor)])
            nodo_factor.agregar_hijo(nodo_identificador)
            self.consumir_token()
        else:
            self.error(f"Factor inválido en la línea {self.token_actual().numero_linea}.")
            self.consumir_token()
        return nodo_factor

# Código principal
tokens = leer_tokens('resultados.txt')  # Reemplaza 'resultados.txt' con el nombre de tu archivo de tokens

analizador_sintactico = AnalizadorSintactico(tokens)
arbol_sintaxis = analizador_sintactico.analizar()

# Función para generar el árbol sintáctico utilizando anytree
def generar_arbol_anytree(nodo, parent=None):
    current_node = Node(str(nodo.valor), parent=parent)
    for hijo in nodo.hijos:
        generar_arbol_anytree(hijo, parent=current_node)

# Generar árbol sintáctico utilizando anytree
root = Node("ArbolSintactico")
generar_arbol_anytree(arbol_sintaxis, parent=root)

print("Analisis sintactico terminado")

# Guardar el árbol sintáctico en un archivo de texto
with open('arbol_sintaxis.txt', 'w', encoding='utf-8') as archivo:
    for pre, fill, node in RenderTree(root):
        archivo.write(f"{pre}{node.name}\n")

# Guardar errores sintácticos en otro archivo
with open('errores_sintaxis.txt', 'w', encoding='utf-8') as archivo:
    for error in analizador_sintactico.errores:
        archivo.write(error + '\n')
