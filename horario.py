'''
Created on 28 mar. 2019

@author: WEB2
'''
from pathlib import Path
from datetime import datetime


class Horario:

    def __init__(self):
        self.rutaDb, self.rutaHistorial = self.rutas('casa')
        self.fechaHoraEstadoProyectos = {}  # {fecha:hoy, hora:inicio_jornada, Estado:Nada}
        self.jornada = {}  # {Proyecto: {subProyecto: listaConHoras}}
        self.lista_acciones = ['Proyectos', 'Salida', 'Descanso']
        self.estadoActual = 'Nada'

    # Generar los campos necesarios para poder almacenar datos
    def preparar_campos(self):
        if not Path(self.rutaDb).is_file():
            self.generar_contenido_fichero_db('Creado fichero "db.txt" correctamente', ficherosCreados=False)
            
        historial = None
        mensaje = None
        self.fechaHoraEstadoProyectos, self.jornada = self.cargar_diccionarios(self.rutaDb)

        # si es jornada nueva, resetear datos db
        if self.fechaHoraEstadoProyectos['Fecha'] != self.getFechaActual():
            self.generar_contenido_fichero_db("Creada nueva jornada laboral", ficherosCreados=True)
        else:
            # el usuario elige que acción realizar: iniciar proyecto, descansar, ...
            accion = self.mostrar_opciones(self.lista_acciones)
            if accion[0].lower() == 'p':  # proyectos disponibles
                proyecto = self.mostrar_opciones(self.getProyectos().split(' '))
                if self.getEstado() != 'Nada':
                    proyectoAnterior = self.getEstado()
                    self.jornada[proyectoAnterior].append(self.getHoraActual())
                self.jornada[proyecto].append(self.getHoraActual())
                self.setEstado(proyecto)
            elif accion[0].lower() == 'd':  # descanso
                proyectoAnterior = self.getEstado()
                self.jornada[proyectoAnterior].append(self.getHoraActual())
                if accion not in self.jornada:
                    self.jornada[accion] = []
                self.jornada[accion].append(self.getHoraActual())
                self.setEstado(accion)
            elif accion[0].lower() == 's':  # salida
                if self.getEstado() != 'Nada':
                    ultimaTarea = self.getEstado()
                    self.jornada[ultimaTarea].append(self.getHoraActual())
                    self.setEstado('Nada')
                historial = self.escribir_en_fichero_historial(self.fechaHoraEstadoProyectos, self.jornada)
                mensaje = 'Generado historial del día de hoy'

            datos = self.rellenar_variable_datos(self.fechaHoraEstadoProyectos, self.jornada)
            self.escribir_ficheros(datos=datos, historial=historial, mensaje=mensaje)


    ####  Funciones  ####
    def setProyectos(self, ficherosCreados=True):
        lista_proyectos = list()
        if ficherosCreados:
            print('Lista de proyectos de ayer: ', self.getProyectos())
            print('¿Sigues con estos proyectos(Sí) o quieres actualizar la lista(No)?')
            respuesta = self.mostrar_opciones(['Sí', 'No'])
            if respuesta == 'Sí':
                return self.getProyectos()
        else:
            print('Creando fichero "db.txt" en el directorio {0}...'.format(self.rutaDb))
            print('Primero de todo, debes especificar los proyectos con los que vas a trabajar hoy...')
        while True:
            proyecto = input('Inserta el nombre del proyecto (vacío para terminar): ')
            if proyecto == '':
                break
            lista_proyectos.append(proyecto)
        lista_proyectos.append('Inf_General')
        return ' '.join(lista_proyectos)

    def cargar_diccionarios(self, rutaDb):
        fecha_hora_estado_proyectos_tmp = {}
        jornada_tmp = {}
        fichero = open(rutaDb, 'r')
        # leo la primera linea
        primeraLinea = fichero.readline()
        for contenido in primeraLinea.split(';'):
            clave, valor = contenido.split('-')
            fecha_hora_estado_proyectos_tmp[clave] = valor.strip()

        for linea in fichero.readlines():
            proyecto, lista_horas = linea.split('>')
            jornada_tmp[proyecto] = []
            horas = lista_horas.rstrip('\n')
            for hora in horas.split(' '):
                if hora != '':
                    jornada_tmp[proyecto].append(hora.rstrip())
        return fecha_hora_estado_proyectos_tmp, jornada_tmp

    def generar_contenido_fichero_db(self, mensaje, ficherosCreados):
        self.setProyectos(self.setProyectos(ficherosCreados))
        datos = self.linea_inicio(self.getFechaActual(), self.getHoraActual(), self.estadoActual, self.getProyectos())
        for proyecto in self.getProyectos().split(' '):
            datos += '{0}>\n'.format(proyecto)
        self.escribir_ficheros(datos=datos, mensaje=mensaje)

    def linea_inicio(self, fecha, hora, estado, proyectos):
        return 'Fecha-{0};Hora-{1};Estado-{2};Proyectos-{3}\n'.format(fecha, hora, estado, proyectos)

    def rellenar_variable_datos(self, fechaHoraEstado, jornada, lineaInicio=True):
        datos = ''
        if lineaInicio:
            datos = self.linea_inicio(fechaHoraEstado['Fecha'], fechaHoraEstado['Hora'], fechaHoraEstado['Estado'], fechaHoraEstado['Proyectos'])
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
            elif opcion_elegida == 'd' and self.getEstado() == 'Nada':
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
        if mensaje is not None: print(mensaje)

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
        historial += 'Fin de jornada > {0}\n\n'.format(self.getHoraActual())
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
            return [self.restar_horas(lista[i - 1], lista[i]) for i in range(1, len(lista), 2)][0]
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

    def getProyectos(self):
        return self.fechaHoraEstadoProyectos['Proyectos']
    
    def setEstado(self, estado):
        self.fechaHoraEstadoProyectos['Estado'] = estado
        
    def getEstado(self):
        return self.fechaHoraEstadoProyectos['Estado']

    def getHoraActual(self):
        return datetime.now().strftime("%H:%M:%S")

    def getFechaActual(self):
        return datetime.now().strftime("%Y/%m/%d")

horario = Horario()
horario.preparar_campos()