'''
Created on 22 jun. 2019

@author: Lluís
'''

import os
import sys
import codecs
from pathlib import Path
from datetime import datetime, timedelta
import smtplib, getpass
import mimetypes
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64
from email import encoders
import zipfile
import re
import configparser


class Horario:
    
    def __init__(self, folder_path, history_file_path, my_mail, passwd=None):
        self.folder_path = folder_path
        self.history_file_path = history_file_path
        self.home_path = folder_path[:14]
        self.file_name = '{0}.txt'.format(self.get_date())
        self.my_mail = my_mail
        self.passwd = passwd


    def working_day(self):
        if not os.path.exists(folder_path):
            self.__mkdir(self.folder_path)
        config_path = folder_path + '\\config.ini'
        if not Path(config_path).is_file():
            self.__nano_config(config_path)
        self.__write_file(self.home_path, self.folder_path, self.file_name, self.history_file_path)


    def extra_commands(self, command):
        if command == '-c': #cambiar correo y contraseña (cifrada)
            print('desarrollo')
        elif command == '-h': #mostrar comandos disponibles
            print('desarrollo')
        elif command == '-r': #refactorizar history.py
            print('desarrollo')
        else:
            print('Command not found. For more info "horario.py -h"')


    def __mkdir(self, folder_path):
        try:
            os.mkdir(folder_path)
        except:
            print('The folder could not be created')
        else:
            print('New folder: {0}'.format(folder_path))
        return folder_path


    def __nano_config(self, config_path):
        #config_file = codecs.open(config_path, 'w', 'utf8')
        email = input('Email: ')
        password = getpass.getpass('Password: ')

        config = configparser.ConfigParser()
        config.add_section('USER')
        config.set('USER', 'name', '')
        config.set('USER', 'email', email)
        config.set('USER', 'password', password)

        with open(config_path, 'w') as f:
            config.write(f)


    def __write_file(self, home_path, folder_path, file_name, history_file_path):
        workday_path = '{0}\\{1}'.format(folder_path, file_name)
        save_history = False
        
        if not Path(history_file_path).is_file():
            history_file = codecs.open(history_file_path, 'w', 'utf8')
            history_file.close()
             
        if not Path(workday_path).is_file(): #nueva jornada
            workday_file = codecs.open(workday_path, 'w', 'utf8')
            data = 'Fecha de la jornada actual -> {0}\nHora de inicio -> {1}\n\n'.format(self.get_date(), self.get_hour())
        else: #fin jornada
            save_history = True
            workday_file = codecs.open(workday_path, 'a', 'utf8')
            data = '\nFin de jornada -> {0}'.format(self.get_hour())
        workday_file.write(data)
        workday_file.close()
         
        if save_history:
            data = self.__save_history(folder_path, file_name)
            os.chdir(home_path)
            history_file = codecs.open(history_file_path, 'a', 'utf8')
            history_file.write(data)
            history_file.close()
        
        if save_history:
            self.__send_mail()
            
        
    def __save_history(self, folder_path, file_name):
        os.chdir(folder_path)
        file = codecs.open(file_name, 'r', 'utf8')
        
        d_workday = dict()
        d_proyects = dict()
        date_workday = file.readline().split('->')[1]
        start_hour_workday = file.readline().split('->')[1]
        end_hour_workday = None
        
        for line in file.readlines():
            line = line.strip()
            start_hour_task = end_hour_task = task = None
            if line.find('->') > 0:
                end_hour_workday = line.split('->')[1]
            else:
                if len(line) > 1:
                    hours, task = line.split('=>')
                    task = task.strip().lower()
                    #proyect = re.match('\[([^]]+)\]', task).group()
                    start_hour_task, end_hour_task = hours.split('-')
                    if task not in d_workday:
                        d_workday.update({task: [start_hour_task, end_hour_task]})
                    else:
                        d_workday.get(task).extend([start_hour_task, end_hour_task])
                    #if task.find(proyect) >= 0:
                    #    d_proyects.update({proyect: [start_hour_task, end_hour_task]})
        file.close()
        
        '''
        si salgo a comer/almorzar, lo que hago es sumarle a la hora de entrar al trabajo,
        el tiempo que he estado descansando -> workday_time
        '''
        time_list = []
        for k in d_workday:
            if k == 'break':
                time_list.extend(d_workday[k])
        if len(time_list) > 0:
            workday_time = self.__operate_hours_list(time_list)
            start_hour_workday = self.__add_hours(start_hour_workday, workday_time)
        
        historical = '\n\n--------------------------------------\n'
        historical += 'Resumen jornada de hoy, {0}\n\n'.format(date_workday)
        historical += 'Inicio de jornada > {0}\n'.format(start_hour_workday)
        historical += 'Fin de jornada > {0}\n'.format(end_hour_workday)
        historical += 'Duración de la jornada: {0}\n\n'.format(self.__subtract_hours(start_hour_workday, end_hour_workday))
        historical += 'Intervalos de tiempo para cada tarea:\n'
        historical += self.task_manager(d_workday)
        historical += '\n'
        historical += 'Dedicación a cada proyecto:\n'
        for proyect in d_proyects:
            time = self.__operate_hours_list(d_proyects[proyect] if len(d_proyects[proyect]) > 0 else '00:00:00')
            historical += '{0}>{1}\n'.format(proyect, time)
        historical += '\nDedicación a cada tarea:\n'
        for task in d_workday:
            time = self.__operate_hours_list(d_workday[task]) if len(d_workday[task]) > 0 else '00:00:00' 
            historical += '{0}>{1}\n'.format(task, time)
        return historical
        
        
    def task_manager(self, d_workday):
        data = ''
        for task in d_workday:
            data += '{0}>{1}\n'.format(task, ' '.join(d_workday[task]))
        return data
            
    
    def __operate_hours_list(self, hours_list):
        """
        Recibe una lista de horas de una tarea y/o proyecto

        :param hours_list: lista con horas
        :returns: tiempo empleado
        """
        if len(hours_list) == 2:
            return [self.__subtract_hours(hours_list[i - 1], hours_list[i]) for i in range(1, len(hours_list), 2)][0]
        else:
            hours_list = [self.__subtract_hours(hours_list[i - 1], hours_list[i]) for i in range(1, len(hours_list), 2)]
            while len(hours_list) > 2:
                hours_list_tmp = [self.__add_hours(hours_list[i - 1], hours_list[i]) for i in range(1, len(hours_list), 2)]
                if len(hours_list_tmp) % 2 != 0:
                    hours_list_tmp.append(hours_list[len(hours_list) - 1])
                hours_list = hours_list_tmp
            return [self.__add_hours(hours_list[i - 1], hours_list[i]) for i in range(1, len(hours_list), 2)][0]
    
    
    def __subtract_hours(self, start, end):
        start = start.strip()
        end = end.strip()
        if len(start.split(':')) == 2:
            start = '{0}:00'.format(start)
            end = '{0}:00'.format(end)
        str_format = "%H:%M:%S"
        h1 = datetime.strptime(start, str_format)
        h2 = datetime.strptime(end, str_format)
        return str(h2 - h1)
    
    
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
        zip_name, backup_zip, start_of_workweek, end_of_workweek = self.__files_compress()

        # Inicializo variables
        mail_to = mail_from = self.my_mail
        mail_subject = 'Jornada {0} - {1}'.format(start_of_workweek, end_of_workweek)
        mail_body = 'Periodo de jornadas: {0} hasta {1}'.format(start_of_workweek, end_of_workweek)

        # Creo el objeto mensaje
        msg = MIMEMultipart()
         
        # Establezco los atributos del mensaje
        if self.passwd is None:
            password = getpass.getpass('Contraseña ({0}): '.format(self.my_mail))
        else:
            password = self.passwd
        msg['From'] = mail_from
        msg['To'] = mail_to
        msg['Subject'] = mail_subject
         
        # Agrego el cuerpo del correo como objeto MIMO
        msg.attach(MIMEText(mail_body, 'plain'))
        
        # Creo objeto MIME base
        mail_attach = MIMEBase('application', 'octet-stream')
        # Le cargo fichero adjunto
        zp = open(zip_name, 'rb')
        mail_attach.set_payload(zp.read())
        # Codifico a BASE64
        encoders.encode_base64(mail_attach)
        # Agrego cabecera al objeto
        mail_attach.add_header('Content-Disposition', 'attachment; filename = %s' % zip_name)
        # Añado el fichero al correo
        msg.attach(mail_attach)
         
        # Creo conexión con servidor
        server = smtplib.SMTP('smtp.gmail.com: 587')
        # Cifro conexión
        server.starttls()
        # Inicio sesión
        server.login(self.my_mail, password)
        
        # Convierto el mensaje a texto
        msg = msg.as_string()
        
        # Envío el correo
        server.sendmail(mail_from, mail_to, msg)
         
        server.quit()
        server.close()
         
        print('Correo enviado a {0} satisfactoriamente'.format(self.my_mail))


    def __files_compress(self):
        end_of_workday = datetime.now()
        start_of_workday = end_of_workday - timedelta(days=4)
        end_of_workweek = end_of_workday.strftime('%Y-%m-%d')
        start_of_workweek = start_of_workday.strftime('%Y-%m-%d')
        
        # Generar comprimido y guardar los ficheros correspondientes a esta semana
        list_of_days = [d for d in range(start_of_workday.day, end_of_workday.day + 1)]
        zip_name = self.folder_path + '\\backup_{0}_{1}.zip'.format(start_of_workweek,
                                                                            end_of_workweek)
        backup_zip = zipfile.ZipFile(zip_name, 'w')
#         for folder, subfolders, files in os.walk(self.folder_path):
#             for file in files:
#                 if int(file.split('-')[2].split('.')[0]) in list_of_days:
#                     backup_zip.write(os.path.join(folder, file),
#                                      file,
#                                      compress_type=zipfile.ZIP_DEFLATED)
#
# #           file = 'history.txt'
# #         os.chdir(self.home_path)
# #         with zipfile.ZipFile(zip_name, 'a') as myzip:
# #             myzip.write(os.path.join(file),
# #                          file,
# #                          compress_type=zipfile.ZIP_DEFLATED)
# #         backup_zip.write()
# #         backup_zip.setpassword(self.passwd_zip)
        backup_zip.close()
        return zip_name, backup_zip, start_of_workweek, end_of_workweek


    def get_hour(self):
        return datetime.now().strftime("%H:%M:%S")


    def get_date(self):
        return datetime.now().strftime('%Y-%m-%d')
    
    
    
    
    
    
folder_path = 'C:\\Users\\Lluis\\Jornadas'
history_file_path = 'C:\\Users\\Lluis\\history.txt'
my_mail = 'example@gmail.com'
passwd = 'passwd'
if __name__ == '__main__':
    horario = Horario(folder_path=folder_path,
                        history_file_path=history_file_path,
                        my_mail=my_mail)
    if len(sys.argv) > 1:
        horario.extra_commands(sys.argv[1])
    else:
        horario.working_day()