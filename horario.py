'''
Created on 28 mar. 2019

@author: WEB2
'''
from pathlib import Path
from datetime import datetime
import sys


class Horario:

    def __init__(self):
        self.rutaDb, self.rutaHistorial = self.rutas('empresa')
        self.fechaHoraEstado = {}  # {fecha:hoy, hora:inicio_jornada, Estado:Nada}
        self.jornada = {}  # {Proyecto: {subProyecto: listaConHoras}}
        self.lista_acciones = ['Proyectos', 'Salida', 'Descanso']
        self.lista_proyectos = ['H3O', 'Ordoñez', 'LCADB', 'Infor_Genral'] #temporal
        self.estadoActual = 'Nada'

    # Generar los campos necesarios para poder almacenar datos
    def preparar_campos(self):
        if Path(self.rutaDb).is_file():
            historial = None
            mensaje = None
        else:
            self.generar_contenido_fichero_db('Creado fichero "db.txt" correctamente')

        self.fechaHoraEstado, self.jornada = self.cargar_diccionarios(self.rutaDb)

        # si es jornada nueva, resetear datos db
        if self.fechaHoraEstado['Fecha'] != self.fecha_actual():
            self.generar_contenido_fichero_db("Creada nueva jornada laboral")
        else:
            # el usuario elige que acción realizar: iniciar proyecto, descansar, ...
            accion = self.mostrar_opciones(self.lista_acciones)
            if accion[0].lower() == 'p':  # proyectos disponibles
                proyecto = self.mostrar_opciones(self.lista_proyectos)
                if self.fechaHoraEstado['Estado'] != 'Nada':
                    proyectoAnterior = self.fechaHoraEstado['Estado']
                    self.jornada[proyectoAnterior].append(self.hora_actual())
                self.jornada[proyecto].append(self.hora_actual())
                self.fechaHoraEstado['Estado'] = proyecto
            elif accion[0].lower() == 'd':  # descanso
                proyectoAnterior = self.fechaHoraEstado['Estado']
                self.jornada[proyectoAnterior].append(self.hora_actual())
                if accion not in self.jornada:
                    self.jornada[accion] = []
                self.jornada[accion].append(self.hora_actual())
                self.fechaHoraEstado['Estado'] = accion
            elif accion[0].lower() == 's':  # salida
                if self.fechaHoraEstado['Estado'] != 'Nada':
                    ultimaTarea = self.fechaHoraEstado['Estado']
                    self.jornada[ultimaTarea].append(self.hora_actual())
                    self.fechaHoraEstado['Estado'] = 'Nada'
                historial = self.escribir_en_fichero_historial(self.fechaHoraEstado, self.jornada)
                mensaje = 'Generado historial del día de hoy'

            datos = self.rellenar_variable_datos(self.fechaHoraEstado, self.jornada)
            self.escribir_ficheros(datos=datos, historial=historial, mensaje=mensaje)


    ####  Funciones  ####
    def cargar_diccionarios(self, rutaDb):
        fecha_hora_estado_tmp = {}
        jornada_tmp = {}
        fichero = open(rutaDb, 'r')
        # leo la primera linea
        primeraLinea = fichero.readline()
        for contenido in primeraLinea.split(';'):
            clave, valor = contenido.split('-')
            fecha_hora_estado_tmp[clave] = valor.strip()

        for linea in fichero.readlines():
            proyecto, lista_horas = linea.split('>')
            jornada_tmp[proyecto] = []
            horas = lista_horas.rstrip('\n')
            for hora in horas.split(' '):
                if hora != '':
                    jornada_tmp[proyecto].append(hora.rstrip())
        return fecha_hora_estado_tmp, jornada_tmp

    def generar_contenido_fichero_db(self, mensaje):
        datos = self.linea_inicio(self.fecha_actual(), self.hora_actual(), self.estadoActual)
        for proyecto in self.lista_proyectos:
            datos += '{0}>\n'.format(proyecto)
        self.escribir_ficheros(datos=datos, mensaje=mensaje)

    def linea_inicio(self, fecha, hora, estado):
        return 'Fecha-{0};Hora-{1};Estado-{2}\n'.format(fecha, hora, estado)

    def rellenar_variable_datos(self, fechaHoraEstado, jornada, lineaInicio=True):
        datos = ''
        if lineaInicio:
            datos = self.linea_inicio(fechaHoraEstado['Fecha'], fechaHoraEstado['Hora'], fechaHoraEstado['Estado'])
        for proyecto in jornada:
            datos += '{0}>{1}\n'.format(proyecto, ' '.join(jornada[proyecto]))
        return datos

    def mostrar_opciones(self, lista):
        while True:
            dicc_tmp = dict()
            for opcion in lista:
                acronimo = opcion[0].lower()
                print('{0} -> {1}'.format(acronimo, opcion))
                dicc_tmp[acronimo] = opcion

            opcion_elegida = input("Elige una opción: ")

            if opcion_elegida not in dicc_tmp:
                print('Elección incorrecta')
            elif opcion_elegida == 'd' and self.fechaHoraEstado['Estado'] == 'Nada':
                print("Acción no permitida")
            else:
                break
        return dicc_tmp[opcion_elegida]

    def escribir_ficheros(self, datos=None, historial=None, mensaje=None):
        if datos is not None:
            db = open(self.rutaDb, "w")
            db.write(datos)
        if historial is not None:
            db = open(self.rutaHistorial, 'a')
            db.write(historial)
        db.close()
        print(mensaje) if mensaje is not None else ''

    def rutas(self, lugar):
        if lugar == 'empresa':
            db = 'C:\\Users\\WEB2\\db.txt'
            historial = 'C:\\Users\\WEB2\\historial.txt'
        else:
            db = 'C:\\Users\\Lluis\\db.txt'
            historial = 'C:\\Users\\Lluis\\historial.txt'
        return db, historial

    def escribir_en_fichero_historial(self, fechaHoraEstado, jornada):
        historial = '\n\n--------------------------------------\n'
        historial += 'Resumen jornada de hoy, {0}\n\n'.format(fechaHoraEstado['Fecha'])
        historial += 'Inicio de jornada > {0}\n'.format(fechaHoraEstado['Hora'])
        historial += 'Fin de jornada > {0}\n\n'.format(self.hora_actual())
        historial += 'Tiempos de cada proyecto:\n'
        historial += self.rellenar_variable_datos(fechaHoraEstado, jornada, lineaInicio=False)
        historial += '\n'
        historial += 'Dedicación a cada proyecto:\n'
        for proyecto, lista_tiempos in jornada.items():
            tiempo = self.operar_horas_lista(lista_tiempos) if len(lista_tiempos) > 0 else '00:00:00'
            historial += '{0}>{1}\n'.format(proyecto, tiempo)
        return historial

    def operar_horas_lista(self, lista):
        if len(lista) == 2:
            return [self.sumar_horas(lista[i - 1], lista[i]) for i in range(1, len(lista), 2)][0]
        else:
            lista = [self.restar_horas(lista[i - 1], lista[i]) for i in range(1, len(lista), 2)]
            while len(lista) > 2:
                lista_tmp = [self.sumar_horas(lista[i - 1], lista[i]) for i in range(1, len(lista), 2)]
                if len(lista_tmp) % 2 != 0:
                    lista_tmp.append(lista[len(lista) - 1])
                    lista = lista_tmp
            return [self.sumar_horas(lista[i - 1], lista[i]) for i in range(1, len(lista), 2)][0]

    def restar_horas(self, hora1, hora2):
        formato = "%H:%M:%S"
        h1 = datetime.strptime(hora1, formato)
        h2 = datetime.strptime(hora2, formato)
        return str(h2 - h1)

    def sumar_horas(self, hora1, hora2):
        tiempo1 = hora1.split(':')
        tiempo2 = hora2.split(':')
        tiempos = [int(tiempo1[i]) + int(tiempo2[i]) for i in range(len(tiempo1))]
        for j in range(len(tiempos) - 1, 0, -1):
            if tiempos[j] >= 60:
                tiempos[j] -= 60
                tiempos[j - 1] += 1
        for i in range(len(tiempos)):
            if tiempos[i] < 10:
                tiempos[i] = '0' + str(tiempos[i])
        return '{0}:{1}:{2}'.format(tiempos[0], tiempos[1], tiempos[2])

    def hora_actual(self):
        return datetime.now().strftime("%H:%M:%S")

    def fecha_actual(self):
        return datetime.now().strftime("%Y/%m/%d")

horario = Horario()
horario.preparar_campos()