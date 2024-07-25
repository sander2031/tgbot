""" Telegram бот для первого блока курса DevOPS.
 
примеры регулярных выражений для поиска телефонных номеров в тексте
 (8(\d{10})|8\(\d{3}\)\d{7}|8\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|8\ \d{3}\ \d{3}\ \d{2}\ \d{2}|8\-\d{3}\-\d{3}\-\d{2}\-\d{2}|\+7(\d{10})|\+7\(\d{3}\)\d{7}|\+7\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|\+7\ \d{3}\ \d{3}\ \d{2}\ \d{2}|\+7\-\d{3}\-\d{3}\-\d{2}\-\d{2})
 (8|\+7)((\d{10})|\(\d{3}\)\d{7}|\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|\ \d{3}\ \d{3}\ \d{2}\ \d{2}|\-\d{3}\-\d{3}\-\d{2}\-\d{2})
"""

import os
import logging
import time
import re
import platform
import paramiko
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

# Подключаем переменные из .env файла
load_dotenv()
TOKEN = os.getenv('TOKEN')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Подключаем логирование
logging.basicConfig(
    filename='logfile.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
#logging.disable(logging.CRITICAL)

logging.debug('==== START ANOTHER T BOT ====')
#logger = logging.getLogger(__name__)

# Функция вывода доступных комманд
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
                              /get_services - информация о запущенных сервисах\r\n')

### Функции для обработки диалога с пользователем

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')

    return 'findEmails'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль: ')

    return 'verifyPassword'

### Функция поиска телефонных номеров
def findPhoneNumbers(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(8\d{10}|8\(\d{3}\)\d{7}|8\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|8\ \d{3}\ \d{3}\ \d{2}\ \d{2}|8\-\d{3}\-\d{3}\-\d{2}\-\d{2}|\+7\d{10}|\+7\(\d{3}\)\d{7}|\+7\ \(\d{3}\)\ \d{3}\ \d{2}\ \d{2}|\+7\ \d{3}\ \d{3}\ \d{2}\ \d{2}|\+7\-\d{3}\-\d{3}\-\d{2}\-\d{2})') # Стоит учесть различные варианты записи номеров телефона. 8XXXXXXXXXX, 8(XXX)XXXXXXX, 8 XXX XXX XX XX, 8 (XXX) XXX XX XX, 8-XXX-XXX-XX-XX. Также вместо ‘8’ на первом месте может быть ‘+7’.

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены 😢')
        return ConversationHandler.END # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

###  Функция поиска почтовых адресов
def findEmails(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) почтовые адреса

    emailsRegex = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+') # Регулярное выражение для поска почтовых адресов.

    emailsList = emailsRegex.findall(user_input) # Ищем почтовые адреса

    if not emailsList: # Обрабатываем случай, когда почтовых адресов нет
        update.message.reply_text('Почтовые ящики не найдены 😢')
        return ConversationHandler.END# Завершаем выполнение функции
    
    emails = '' # Создаем строку, в которую будем записывать почтовые адреса
    for i in range(len(emailsList)):
        emails += f'{i+1}. {emailsList[i]}\n' # Записываем очередной почтовый адрес
        
    update.message.reply_text(emails) # Отправляем сообщение пользователю
    return ConversationHandler.END

### Функция проверки надежности пароля
def verifyPassword(update: Update, context):
    user_input = update.message.text # Введенный пароль
    passwordRegex =  re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}')
    user_password = passwordRegex.findall(user_input) # Проверка на соответствие условиям

    if not user_password: # Обрабатываем случай, когда нет совпадений с регулярным выражением 
        update.message.reply_text('Простой пароль 😢')
        return ConversationHandler.END# Завершаем выполнение функции

        
    update.message.reply_text("Сложный пароль 💪") # Отправляем сообщение пользователю, если введенный текст совпадает с регулярным выражением
    return ConversationHandler.END    

### Функции вывода системной информации
# Функция получения релиза

def getRelease(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('lsb_release -a')
        time.sleep(1)
        release_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{release_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect')     
        
    return
   
def getUname(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('uname -a')
        time.sleep(1)
        uname_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{uname_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getUptime(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('uptime')
        time.sleep(1)
        uptime_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{uptime_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getDf(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('df -h')
        time.sleep(1)
        df_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{df_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getFree(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('free')
        time.sleep(1)
        free_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{free_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getMpstat(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('mpstat')
        time.sleep(1)
        mpstat_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{mpstat_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getW(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('w')
        time.sleep(1)
        release_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{release_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getAuths(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('last | head -n10')
        time.sleep(1)
        release_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{release_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return

def getCritical(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('journalctl -p 2 | tail -n5')
        time.sleep(1)
        critical_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{critical_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return    

def getPs(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('ps')
        time.sleep(3)
        release_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(f'{release_data.decode()}')
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return    

def getSs(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('ss -uat')
        ps_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(ps_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return    

def getAptList(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
        stdin, stdout, stderr = client.exec_command('apt list | head -n10') # Костыль на вывод 10 строк.
        apt_data = stdout.read() + stderr.read()
        logging.debug(apt_data.decode())
        client.close()
        update.message.reply_text(apt_data.decode())
    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return    

def getServices(update: Update, context):
    try:
        client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False, allow_agent=False)
        update.message.reply_text('Connect successfully to: '+host)
#        update.message.reply_text('Вывести все пакеты? '+host)

#        if update.message.text == 'y':
        stdin, stdout, stderr = client.exec_command('systemctl --type=service|tail -n10') # Костыль на вывод 10 строк.
        apt_list_data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(apt_list_data.decode())
#        else:
#            pkg = update.message.text
#            stdin, stdout, stderr = client.exec_command('dpkg -l {pkg}')
#            time.sleep(1)
#            pkg_data = stdout.read() + stderr.read()
#            client.close()
#            update.message.reply_text(pkg_data.decode())

    except Exception:
        update.message.reply_text('Failed to connect') 
        
    return    


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчики диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
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


	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
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
    dp.add_handler(CommandHandler('get_apt_list', getAptList))
    dp.add_handler(CommandHandler('get_services', getServices))

	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, start))

	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
