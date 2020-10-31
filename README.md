Proyecto en fase beta.

La finalidad de este proyecto es llevar a cabo un registro de las horas dedicadas a cada tarea durante el trabajo.
Para ejecutarlo hay que seguir los siguientes pasos:

1ª Ejecutar script: 
	- python horario.py
2ª Una vez ejecutado, si es la primera vez que se hace, se creará la siguiente estructura:

	- directorio Usuario:
		- Jornadas
			\<AAAA>_<MM>_<DD>.txt
			\config.ini
		- history.txt
	
En el directorio Jornadas se habrá creado un fichero con nombre del día que se ha ejecutado el script. Dentro del fichero,
habrán escritas varias líneas siguiendo la siguiente estructura:

	Fecha de la jornada actual -> <AAAA>-<MM>-<DD>
	Hora de inicio -> <HH>:<MM>:<SS>
	a partir de aquí, en cada línea hay que escribir de esta manera:
	14:40 - 15:20 => [break] Comer
	15:20 - <HH>:<MM> => [break] Pasear
	<HH>:<MM> - <HH>:<MM> => [<nombre proyecto>] haciendo la tarea x

Cuando acabas, indicas la hora y el minuto.

3ª Para finalizar, hay que volver a ejecutar el script:
	- python horario.py
	Si volvemos a entrar en el fichero modificado, podremos observar que al final del todo, se ha escrito una línea:
		Fin de jornada -> <HH>:<MM>:<SS>
	Donde se verá reflejado el momento justo que hemos ejecutado el script.
	Por último, si accedemos al fichero history.txt, podremos ver que hay un resumen del txt en el que hemos escrito nuestras tareas:
	
		Resumen jornada de hoy, <AAAA>-<MM>-<DD>
		Inicio de jornada > <HH>:<MM>:<SS>
		Fin de jornada >  <HH>:<MM>:<SS>
		Duración de la jornada > <HH>:<MM>:<SS>

		Dedicación a cada tarea:
		[break] Comer > 00:20:00
		[break] Pasear > <HH>:<MM>:<SS>
		[<nombre proyecto>] > haciendo la tarea x
		
		Dedicación a cada proyecto:
		[break] > <HH>:<MM>:<SS>
		[<nombre proyecto>] > <HH>:<MM>:<SS>
		
		
		----------------------------------------

Se generará esta información cada vez que se ejecute el programa.
