""" Telegram бот для первого блока курса DevOPS.
 
примеры регулярных выражений для поиска телефонных номеров в тексте
 (8(\d{10})|8\(\d{3}\)\d{7}|8\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|8\ \d{3}\ \d{3}\ \d{2}\ \d{2}|8\-\d{3}\-\d{3}\-\d{2}\-\d{2}|\+7(\d{10})|\+7\(\d{3}\)\d{7}|\+7\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|\+7\ \d{3}\ \d{3}\ \d{2}\ \d{2}|\+7\-\d{3}\-\d{3}\-\d{2}\-\d{2})
 (8|\+7)((\d{10})|\(\d{3}\)\d{7}|\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|\ \d{3}\ \d{3}\ \d{2}\ \d{2}|\-\d{3}\-\d{3}\-\d{2}\-\d{2})
"""

import os
import logging
import time
import datetime
import re
import platform
import paramiko
import psycopg2
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv


# Подключение переменных из .env файла.
load_dotenv()

TOKEN = os.getenv('TOKEN')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Подключение логирования.
logging.basicConfig(
    filename='logfile.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

# Выключение логирования.
#logging.disable(logging.CRITICAL)

logging.debug('==== START ANOTHER T BOT ====')
logger = logging.getLogger(__name__)


## Функция вывода доступных комманд.
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'{user.full_name}, список доступных команд:\r\n\
                              /verify_password - проверка надежности пароля\r\n\
                              ==== Поиск информации в тексте ====\r\n\
                              /find_email - поиск почтовых адресов в тексте\r\n\
                              /find_phone_number - поиск телефонных номеров в тексте\r\n\
                              ====  Мониторинг Linux-системы ====\r\n\
                              /get_release - релиз\r\n\
                              /get_uname - имя хоста, архитектура процессора, версия ядра\r\n\
                              /get_uptime - время работы хоста\r\n\
                              /get_df - информация о состоянии файловой системы\r\n\
                              /get_free - информация о состоянии оперативной памяти.\r\n\
                              /get_mpstat - информация о производительности системы\r\n\
                              /get_w - информация о работающих в данной системе пользователях.\r\n\
                              /get_auths - последние 10 входов в систему.\r\n\
                              /get_critical - последние 5 критических событий\r\n\
                              /get_ps - Информация о запущенных процессах.\r\n\
                              /get_ss - информация об используемых портах\r\n\
                              /get_apt_list - информация об установленных пакетах.\r\n\
                              /get_services - информация о запущенных сервисах.\r\n\
                              ==== Функции получения данных из базы ====\r\n\
                              /get_emails - получение сохраненных почтовых адресов.\r\n\
                              /get_phone_numbers - получение сохраненных.\r\n\
                              /get_repl_logs - получение информации о репликации.')

## Функции для обработки диалога с пользователем.
# Функция поиска телефонных номеров в тексте.
def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

# Функция поиска почтовых адресов в тексте.
def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')

    return 'findEmails'

# Функция проверки надежности введенного пароля.
def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль: ')

    return 'verifyPassword'

# Функция запроса уточнения о выводе списка пакетов.
def getAptListCommand(update: Update, context):
    update.message.reply_text('Вывод информации о всех пакетах? y / package_name')
    return 'getAptList'

# Функция поиска телефонных номеров.
def findPhoneNumbers(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов.

    phoneNumRegex = re.compile(r'(8\d{10}|8\(\d{3}\)\d{7}|8\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|8\ \d{3}\ \d{3}\ \d{2}\ \d{2}|8\-\d{3}\-\d{3}\-\d{2}\-\d{2}|\+7\d{10}|\+7\(\d{3}\)\d{7}|\+7\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|\+7\ \d{3}\ \d{3}\ \d{2}\ \d{2}|\+7\-\d{3}\-\d{3}\-\d{2}\-\d{2})') # Стоит учесть различные варианты записи номеров телефона. 8XXXXXXXXXX, 8(XXX)XXXXXXX, 8 XXX XXX XX XX, 8 (XXX) XXX XX XX, 8-XXX-XXX-XX-XX. Также вместо ‘8’ на первом месте может быть ‘+7’.

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов.

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет.
        update.message.reply_text('Телефонные номера не найдены.')
        return ConversationHandler.END # Завершаем выполнение функции.
    
    global phoneNumbers # Глобальная переменная, чтобы дотянуться до нее из другой функции.
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов.
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{phoneNumberList[i]},' # Записываем очередной номер.
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю.
    update.message.reply_text('Записать найденные телефонные номера в базу? ( y )')
    
    return 'writePhoneNumbers'  # Переходим в функцию записи.

#  Функция поиска почтовых адресов.
def findEmails(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) почтовые адреса.

    emailsRegex = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+') # Регулярное выражение для поска почтовых адресов.

    emailsList = emailsRegex.findall(user_input) # Ищем почтовые адреса.

    if not emailsList: # Обрабатываем случай, когда почтовых адресов нет.
        update.message.reply_text('Почтовые ящики не найдены.')
        return ConversationHandler.END # Завершаем выполнение функции.
    global emails # Глобальная переменная, чтобы дотянуться до нее из другой функции. 
    emails = '' # Создаем строку, в которую будем записывать почтовые адреса.

    for i in range(len(emailsList)):
        emails += f'{emailsList[i]} ' # Записываем очередной почтовый адрес.
        
    update.message.reply_text(emails) # Отправляем сообщение пользователю.
    update.message.reply_text('Записать найденные почтовые ящики? ( y )')

    return 'writeEmails' # Переходим в функцию записи.

# Функция проверки надежности пароля.
def verifyPassword(update: Update, context):
    user_input = update.message.text # Введенный пароль.
    passwordRegex =  re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}')
    user_password = passwordRegex.findall(user_input) # Проверка на соответствие условиям.

    if not user_password: # Обрабатываем случай, когда нет совпадений с регулярным выражением.
        update.message.reply_text('Простой пароль.')
        return ConversationHandler.END # Завершаем выполнение функции.

        
    update.message.reply_text("Сложный пароль.") # Отправляем сообщение пользователю, если введенный текст совпадает с регулярным выражением.
    return ConversationHandler.END # Завершаем выполнение функции.   

## Функции вывода системной информации.
# Функция получения релиза.
def getRelease(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('lsb_release -a')
        time.sleep(1)
        release_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(release_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.')     
        
    return

# Функция получения архитектуры процессора, имени хоста системы и версии ядра.    
def getUname(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('uname -a')
        time.sleep(1)
        uname_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(uname_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения информации о времени работы. linux системы.
def getUptime(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('uptime')
        time.sleep(1)
        uptime_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(uptime_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения информации о файловой системе.
def getDf(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('df -h')
        time.sleep(1)
        df_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(df_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения информации о состоянии оперативной памяти.
def getFree(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('free')
        time.sleep(1)
        free_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(free_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения информации о производительности системы.
def getMpstat(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('mpstat')
        time.sleep(1)
        mpstat_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(mpstat_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения информации о активных пользователях в системе.
def getW(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('w')
        time.sleep(1)
        w_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(w_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения информации о последних 10 входах в систему.
def getAuths(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('last | head -n10')
        time.sleep(1)
        auths_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(auths_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return

# Функция получения 5 критических событиях.
def getCritical(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('journalctl -p 2 | tail -n5')
        time.sleep(1)
        critical_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(critical_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return    

# Функция получения информации о запущенных процессах.
def getPs(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('ps')
        time.sleep(3)
        ps_data = stdout.read() + stderr.read()
        client.close()
        if len(ps_data) > 4096: # Проверка длины возвращаемого сообщения.
            for x in range(0, len(ps_data), 4096):
                update.message.reply_text(ps_data[x:x+4096].decode()) # Вывод сообщения блоками по 4096 символов.
        else:
            update.message.reply_text(ps_data.decode()) # Если сообщение <= 4096 - выводит его целиком.
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return    

# Функция получения информации об используемых портах.
def getSs(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('ss -uat')
        ss_data = stdout.read() + stderr.read()
        client.close()
        if len(ss_data) > 4096: # Проверка длины возвращаемого сообщения.
            for x in range(0, len(ss_data), 4096):
                update.message.reply_text(ss_data[x:x+4096].decode()) # Вывод сообщения блоками по 4096 символов.
        else:
            update.message.reply_text(ss_data.decode()) # Если сообщение <= 4096 - выводит его целиком.
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return    

# Функция получения информации об установленных пакетах или пакете.
def getAptList(update: Update, context):
    if update.message.text == 'y':
        try:
            client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
            update.message.reply_text('Connect successfully to: '+host)
            stdin, stdout, stderr = client.exec_command('apt list') 
            package_data = stdout.read() + stderr.read()
            client.close()
            if len(package_data) > 4096: # Проверка длины возвращаемого сообщения.
                for x in range(0, len(package_data), 4096):
                    update.message.reply_text(package_data[x:x+4096].decode()) # Вывод сообщения блоками по 4096 символов.
                client.close()
            else:
                update.message.reply_text(package_data.decode())
                client.close()
        except Exception:
            update.message.reply_text('Failed to connect.') 
        return ConversationHandler.END
    else:
        try:
            client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
            update.message.reply_text('Connect successfully to: '+host)
            stdin, stdout, stderr = client.exec_command('dpkg -s '+update.message.text) 
            package_data = stdout.read() + stderr.read()
            client.close()
            if len(package_data) > 4096: # Проверка длины возвращаемого сообщения.
                for x in range(0, len(package_data), 4096):
                    update.message.reply_text(package_data[x:x+4096].decode()) # Вывод сообщения блоками по 4096 символов.
                client.close()
            else:
                update.message.reply_text(package_data.decode())
                client.close()
        except Exception:
            update.message.reply_text('Failed to connect.') 
        return ConversationHandler.END       

# Функция получения информации о запущенных сервисах.
def getServices(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('systemctl --type=service') 
        service_list_data = stdout.read() + stderr.read()
        client.close()
        if len(service_list_data) > 4096: # Проверка длины возвращаемого сообщения.
            for x in range(0, len(service_list_data), 4096):
                update.message.reply_text(service_list_data[x:x+4096].decode()) # Вывод сообщения блоками по 4096 символов.
        else:
            update.message.reply_text(service_list_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return    

# Функции работы с базой данных.
# Функция получения почтовых адресов.
def getEmails(update: Update, context):
    try:
        db_connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_database)
        cursor = db_connection.cursor()
        cursor.execute("SELECT email FROM emails")
        emails_data = cursor.fetchall()
        for row in emails_data:
            update.message.reply_text(row)
        cursor.close()
        db_connection.close()
    except Exception:
        update.message.reply_text('Failed DB connect.')

    return

# Функция получения телефонных номеров.
def getPhoneNumbers(update: Update, context):
    try:
        db_connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_database)
        cursor = db_connection.cursor()
        cursor.execute("SELECT phone FROM phone_numbers")
        phone_numbers_data = cursor.fetchall()
        for row in phone_numbers_data:
            update.message.reply_text(row)
        cursor.close()
        db_connection.close()
    except Exception:
        update.message.reply_text('Failed DB connect.')

    return

# Функция записи найденных почтовых адресов.
def writeEmails(update: Update, context):    
    user_input = update.message.text
    if user_input == 'y':
        try:
            add_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            request_to_insert = "INSERT INTO emails (email, insert_time) VALUES ( %s, %s)"
            db_connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_database)
            db_cursor = db_connection.cursor()
            mails_list = list(emails.split(" "))
            for row in mails_list:
                db_cursor.execute(request_to_insert, (row, add_time))
            db_connection.commit()
            db_cursor.close()
            db_connection.close()
            update.message.reply_text('Успешно записано в базу.')
            return ConversationHandler.END
        except Exception:
            update.message.reply_text('Ошибка подключения к базе.')
            return ConversationHandler.END
    else:
        update.message.reply_text('Ничего не записано в базу.')
        return ConversationHandler.END    
    
# Функция записи найденных телефонных номеров.
def writePhoneNumbers(update: Update, context):    
    user_input = update.message.text
    if user_input == 'y':
        try:
            add_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            request_to_insert = "INSERT INTO phone_numbers (phone, insert_time) VALUES ( %s, %s)"
            db_connection = psycopg2.connect(user=db_username, password=db_password, host=db_host, port=db_port, database=db_database)
            db_cursor = db_connection.cursor()
            phone_numbers_list = list(phoneNumbers.split(","))
            for row in phone_numbers_list:
                db_cursor.execute(request_to_insert, (row, add_time))
            db_connection.commit()
            db_cursor.close()
            db_connection.close()
            update.message.reply_text('Успешно записано в базу.')
            return ConversationHandler.END
        except Exception:
            update.message.reply_text('Ошибка подключения к базе.')
            return ConversationHandler.END
    else:
        update.message.reply_text('Ничего не записано в базу.')
        return ConversationHandler.END

# Функция получения информации о репликации.
def getReplLogs(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('cat /var/log/postgresql/postgresql-14-main.log |grep repl_user') 
        logs_data = stdout.read() + stderr.read()
        client.close()
        if len(logs_data) > 4096: # Проверка длины возвращаемого сообщения.
            for x in range(0, len(logs_data), 4096):
                update.message.reply_text(logs_data[x:x+4096].decode()) # Вывод сообщения блоками по 4096 символов.
        else:
            update.message.reply_text(logs_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect.') 
        
    return  

# Основная функция.
def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков.
    dp = updater.dispatcher

    # Обработчики диалога.
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'writePhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, writePhoneNumbers)]
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'writeEmails': [MessageHandler(Filters.text & ~Filters.command, writeEmails)]            
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'getAptList': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )   

	# Регистрируем обработчики команд.
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('get_release', getRelease))
    dp.add_handler(CommandHandler('get_uname', getUname))
    dp.add_handler(CommandHandler('get_uptime', getUptime))
    dp.add_handler(CommandHandler('get_df', getDf))
    dp.add_handler(CommandHandler('get_free', getFree))
    dp.add_handler(CommandHandler('get_mpstat', getMpstat))
    dp.add_handler(CommandHandler('get_w', getW))
    dp.add_handler(CommandHandler('get_auths', getAuths))
    dp.add_handler(CommandHandler('get_critical', getCritical))
    dp.add_handler(CommandHandler('get_ps', getPs))
    dp.add_handler(CommandHandler('get_ss', getSs))
    dp.add_handler(CommandHandler('get_services', getServices))
    dp.add_handler(CommandHandler('get_emails', getEmails))
    dp.add_handler(CommandHandler('get_phone_numbers', getPhoneNumbers))
    dp.add_handler(CommandHandler('get_repl_logs', getReplLogs))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerGetAptList)
 

	# Регистрируем обработчик текстовых сообщений.
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, start))

	# Запускаем бота.
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C.
    updater.idle()


if __name__ == '__main__':
    main()

