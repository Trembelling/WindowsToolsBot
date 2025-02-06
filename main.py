import telebot 
from telebot import types
import os
import time
import webbrowser
import requests
import platform
import ctypes
import mouse
import PIL.ImageGrab
import json
from PIL import Image, ImageDraw
import tkinter as tk
from psutil import process_iter
from win10toast import ToastNotifier
import psutil
import pyautogui
import numpy as np
import threading
import string
import random
import mouse
from methods_windowstools import *

config_file = 'config.json'
my_id = None
bot_token = None
is_recording = False
bot = None
curs_range = 50
password_to_change_account = "your_password"

def id_user_tg():
    global my_id, bot_token
    webbrowser.open('https://web.telegram.org/k/#@getmyid_bot')
    
    window = tk.Tk()
    window.title('WindowsToolsBot')
    window.geometry('500x400')
    window.resizable(width=False, height=False)

    label = tk.Label(text='Введите свой Telegram id:', bg='White', fg='Black', font='TNR 14')
    label.place(x=50, y=25)

    label1 = tk.Label(text='Введите токен своего бота Telegram:', bg='White', fg='Black', font='TNR 14')
    label1.place(x=50, y=200)

    frame1 = tk.Frame(window, width=400, height=400)
    frame1.place(x=50, y=250)
    ent1 = tk.Entry(frame1, font='TNR 10', bg='white', fg='black', width=90)
    ent1.place(x=0, y=0)

    frame = tk.Frame(window, width=200, height=100)
    ent_var = tk.StringVar()
    ent = tk.Entry(frame, textvariable=ent_var, font='TNR 14', bg='white', fg='black', width=15)

    btn = tk.Button(frame1, text='Ввод', font='TNR 14', bg='white', fg='black', command=lambda: test(ent_var.get(), ent1.get(), window))
    
    frame.place(x=25, y=65)
    ent.place(x=25, y=0)
    btn.place(x=150, y=50)
        
    window.bind('<Return>', lambda event: test(ent_var.get(), ent1.get(), window))
    window.mainloop()

def test(my_id_input, bot_token_input, window):
    global my_id, bot_token
    my_id = my_id_input
    bot_token = bot_token_input
    save_my_id()  
    window.destroy()  
    initialize_bot()  

def save_my_id():
    with open(config_file, 'w') as f:
        json.dump({"my_id": my_id, "bot_token": bot_token}, f)  

def load_my_id():
    global my_id, bot_token
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            my_id = config.get("my_id")
            bot_token = config.get("bot_token")
    else:
        id_user_tg()  

def initialize_bot():
    global bot
    bot = telebot.TeleBot(bot_token)  
    
load_my_id()

if my_id is None or bot_token is None:
    id_user_tg()
else:
    initialize_bot()  



@bot.message_handler(commands=['start'])
def send_welcome(message):
    if str(message.from_user.id) == my_id:
        bot.send_photo(my_id, "https://i.imgur.com/qrK0FaT.png", caption="Добро пожаловать в WindowsToolBot! Выберите действие из меню ниже.")
        send_main_menu(message)
    else:
        bot.send_message(message.chat.id, "Доступ запрещен.")

@bot.message_handler(commands=['reg_new_account'])
def reg_new_account(message):
    global new_id
    if message.text[17:] == password_to_change_account:
        new_id = message.from_user.id
        with open(config_file, 'w') as f:
            json.dump({"my_id": new_id, "bot_token": bot_token}, f)
        load_my_id()
        bot.send_message(message.from_user.id, "Пароль Верный, перезапустите бота")
    else:
        bot.send_message(message.chat.id, "Неправильный пароль.")


def send_first_msg(id):
    bot.send_photo(my_id, "https://i.imgur.com/qrK0FaT.png", caption="Добро пожаловать в WindowsToolBot! Выберите действие из меню ниже.")
    send_main_menu(id)

send_first_msg(my_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global curs_range
    funcs = {
    #"callback.data":command
    "screenshot": screenshot,
    "mouse_control": callback_handle_mouse_control,
    "files_and_processes": handle_files_and_processes,
    "additional_options": handle_additional_options,
    "send_notification": handler_send_notify,
    "record_screen": start_recording,
    "insert_text": handle_insert_text,
    "professionals": handle_professionals,
    "emulate_keys": handle_emulate_keys,
    "block_input": handle_block_input,
    "unblock_input": handle_unblock_input,
    "send_main_menu": send_main_menu,
}
    
    if int(call.from_user.id) == int(my_id):
        if call.data in funcs:
            funcs[call.data](call)
        elif call.data == "info":
            bot.send_message(my_id, info_msg, parse_mode="markdown")
            send_main_menu(call)
        elif call.data == "record_stop":
            stop_recording(call)
            send_main_menu(call.message)
        elif call.data == "unblock_input":
            handle_unblock_input(call)
        elif call.data == "start_process":
            bot.send_message(my_id, "Введите команду")
            bot.register_next_step_handler(call.message, start_process)
        elif call.data == "kill_process":
            bot.send_message(my_id, "Введите имя процесса")
            bot.register_next_step_handler(call.message, kill_process)
        elif call.data == "download_file":
            bot.send_message(my_id, "Отправьте путь к файлу который хотите скопировать с ПК.")
            bot.register_next_step_handler(call.message, downfile_process)
        elif call.data == "upload_file":
            bot.send_message(my_id, "Отправьте файл, после скачивания файл будет в папке с программой.")
            bot.register_next_step_handler(call.message, uploadfile_process)
        elif call.data == "upload_url":
            bot.send_message(my_id, "Отправьте ссылку на файл который хотите скачать на ПК")
            bot.register_next_step_handler(call.message, uploadurl_process)
        elif call.data == "open_url":
            bot.send_message(my_id, "Отправьте ссылку по которой нужно перейти")
            bot.register_next_step_handler(call.message, web_process)
        elif call.data == "start_command":
            bot.send_message(my_id, "Введите команду")
            bot.register_next_step_handler(call.message, cmd_process) 
        elif call.data == "turn_off_pc":
            bot.send_message(my_id, "ПК выключается")
            os.system("shutdown /s /t 1")
        elif call.data == "restart_pc":
            bot.send_message(my_id, "ПК перезагружается")
            os.system("shutdown /r /t 1")
        elif call.data == "info_pc":
            system_info()
        elif call.data == "mouse_up":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX, currentMouseY - curs_range)
            screen_process(call)

        elif call.data == "mouse_down":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX, currentMouseY + curs_range)
            screen_process(call)

        elif call.data == "mouse_left":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX - curs_range, currentMouseY)
            screen_process(call)

        elif call.data == "mouse_right":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX + curs_range, currentMouseY)
            screen_process(call)

        elif call.data == "mouse_ok":
            mouse.click()
            screen_process(call)

        elif call.data == "set_curs_range":
            bot.send_chat_action(my_id, 'typing')
            bot.send_message(my_id, "Введите значение размаха курсора")
            bot.register_next_step_handler(call.message, set_curs_range)
        elif call.data == "processes":
            bot.send_chat_action(my_id, 'typing')
            processes_names = {process.name() for process in process_iter()}
            elements_to_remove = {
                'System', 
                'System Idle Process', 
                'taskhostw.exe', 
                'svchost.exe', 
                'csrss.exe', 
                'RuntimeBroker.exe', 
                'Registry', 
                'services.exe', 
                'wininit.exe', 
                'winlogon.exe', 
                'dllhost.exe', 
                'powershell.exe', 
                'conhost.exe', 
                'explorer.exe', 
                'sihost.exe'
            }
            
            for element in elements_to_remove:
                processes_names.discard(element)
            
            sorted_processes = sorted(processes_names)
            numbered_processes = '\n'.join(f"{i + 1}. {process}" for i, process in enumerate(sorted_processes))
 
            bot.send_message(my_id, numbered_processes)
                
            bot.send_message(my_id, 'Хотите ли вы завершить какой-нибудь процесс? (да/нет)')
            send_main_menu()

def handle_professionals(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
            types.InlineKeyboardButton(text="🔄Безопасный режим", callback_data="safe_mode"),
            types.InlineKeyboardButton(text="🔄Безопасный с командной строкой", callback_data="safe_mode_cmd"),
            types.InlineKeyboardButton(text="🧬Запустить диагностику", callback_data="start_diagnostic"),
            types.InlineKeyboardButton(text="🔌Включить брандмауэр", callback_data="turnon_brand"),
            types.InlineKeyboardButton(text="🚫Выключить брандмауэр", callback_data="turnoff_brand"),
            types.InlineKeyboardButton(text="🏠Главное меню🏠", callback_data="send_main_menu"))
    bot.send_message(call.message.chat.id, "Выберите действие", reply_markup=keyboard)
                 
def handle_block_input(call):
    block_input()

@bot.callback_query_handler(func=lambda call: call.data == "emulate_keys")
def handle_emulate_keys(call):
    bot.send_message(my_id, "Введите клавишу для эмуляции")
    bot.register_next_step_handler(call.message, emulate_keypress)

@bot.callback_query_handler(func=lambda call: call.data == "unblock_input")
def handle_unblock_input(call):
    bot.send_message(my_id, "Введите код с экрана")
    bot.register_next_step_handler(call.message, check_code)
    check_code(call.message)

def callback_handle_mouse_control(call):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton(text=" ", callback_data="null"),
        types.InlineKeyboardButton(text="⬆️", callback_data="mouse_up"),
        types.InlineKeyboardButton(text=" ", callback_data="null"),
        types.InlineKeyboardButton(text="⬅️", callback_data="mouse_left"),
        types.InlineKeyboardButton(text="🆗", callback_data="mouse_ok"),
        types.InlineKeyboardButton(text="➡️", callback_data="mouse_right"),
        types.InlineKeyboardButton(text=" ", callback_data="null"),
        types.InlineKeyboardButton(text="⬇️", callback_data="mouse_down"),
        types.InlineKeyboardButton(text="Указать размах курсора", callback_data="set_curs_range"),
        types.InlineKeyboardButton(text="🏠Главное меню🏠", callback_data="send_main_menu")
    )
    bot.send_message(call.message.chat.id, "Выберите действие", reply_markup=keyboard)

def handle_files_and_processes(call):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton(text="✔️Запустить", callback_data="start_process"),
        types.InlineKeyboardButton(text="❌Завершить процесс", callback_data="kill_process"),
        types.InlineKeyboardButton(text="⬇️Скачать файл", callback_data="download_file"),
        types.InlineKeyboardButton(text="⬆️Загрузить файл", callback_data="upload_file"),
        types.InlineKeyboardButton(text="🔗Загрузить по ссылке", callback_data="upload_url"),
        types.InlineKeyboardButton(text="🏠Главное меню🏠", callback_data="send_main_menu")
    )
    bot.send_message(call.message.chat.id, "Выберите действие", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "send_notification")
def handler_send_notify(call):
    bot.send_message(call.message.chat.id, "Введите текст для уведомления:")
    bot.register_next_step_handler(call.message, get_notification_text)

@bot.callback_query_handler(func=lambda call: call.data == "insert_text")
def handle_insert_text(call):
    bot.send_message(call.message.chat.id, "Введите текст для вставки:")
    bot.register_next_step_handler(call.message, paste_text)

def get_notification_text(message):
    bot.send_chat_action(my_id, 'typing')
    notification_text = message.text.strip()
    
    # Отправка уведомления на ПК
    toaster = ToastNotifier()
    toaster.show_toast(
        "WindowsToolBot",  
        notification_text,        
        duration=10     
    )
    
    bot.send_message(my_id, f"Уведомление с текстом: \"{notification_text}\" было отправлено.")
    send_main_menu('call')

def handle_additional_options(call):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton(text="🔗Перейти по ссылке", callback_data="open_url"),
        types.InlineKeyboardButton(text="✅Выполнить команду", callback_data="start_command"),
        types.InlineKeyboardButton(text="⛔️Выключить компьютер", callback_data="turn_off_pc"),
        types.InlineKeyboardButton(text="♻️Перезагрузить компьютер", callback_data="restart_pc"),
        types.InlineKeyboardButton(text="�О компьютере", callback_data="info_pc"),
        types.InlineKeyboardButton(text="Процессы", callback_data="processes"),
        types.InlineKeyboardButton(text="🏠Главное меню🏠", callback_data="send_main_menu"))
    bot.send_message(call.message.chat.id, "Выберите действие", reply_markup=keyboard)


info_msg = '''
*О командах*
_📷Сделать скриншот_ - создает снимок экрана вместе с указателем мыши. Вы можете сохранить изображение экрана с отображением положения курсора.
_🖱Управление мышкой_ - переходит в раздел управления курсором, где вы можете перемещать указатель и выполнять клики.
_📂Файлы и процессы_ - открывает меню для управления файлами и процессами, где вы можете запускать и завершать процессы, а также управлять файлами.
_❇️Дополнительно_ - переходит в раздел с дополнительными функциями, такими как выполнение команд и управление системой.
_📩Отправка уведомления_ - отправляет на ПК глобальное уведомление.
_⏪Назад⏪_ - возвращает в главное меню, позволяя вам вернуться к предыдущему выбору.
_🔗Перейти по ссылке_ - открывает указанную ссылку. Важно указать "http://" или "https://" для открытия ссылки в стандартном браузере, а не в Internet Explorer.
_✅Выполнить команду_ - выполняет в командной строке любую указанную команду, позволяя вам управлять системой через консоль.
_⛔️Выключить компьютер_ - немедленно завершает работу компьютера, если вы хотите остановить его.
_✔️Запустить_ - открывает любые файлы (в том числе и .exe), позволяя вам запускать программы.
_⬇️Скачать файл_ - загружает указанный файл с вашего компьютера, позволяя вам передавать файлы.
_⬆️Загрузить файл_ - загружает файл на ваш компьютер, позволяя вам получать файлы от других пользователей.
_🔗Загрузить по ссылке_ - загружает файл на ваш компьютер по прямой ссылке, позволяя вам скачивать файлы из интернета.
'''

MessageBox = ctypes.windll.user32.MessageBoxW
if os.path.exists("msg.pt"):
    pass
else:
    bot.send_message(my_id, "Спасибо что использвание этого ПО!\nСоветую ознакомиться с меню \"❗️Информация", parse_mode="markdown")
    MessageBox(None, f'На вашем ПК запущена программа WindowsToolBot для управления компьютером\nДанное сообщения является разовым', '!ВНИМАНИЕ!', 0)
    f = open('msg.pt', 'tw', encoding='utf-8')
    f.close

bot.send_message(my_id, "WindowsToolsBot запущен")

def emulate_keypress(message):
    bot.send_chat_action(my_id, 'typing')
    keys_to_press = message.text.strip().split()  

    try:
        for key in keys_to_press:
            pyautogui.press(key)  
            time.sleep(0.1)  
        bot.send_message(my_id, f"Эмулированы нажатия клавиш: {', '.join(keys_to_press)}")
    except Exception as e:
        bot.send_message(my_id, f"Ошибка при эмуляции нажатия клавиш: {str(e)}")
    
    send_main_menu(message)  


def block_input():
    global unlock_code, overlay
    bot.send_message(my_id, "Ввод заблокирован.")
    unlock_code = generate_random_code(random.randint(5, 10))  
    ctypes.windll.user32.BlockInput(True)  

    
    overlay = tk.Tk()
    overlay.attributes('-fullscreen', True)  
    overlay.wm_attributes("-topmost", 1)
    overlay.configure(bg='black')  

    
    label = tk.Label(overlay, text=f"Введите код для разблокировки:\n{unlock_code}", 
                     bg='black', fg='white', font='Helvetica 24 bold')
    label.pack(expand=True)
    overlay.mainloop()

def check_code(message):
    if message.text == unlock_code:
        ctypes.windll.user32.BlockInput(False)
        overlay.destroy()
     

def system_info():
    bot.send_chat_action(my_id, 'typing')
    try:
        # Получаем информацию о системе
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        # Формируем сообщение с информацией
        info = f"""
        *Использование CPU:* {cpu_usage}%
        *Использование памяти:* {memory_info.percent}%
        *Объем памяти:* {memory_info.total / (1024 ** 3):.2f} ГБ
        *Использование диска:* {disk_info.percent}%
        *Объем диска:* {disk_info.total / (1024 ** 3):.2f} ГБ
        """
        bot.send_message(my_id, info, parse_mode="markdown")
    except Exception as e:
        bot.send_message(my_id, f"Ошибка при получении информации о системе: {str(e)}")

def screen_process(message):
    try:
        currentMouseX, currentMouseY = mouse.get_position()
        img = PIL.ImageGrab.grab()
        img.save("screen.png", "png")
        img = Image.open("screen.png")
        draw = ImageDraw.Draw(img)
        draw.polygon((currentMouseX, currentMouseY, currentMouseX, currentMouseY + 15, currentMouseX + 10, currentMouseY + 10), fill="white", outline="black")
        img.save("screen_with_mouse.png", "PNG")
        bot.send_photo(my_id, open("screen_with_mouse.png", "rb"))
        os.remove("screen.png")
        os.remove("screen_with_mouse.png")
    except:
        pass
def mousecurs_settings(message):
    bot.send_chat_action(my_id, 'typing')
    if is_digit(message.text) == True:
        User.curs = int(message.text)
        bot.send_message(my_id, f"Размах курсора изменен на {str(User.curs)}px")
    else:
        bot.send_message(my_id, "Введите целое число:")
        bot.register_next_step_handler(message, mousecurs_settings)

def uploadurl_2process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        User.fin = message.text
        obj = SmartDL(User.urldown, User.fin, progress_bar=False)
        obj.start()
        bot.send_message(my_id, f"Файл успешно сохранён по пути \"{User .fin}\"")
        
    except:
        bot.send_message(my_id, "Указаны неверная ссылка или путь")  

def kill_process_by_number(message):
    bot.send_chat_action(my_id, 'typing')
    process_number = message.text.strip() 
        
    if process_number.isdigit():
        process_number = int(process_number) - 1  
        processes_names = {process.name() for process in process_iter()}
        elements_to_remove = {
            'System', 
            'System Idle Process', 
            'taskhostw.exe', 
            'svchost.exe', 
            'csrss.exe', 
            'RuntimeBroker.exe', 
            'Registry', 
            'services.exe', 
            'wininit.exe', 
            'winlogon.exe', 
            'dllhost.exe', 
            'powershell.exe', 
            'conhost.exe', 
            'explorer.exe', 
            'sihost.exe'
        }
            
        # Удаляем системные процессы из списка
        for element in elements_to_remove:
            processes_names.discard(element)
            
        sorted_processes = sorted(processes_names)
            
        if 0 <= process_number < len(sorted_processes):
            process_to_kill = sorted_processes[process_number]
            try:
                # Завершаем процесс по имени
                for proc in process_iter():
                    if proc.name() == process_to_kill:
                        proc.terminate()  # Завершаем процесс
                        bot.send_message(my_id, f"Процесс '{process_to_kill}' был завершен.")
                        return
            except Exception as e:
                bot.send_message(my_id, f"Ошибка при завершении процесса: {str(e)}")
        else:
            bot.send_message(my_id, "Неверный номер процесса. Пожалуйста, попробуйте снова.")
            bot.register_next_step_handler(message, kill_process_by_number)  # Повторяем запрос
    else:
        bot.send_message(my_id, "Пожалуйста, введите номер процесса.")
        bot.register_next_step_handler(message, kill_process_by_number)  # Повторяем запрос

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(2)