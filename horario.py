"""
Created on 22 jun. 2019

@author: Lluís
"""

# TODO: \
#   cifrar contraseña en el fichero de configuración \
#   enviar por correo copias de las jornadas \
#   backup cada semana \
#   limpiar código \

import os
import sys
import codecs
from pathlib import Path
from datetime import datetime
import getpass
import re
import configparser
import calendar
from shutil import move
from zipfile import ZipFile


class Horario:

    def __init__(self):
        self.home_user_path = Path.home().as_posix()
        self.folder_path = os.path.join(self.home_user_path, 'Jornadas')
        self.history_file_path = os.path.join(self.home_user_path, 'history.txt')
        self.file_name = '{0}.txt'.format(self.get_date_str())
        self.config_path = os.path.join(self.folder_path, 'config.ini')
        self.d_commands_str = {'\n\t\t-c': 'cambia los datos del usuario almacenados en el fichero de configuración.',
                               '-h': 'imprime este mensaje de ayuda.',
                               #'-r': 'refactoriza todo el contenido del fichero "history" con el formato de la \n'
                               #      '\t\t\tversión actual.',
                               '-f': 'recalcula las horas del fichero indicado como segundo argumento:\n'
                                     '\t\t\t-f <jornada>.txt (la extensión no es obligatoria).',
                               '-b': 'hace backup del mes pasado como segundo argumento o -1 para todos los meses'}

    def working_day(self, extra_commands=None):
        """
        Primera función a ejecutar. Inicializa la ejecución del programa.
        :type extra_commands: el usuario quiere realizar una acción específica.
        """
        if not os.path.exists(self.folder_path):  # No existe directorio 'Jornadas'
            self.__mkdir(self.folder_path)
        if not Path(self.config_path).is_file():  # No existe fichero 'config'
            self.__nano_config(self.config_path)
        if extra_commands is not None:  # Se ha especificado un comando
            self.extra_commands(extra_commands)
        else:  # Genera fichero para el día que se ejecuta
            self.__write_file(self.home_user_path, self.folder_path, self.file_name, self.history_file_path)
        
    def extra_commands(self, argvs):
        """
        Redirige a la función que corresponde según el parámetro indicado por el usuario.
        :type argvs: comando extra añadido al ejecutar el script.
        """
        command = argvs[1]
        if command == '-c':  # cambiar correo y contraseña (cifrada)
            self.__c_command(self.config_path)
        elif command == '-h':  # mostrar comandos disponibles
            self.__h_command(self.d_commands_str)
        elif command == '-r':  # refactorizar history.py
            self.__r_command(self.history_file_path)
        elif command == '-f':  # actualizar fichero
            workday_file = argvs[2]
            if workday_file.find('.txt') == -1:  # no tiene extensión
                workday_file += '.txt'
            self.__f_command(self.home_user_path, self.folder_path, workday_file, self.history_file_path)
        elif command == '-b':  # backup
            backup_month = None
            if len(argvs) == 3:  # ha pasado parámetro
                try:
                    backup_month = int(argvs[2])
                except:
                    pass
            return self.__b_command(backup_month)
        else:
            print('Command not found. For more info "horario.py -h"')

    def __mkdir(self, folder_path):
        """
        Crea directorio 'Jornadas' en el directorio principal del usuario (si no existe).
        :param folder_path: directorio donde generar directorio 'Jornadas'.
        """
        try:
            os.mkdir(folder_path)
        except Exception:
            print('The folder could not be created')
        else:
            print('New folder: {0}'.format(folder_path))

    def __nano_config(self, config_path):
        """
        Genera fichero configuración con datos del usuario.
        :param config_path: path donde guardar el fichero de configuración.
        """
        username = input('Username: ')
        email = input('Email: ')
        password = getpass.getpass('Password: ')

        config = configparser.ConfigParser()
        config.add_section('USER')
        config.set('USER', 'name', username)
        config.set('USER', 'email', email)
        config.set('USER', 'password', password)

        with open(config_path, 'w') as f:
            config.write(f)

    def __write_file(self, home_user_path, folder_path, file_name, history_file_path):
        workday_file_path = '{0}{1}{2}'.format(folder_path, os.sep, file_name)  # path fichero jornada actual
        save_history = False

        if not Path(history_file_path).is_file():
            history_file = codecs.open(history_file_path, 'w', 'utf8')
            history_file.close()

        if not Path(workday_file_path).is_file():  # nueva jornada
            workday_file = codecs.open(workday_file_path, 'w', 'utf8')
            data = 'Fecha de la jornada actual -> {0}\nHora de inicio -> {1}\n\n'.format(self.get_date_str(),
                                                                                         self.get_time_str())
        else:  # fin jornada
            save_history = True
            workday_file = codecs.open(workday_file_path, 'a', 'utf8')
            data = '\nFin de jornada -> {0}'.format(self.get_time_str())
        workday_file.write(data)
        workday_file.close()

        if save_history:
            self.summary_workday(home_user_path, folder_path, workday_file_path, history_file_path)
        #     self.__send_mail()
        
        if self.check_last_day_of_month():
            self.__generate_backup(datetime.now().month - 1)


    def summary_workday(self, home_user_path, folder_path, workday_file, history_file_path):
        """
            Le pasas el nombre del fichero de la jornada que quieres actualizar y recalcula tanto
            el fichero indicado como el día en history.

            :param home_user_path: path directorio HOME
            :param folder_path: path directorio Jornadas
            :param workday_file: fichero jornada que se quiere recalcular horas
            :param history_file_path: path fichero history.py
            :return: fichero history.py con el recálculo del fichero indicado
        """
        data = self.__save_history(folder_path, workday_file)
        os.chdir(home_user_path)
        history_file = codecs.open(history_file_path, 'a', 'utf8')
        history_file.write(data)
        history_file.close()

    def __save_history(self, folder_path, workday_file_path):
        os.chdir(folder_path)
        file = codecs.open(workday_file_path, 'r', 'utf8')

        date_workday, start_hour_workday, end_hour_workday, d_workday = self.__prepare_data_to_history_file(file)
        '''
        si hago un descanso, lo que hago es sumarle a la hora de entrada al trabajo,
        el tiempo que he estado descansando -> workday_time
        '''
        if '[break]' in d_workday:
            time_break = [start_hour_workday]
            for k, v in d_workday['[break]'].items():
                time_break.extend(v)
            self.add_hours_of_list(time_break)
            start_hour_workday_fake = time_break[0]
        else:
            start_hour_workday_fake = start_hour_workday

        historical = '\n\n--------------------------------------\n'
        historical += 'Resumen jornada de hoy, {0}\n'.format(date_workday)
        historical += 'Inicio de jornada > {0}\n'.format(start_hour_workday)
        historical += 'Fin de jornada > {0}\n'.format(end_hour_workday)
        historical += 'Duración de la jornada > {0}\n\n'.format(
            self.__subtract_hours(start_hour_workday_fake, end_hour_workday))
        historical += 'Dedicación a cada tarea:\n'
        for project, tasks in d_workday.items():
            for task in tasks:
                self.add_hours_of_list(tasks[task])
                historical += '{0}{1}> {2}\n'.format(project, task, tasks[task][0])
        historical += '\nDedicación a cada proyecto:\n'
        for project in d_workday:
            tasks = d_workday[project]
            time_l = []
            for task in tasks:
                time_l.extend(tasks[task])
            self.add_hours_of_list(time_l)
            historical += '{0} > {1}\n'.format(project, time_l[0])
        return historical

    def add_hours_of_list(self, lista):
        """
        Suma recursivamente los tiempos pasados por parámetro.
        :param lista: contiene los tiempos a sumar
        """
        if len(lista) == 1:
            return lista
        t1 = lista.pop()
        t2 = lista.pop()
        lista.append(self.__add_hours(t1, t2))
        self.add_hours_of_list(lista)

    def __prepare_data_to_history_file(self, file):
        d_workday = dict()
        date_workday = file.readline().split('->')[1].strip()
        start_hour_workday = file.readline().split('->')[1].strip()
        end_hour_workday = None
        for line in file.readlines():
            line = line.strip()
            if line.find('->') > 0:
                end_hour_workday = line.split('->')[1]
            else:
                if len(line) > 1:
                    hours, task = line.split('=>')
                    task = task.strip().lower()
                    project = re.match('.*] ?', task).group()
                    project = project.strip()
                    task_project = task.split(']')[1]
                    hours = [h.strip() for h in hours.split('-')]
                    start_hour_task = hours[0]
                    end_hour_task = hours[1]
                    is_valid_hours, time = self.validate_hours(start_hour_task, end_hour_task)
                    if is_valid_hours:
                        if project not in d_workday:
                            d_workday.update({project: {task_project: [time]}})
                        else:
                            if task_project not in d_workday[project]:
                                d_workday[project].update({task_project: [time]})
                            else:
                                d_workday[project][task_project].append(time)
                    else:
                        print('Las horas introducidas son incorrectas. Corrígelas y vuelve a ejecutar el programa. \n{0}'.format(line))
                        sys.exit()
        file.close()
        return date_workday, start_hour_workday, end_hour_workday, d_workday

    def validate_hours(self, start_hour_task, end_hour_task):
        """
        Recibe la hora de inicio y fin de una tarea y comprueba que inicio < fin
        :param start_hour_task: hora inicio tarea
        :param end_hour_task: hora fin tarea
        :return: inicio < fin (bool) y tiempo dedicado a esa tarea
        """
        total = self.__subtract_hours(start_hour_task, end_hour_task)
        h, m, s = total.split(':')
        return (int(h) * 3600 + int(m) * 60) >= 0, total

    def __subtract_hours(self, start, end):
        start = start.strip()
        end = end.strip()
        if len(start.split(':')) == 2:
            start = '{0}:00'.format(start)
            end = '{0}:00'.format(end)
        str_format = "%H:%M:%S"
        h1 = datetime.strptime(start, str_format)
        h2 = datetime.strptime(end, str_format)
        total = str(h2 - h1)
        if len(total.split(':')[0]) == 1:
            total = '0' + total
        return total

    def __add_hours(self, start, end):
        start = start.split(':')
        end = end.split(':')
        times = [int(start[i]) + int(end[i]) for i in range(len(start))]
        for j in range(len(times) - 1, 0, -1):
            if times[j] >= 60:
                times[j] -= 60
                times[j - 1] += 1
        for i in range(len(times)):
            if times[i] < 10:
                times[i] = '0' + str(times[i])
        return '{0}:{1}:{2}'.format(times[0], times[1], times[2])

    def __send_mail(self):
        #  self.__files_compress()
        pass

    def check_last_day_of_month(self):
        """
        Comprueba si es último día laboral del mes.
        """
        # Obtengo las 2 últimas jornadas y comparo los meses: son distintos -> genero Backup del mes anterior
        l_last_workdays = []
        for f in reversed(os.listdir(self.folder_path)):
            if f.split('.')[1] == 'txt':
                l_last_workdays.append(f)
            if len(l_last_workdays) == 2:
                break

        first_month_field = int(l_last_workdays[0].split('-')[1])
        second_month_field = int(l_last_workdays[1].split('-')[1])
        return first_month_field != second_month_field

    def __generate_backup(self, backup_month, is_cur_date=True):
        """TODO: entrar en 'history.txt', copiar sección mes actual, generar otro 'history.txt' dentro
                del backup de las jornadas"""
        backups_dir = self.folder_path + '/Backups'
        if not os.path.isdir(backups_dir):
            os.mkdir(backups_dir)
        cur_date = datetime.now()
        if (cur_date.day != calendar.monthrange(cur_date.year, backup_month) and is_cur_date) or not is_cur_date:
            try:
                #os.mkdir(os.path.join(self.folder_path, bckup_name))
                if backup_month <= 9:
                    data_str = '{0}-0{1}'.format(cur_date.year, backup_month)
                else:
                    data_str = '{0}-{1}'.format(cur_date.year, backup_month)
                zip_name = 'Backup ' + data_str + '.zip'
                os.chdir(self.folder_path)
                zipObj = ZipFile(zip_name, 'w')
                #bckup_name = 'Backup {0}-{1}'.format(cur_date.year, backup_month)
                zipf = None
                #bckup_path = self.folder_path + bckup_name
                content = os.listdir(self.folder_path)
                count_files = 0
                for file in content:
                    try:    
                        f = file.split('.')[0].split('-')
                        f_year, f_month, f_day = int(f[0]), int(f[1]), int(f[2])
                        if f_month == backup_month and f_year == cur_date.year:
                            zipObj.write(os.path.basename(file))
                            count_files += 1
                    except:
                        pass
                zipObj.close()
                if count_files == 0:  # No hay ficheros para esa fecha, borramos zip
                    os.remove(zip_name)
                    print('No hay ficheros para la fecha ', data_str)
                else:
                    move(zip_name, backups_dir)
                    print('Copia realizada correctamente para fecha ', data_str)
            except:
                print('Ha ocurrido un error y no se ha podido hacer el back up.')


    def __files_compress(self):
        pass

    def get_time_str(self):
        return datetime.now().strftime("%H:%M:%S")

    def get_date_str(self):
        return datetime.now().strftime('%Y-%m-%d')

    def __h_command(self, d_commands_str):
        txt = """
        NOMBRE
                Horario - gestor de jornadas (versión 3.0)
            
        REQUISITOS
                Python >= 3.0
        
        DESCRIPCIÓN
                Este programa tiene la finalidad de contabilizar las horas dedicadas a cada jornada laboral. Al 
                ejecutarlo, genera un fichero en el que se tienen que indicar la hora de inicio y de fin de cada 
                tarea realizada. Una vez finalizada la jornada, se vuelve a ejecutar la aplicación y se contabiliza 
                el tiempo empleado en cada tarea.
        """
        for key, value in d_commands_str.items():
            txt += '\t\t{0}\t{1}\n'.format(key, value)
        print(txt)

    def __r_command(self, history_file):
        print('coming soon... :)')
        pass

    def __c_command(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        section = 'USER'
        user = config[section]
        for key in user:
            finish = False
            while not finish:
                option_selected = input('{0}: {1} --> Do you want to change it (Y/N)? '.format(key, user[key])).lower()
                if option_selected == 'y':
                    config.set(section, key, input('New {0}: '.format(key)))
                    finish = True
                elif option_selected == 'n':
                    finish = True
                    continue
                else:
                    print('Incorrect option.')
        with open(config_path, 'w') as configuration_file:
            config.write(configuration_file)

    def __f_command(self, home_user_path, folder_path, workday_file, history_file_path):
        try:
            self.summary_workday(home_user_path, folder_path, workday_file, history_file_path)
        except ValueError:
            print('Ops, no ha podido actualizarse correctamente.')
        else:
            print('Fichero history.py actualizado!')

    def __b_command(self, backup_month=None):
        if backup_month is not None and isinstance(backup_month, int):
            if backup_month == -1:
                for i in range(1, 13):
                    self.__generate_backup(i, is_cur_date=False)
                return
            elif backup_month >= 1 and backup_month <= 12:
                return self.__generate_backup(backup_month, is_cur_date=False)
            else:
                print('Mes incorrecto')
        else:
            print('Dato incorrecto')
        try:
            backup_month = int(input('Introduce (en número) el mes para hacer backup (-1 para todos los meses): '))
        except:
            backup_month = None
        return self.__b_command(backup_month)    
            


if __name__ == '__main__':
    if len(sys.argv) > 1:
        Horario().working_day(sys.argv)
    else:
        Horario().working_day()
