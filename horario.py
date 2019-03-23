from pathlib import Path
from datetime import datetime
import sys


class Horario:
		
	def __init__(self):
		#Datos fijos que no se deben almacenar en otro db
		self.fechaHoraEstado = {} #{fecha:hoy, hora:inicio_jornada, Estado:Nada}
		self.jornada = {} #{Proyecto: {subProyecto: listaConHoras}}
		self.lista_acciones = ['Proyectos', 'Salida', 'Descanso']
		self.lista_proyectos = ['H3O', 'Ordoñez', 'LCADB']
		######## Usada para generar el fichero db.txt ########
		self.estadoActual = 'Nada'
		####### ######## ######## ######## ######## ######## ##
		self.horaActual = datetime.now().strftime("%H:%M:%S")
		self.fechaActual = datetime.now().strftime("%Y/%m/%d")
		self.rutaDb, self.rutaHistorial = self.rutas('casa')		
			
	#Generar los campos necesarios para poder almacenar datos
	def preparar_campos(self):
		if Path(self.rutaDb).is_file():
		
			self.fechaHoraEstado, self.jornada = self.cargar_diccionarios(self.rutaDb)
			
			#si es jornada nueva, resetear datos db
			if self.fechaHoraEstado['Fecha'] != self.fechaActual:
				self.generar_contenido_fichero_db("Creada nueva jornada laboral")
			else:
				#el usuario elige que acción realizar: iniciar proyecto, descansar, ...
				accion = self.mostrar_opciones(self.lista_acciones)
				if accion[0].lower() == 'p': #proyectos disponibles
					proyecto = self.mostrar_opciones(self.lista_proyectos)
					if self.fechaHoraEstado['Estado'] != 'Nada':
						proyectoAnterior = self.fechaHoraEstado['Estado']
						self.jornada[proyectoAnterior].append(self.horaActual)
					self.jornada[proyecto].append(self.horaActual)
					self.fechaHoraEstado['Estado'] = proyecto
					datos = self.rellenar_variable_datos(self.fechaHoraEstado, self.jornada)
					self.escribir_datos(datos=datos)
					
				elif accion[0].lower() == 'd': #descanso
					if self.fechaHoraEstado['Estado'] == 'Nada':
						print("Acabas de empezar, no puedes descansar!")
						accion = self.mostrar_opciones(self.lista_acciones)
					else:
						proyectoAnterior = self.fechaHoraEstado['Estado']
						self.jornada[proyectoAnterior].append(self.horaActual)
						if accion not in self.jornada:
							self.jornada[accion] = []
						self.jornada[accion].append(self.horaActual)
						self.fechaHoraEstado['Estado'] = accion
						datos = self.rellenar_variable_datos(self.fechaHoraEstado, self.jornada)
						self.escribir_datos(datos=datos)
				elif accion[0].lower() == 's': #salida
					ultimaTarea = self.fechaHoraEstado['Estado']
					self.jornada[ultimaTarea].append(self.horaActual)
					self.fechaHoraEstado['Estado'] = 'Nada'
					
					historial = self.escribir_en_fichero_historial(self.fechaHoraEstado, self.jornada)
					
					self.escribir_datos(historial=historial, mensaje='Generado historial del día de hoy')
					
				#self.escribir_datos(datos) #descomentar cuando funcione todo
		else: #no existe el fichero db, todo de nuevo. Sólo se hará 1 vez.
			self.generar_contenido_fichero_db('Creado fichero "db.txt" correctamente')
			
		
		
	def generar_contenido_fichero_db(self, mensaje):
		datos = self.linea_inicio(self.fechaActual, self.horaActual, self.estadoActual)
		for proyecto in self.lista_proyectos:
			datos += '{0}-\n'.format(proyecto)
		self.escribir_datos(datos=datos, mensaje=mensaje)

	def cargar_diccionarios(self, rutaDb):
		fecha_hora_estado_tmp = {}
		jornada_tmp = {}
		fichero = open(rutaDb, 'r')
		#leo la primera linea
		primeraLinea = fichero.readline()
		fecha, hora, estado = primeraLinea.split(';')
		clave, valor = fecha.split('-')
		fecha_hora_estado_tmp[clave] = valor.strip()
		clave, valor = hora.split('-')
		fecha_hora_estado_tmp[clave] = valor.strip()
		clave, valor = estado.split('-')
		fecha_hora_estado_tmp[clave] = valor.strip()
		#leo el resto de lineas
		for linea in fichero.readlines():
			proyecto, lista_horas = linea.split('-')
			jornada_tmp[proyecto] = []
			horas = lista_horas.rstrip('\n')
			for hora in horas.split(' '):
				if hora != '':
					jornada_tmp[proyecto].append(hora.rstrip())
		return fecha_hora_estado_tmp, jornada_tmp
	
	def linea_inicio(self, fecha, hora, estado):
		return 'Fecha-{0};Hora-{1};Estado-{2}\n'.format(fecha, hora, estado)
	
	def rellenar_variable_datos(self, fechaHoraEstado, jornada, lineaInicio=True):
		datos = ''
		if lineaInicio:
			datos = self.linea_inicio(fechaHoraEstado['Fecha'], fechaHoraEstado['Hora'], fechaHoraEstado['Estado'])
		for proyecto in jornada:
			horas = ''
			for h in jornada[proyecto]:
				horas += h + ' '
			datos += '{0}-{1}\n'.format(proyecto, horas)
		return datos
			
	def mostrar_opciones(self, lista):
		while True:
			dicc_tmp = {}
			for opcion in lista:
				acronimo = opcion[0].lower()
				print('{0} -> {1}'.format(acronimo, opcion))
				dicc_tmp[acronimo] = opcion	
				
			opcion_elegida = input("Elige una opción: ")
			
			if opcion_elegida not in dicc_tmp:
				print('Elección incorrecta')
			else:
				break
		return dicc_tmp[opcion_elegida]
								
	def escribir_datos(self, datos=None, historial=None, mensaje=''):
		if datos is not None:
			db = open(self.rutaDb, "w")
			db.write(datos)
			db.close()
		if historial is not None:
			db = open(self.rutaHistorial, 'a')
			db.write(historial)
			db.close()
		print(mensaje)
		
	def rutas(self, lugar):
		if lugar == 'empresa':
			db = 'C:\\Users\\Lluis\\db.txt'
			historial = 'C:\\Users\\WEB2\\tiempos.txt'
		else:
			db = 'C:\\Users\\Lluis\\db.txt'
			historial = 'C:\\Users\\Lluis\\historial.txt'
		return db, historial
		
	def escribir_en_fichero_historial(self, fechaHoraEstado, jornada):
		historial = "\n\n\n--------------------------------------\n"
		historial += "Resumen jornada de hoy, {0}\n\n".format(fechaHoraEstado['Fecha'])
		historial += 'Inicio de jornada > {0}\n'.format(fechaHoraEstado['Hora'])
		historial += 'Fin de jornada > {0}\n\n'.format(self.horaActual)
		historial += 'Tiempos de cada proyecto:\n'
		historial += self.rellenar_variable_datos(fechaHoraEstado, jornada, lineaInicio=False)
		historial += '\n'
		historial += 'Dedicación a cada proyecto:\n'
		tiempo = ''
		tiempos_sumados = []
		for proyecto in jornada:
			horas_proyecto = jornada[proyecto]
			if len(horas_proyecto) > 0:
				horas = []
				for hora in horas_proyecto:
					horas.append(hora)
				tiempo = self.restar_horas_lista(horas)
			else:
				tiempo = '00:00:00'
			tiempos_sumados.append(tiempo)
			historial += '{0} > {1}\n'.format(proyecto, tiempo)
		historial += '\n'
		tiempoTotal = self.sumar_horas_lista(tiempos_sumados)
		historial += 'Tiempo total trabajado hoy: {0}'.format(tiempoTotal)
		return historial
			
	def restar_horas_lista(self, lista):
		while len(lista) != 1:
			lista_tmp = []
			for i in range(1, len(lista), 2):
				lista_tmp.append(self.restar_horas(lista[i-1], lista[i]))
			if len(lista) % 2 != 0:
				lista_tmp.append(lista[len(lista)-1])
			lista = lista_tmp
		return lista[0]
		
	def restar_horas(self, hora1, hora2):
		formato = "%H:%M:%S"
		h1 = datetime.strptime(hora1, formato)
		h2 = datetime.strptime(hora2, formato)
		return str(h2 - h1)
	
	def sumar_horas_lista(self, lista):
		while len(lista) != 1:
			lista_tmp = []
			for i in range(1, len(lista), 2):
				lista_tmp.append(self.sumar_horas(lista[i-1], lista[i]))
			if len(lista) % 2 != 0:
				lista_tmp.append(lista[len(lista)-1])
			lista = lista_tmp
		return lista[0]
	
	def sumar_horas(self, hora1, hora2):
		formato = "%H:%M:%S"
		h1, m1, s1 = hora1.split(':')
		h2, m2, s2 = hora2.split(':')
		h_total = int(h1) + int(h2)
		m_total = int(m1) + int(m2)
		s_total = int(s1) + int(s2)
		if s_total >= 60:
			s_total -= 60
			m_total += 1
		if m_total >= 60:
			m_total -= 60
			h_total += 1
		if s_total < 10:
			s_total = '0' + str(s_total)
		if m_total < 10:
			m_total = '0' + str(m_total)
		if h_total < 10:
			h_total = '0' + str(h_total)
		total = '{0}:{1}:{2}'.format(h_total, m_total, s_total)
		return total
		
horario = Horario()
horario.preparar_campos()