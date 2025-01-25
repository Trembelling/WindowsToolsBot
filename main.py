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
import subprocess
import pyperclip
import pyautogui
import cv2
import numpy as np
import threading
import string
import random
import mouse

config_file = 'config.json'
my_id = None
bot_token = None
is_recording = False
bot = None
curs_range = 50

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

def send_main_menu(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="📷 Сделать скриншот", callback_data="screenshot"),
        types.InlineKeyboardButton(text="🖱 Управление мышкой", callback_data="mouse_control"),
        types.InlineKeyboardButton(text="📂 Файлы и процессы", callback_data="files_and_processes"),
        types.InlineKeyboardButton(text="❇️ Дополнительно", callback_data="additional_options"),
        types.InlineKeyboardButton(text="📩 Отправка уведомления", callback_data="send_notification"),
        types.InlineKeyboardButton(text="🎥 Записать экран", callback_data="record_screen"),
        types.InlineKeyboardButton(text="🎥 Остановить запись", callback_data="record_stop"),
        types.InlineKeyboardButton(text="📝 Вставить текст", callback_data="insert_text"),
        types.InlineKeyboardButton(text="❗️ Информация", callback_data="info"),
        types.InlineKeyboardButton(text="👾 Для профессионалов", callback_data="professionals"),
        types.InlineKeyboardButton(text="⌨️ Эмулировать нажатие клавиш", callback_data="emulate_keys"),
        types.InlineKeyboardButton(text="🔒 Заблокировать ввод", callback_data="block_input"),
        types.InlineKeyboardButton(text="🔓 Разблокировать ввод", callback_data="unblock_input")
    )
    bot.send_message(my_id, "Выберите действие", reply_markup=keyboard)

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
    "record_stop": stop_recording,
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
            bot.register_next_step_handler(call.message, confirm_kill_process)  
            bot.register_next_step_handler(call.message, addons_process)
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

menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btnscreen = types.KeyboardButton('📷Сделать скриншот')
btnmouse = types.KeyboardButton('🖱Управление мышкой')
btnfiles = types.KeyboardButton('📂Файлы и процессы')
btnaddit = types.KeyboardButton('❇️Дополнительно')
btnmsgbox = types.KeyboardButton('📩Отправка уведомления')
btn_record_screen = types.KeyboardButton('🎥Записать экран')
btn_record_screen_stop = types.KeyboardButton('🎥Остановить запись')
btnpaste = types.KeyboardButton('�Вставить текст')
btninfo = types.KeyboardButton('❗️Информация')
btnpro = types.KeyboardButton('👾Для проффесионалов')
btn_emulate_keys = types.KeyboardButton('⌨️Эмулировать нажатие клавиш')
btn_block_input = types.KeyboardButton('Заблокировать ввод')
btn_unblock_input = types.KeyboardButton('Разблокировать ввод')
menu_keyboard.row(btnscreen, btnmouse)
menu_keyboard.row(btnpaste, btn_record_screen)
menu_keyboard.row(btn_record_screen_stop, btn_emulate_keys)
menu_keyboard.row(btnfiles, btnaddit)
menu_keyboard.row(btninfo, btnmsgbox)
menu_keyboard.row(btn_block_input, btn_unblock_input)
menu_keyboard.row(btnpro)

files_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btnstart = types.KeyboardButton('✔️Запустить')
btnkill = types.KeyboardButton('❌Завершить процесс')
btndown = types.KeyboardButton('⬇️Скачать файл')
btnupl = types.KeyboardButton('⬆️Загрузить файл')
btnurldown = types.KeyboardButton('�Загрузить по ссылке')
btnback = types.KeyboardButton('⏪Назад⏪')
files_keyboard.row(btnstart, btnkill)
files_keyboard.row(btndown, btnupl)
files_keyboard.row(btnurldown, btnback)

additionals_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btnweb = types.KeyboardButton('🔗Перейти по ссылке')
btncmd = types.KeyboardButton('✅Выполнить команду')
btnoff = types.KeyboardButton('⛔️Выключить компьютер')
btnreb = types.KeyboardButton('♻️Перезагрузить компьютер')
btninfo = types.KeyboardButton('�О компьютере')
btnproccesses = types.KeyboardButton('Процессы')
btnback = types.KeyboardButton('⏪Назад⏪')
additionals_keyboard.row(btnoff, btnreb)
additionals_keyboard.row(btncmd, btnweb)
additionals_keyboard.row(btninfo, btnback)
additionals_keyboard.row(btnproccesses)

mouse_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btnup = types.KeyboardButton('⬆️')
btndown = types.KeyboardButton('⬇️')
btnleft = types.KeyboardButton('⬅️')
btnright = types.KeyboardButton('➡️')
btnclick = types.KeyboardButton('🆗')
btnback = types.KeyboardButton('⏪Назад⏪')
btncurs = types.KeyboardButton('Указать размах курсора')
mouse_keyboard.row(btnup)
mouse_keyboard.row(btnleft, btnclick, btnright)
mouse_keyboard.row(btndown)
mouse_keyboard.row(btnback, btncurs)

pro_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btnsafe = types.KeyboardButton('🔄Безопасный режим')
btnsafecmd = types.KeyboardButton('🔄Безопасный с командной строкой')
btnstartdiagnostic = types.KeyboardButton('🧬Запустить диагностику')
btnturnonbrandmwr = types.KeyboardButton('🔌Включить брандмауэр')
btnoffbrandmwr = types.KeyboardButton('🚫Выключить брандмауэр')
pro_keyboard.row(btnsafe, btnsafecmd)
pro_keyboard.row(btnstartdiagnostic)
pro_keyboard.row(btnturnonbrandmwr, btnoffbrandmwr)
pro_keyboard.row(btnback)

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

bot.send_message(my_id, "Ржавый пень запущен", reply_markup=menu_keyboard)

@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    if str(message.from_user.id) == my_id:
        bot.send_chat_action(my_id, 'typing')
        if message.text == "📷Сделать скриншот":
            bot.register_next_step_handler(message, screenshot)

        elif message.text == "🖱Управление мышкой":
            bot.send_message(my_id, "🖱Управление мышкой", reply_markup=mouse_keyboard)
            bot.register_next_step_handler(message, mouse_process)

        elif message.text == "⏪Назад⏪":
            back(message)

        elif message.text == "📂Файлы и процессы":
            bot.send_message(my_id, "📂Файлы и процессы", reply_markup=files_keyboard)
            bot.register_next_step_handler(message, files_process)

        elif message.text == "❇️Дополнительно":
            bot.send_message(my_id, "❇️Дополнительно", reply_markup=additionals_keyboard)
            bot.register_next_step_handler(message, addons_process)

        elif message.text == "📩Отправка уведомления":
            bot.send_message(my_id, "Укажите текст уведомления:")
            bot.register_next_step_handler(str.replace(message), messaga_process)
            
        elif message.text == "❗️Информация":
            bot.send_message(my_id, info_msg, parse_mode="markdown")

        elif message.text == "👾Для проффесионалов":
            bot.send_message(my_id, "👾Для проффесионалов", reply_markup=pro_keyboard)
            bot.register_next_step_handler(message, pro_func)

        elif message.text == "📋Вставить текст":
            bot.send_message(my_id, "Укажите текст для вставки:")
            bot.register_next_step_handler(message, paste_text)

        elif message.text == "🎥Записать экран":
            start_recording(message)
        elif message.text.lower() == "🎥Остановить запись":
            stop_recording(message)

        elif message.text == "⌨️Эмулировать нажатие клавиш":
            bot.send_message(my_id, "Укажите клавиши для эмуляции (например, 'ctrl c' для копирования):")
            bot.register_next_step_handler(message, emulate_keypress)

        elif message.text == "Заблокировать ввод":
            block_input()
            
            
        elif message.text == "Разблокировать ввод":
            bot.send_message(my_id, "Введите код с экрана")
            bot.register_next_step_handler(message, check_code)
             
            
        else:
            pass

    else:
        info_user(message)

def screenshot(message):
            bot.send_chat_action(my_id, 'upload_photo')
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
                bot.send_message(my_id, "Компьютер заблокирован")

def pro_func(message):
    if str(message.from_user.id) == my_id:
        bot.send_chat_action(my_id, 'typing')
        if message.text == '🔄Безопасный режим':
            os.system('bcdedit /set {default} safeboot minimal')
            os.system('shutdown /r /t 1')
            bot.register_next_step_handler(message, pro_func)
        elif message.text == '🔄Безопасный с командной строкой':
            os.system('bcdedit /set {default} safeboot minimal')
            os.system('bcdedit /set {default} safebootalternateshell yes')
            os.system('shutdown /r')
            bot.register_next_step_handler(message, pro_func)
        elif message.text == "🧬Запустить диагностику":
            run_diagnostics(message)
            bot.register_next_step_handler(message, pro_func)
        elif message.text == "🔌Включить брандмауэр":
            toggle_firewall('enable')
            bot.register_next_step_handler(message, pro_func)
        elif message.text == "🚫Выключить брандмауэр":
            toggle_firewall('disable')
            bot.register_next_step_handler(message, pro_func)
        elif message.text == "⏪Назад⏪":
            back(message)
            bot.register_next_step_handler(message, pro_func)
        else:
            pass
    else:
        info_user(message)

def paste_text(message):
    bot.send_chat_action(my_id, 'typing')
    text_to_paste = message.text.strip()
    pyperclip.copy(text_to_paste)
    pyautogui.hotkey('ctrl', 'v')  
    bot.send_message(my_id, f"Текст \"{text_to_paste}\" вставлен в активное поле ввода.")
    send_main_menu(message)  

def addons_process(message):
    if str(message.from_user.id) == my_id:
        bot.send_chat_action(my_id, 'typing')
        if message.text == "🔗Перейти по ссылке":
            bot.send_message(my_id, "Укажите ссылку: ")
            bot.register_next_step_handler(message, web_process)

        elif message.text == "✅Выполнить команду":
            bot.send_message(my_id, "Укажите консольную команду: ")
            bot.register_next_step_handler(message, cmd_process)

        elif message.text == "⛔ ️Выключить компьютер":
            bot.send_message(my_id, "Выключение компьютера...")
            os.system('shutdown -s /t 0 /f')
            bot.register_next_step_handler(message, addons_process)

        elif message.text == "♻️Перезагрузить компьютер":
            bot.send_message(my_id, "Перезагрузка компьютера...")
            os.system('shutdown -r /t 0 /f')
            bot.register_next_step_handler(message, addons_process)

        elif message.text == "🖥О компьютере":
            system_info()
            bot.register_next_step_handler(message, addons_process)

        elif message.text == "Процессы":
            if str(message.from_user.id) == my_id:
                bot.send_chat_action(my_id, 'typing')
                
                # Получаем список процессов
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
                bot.register_next_step_handler(message, confirm_kill_process)  
                bot.register_next_step_handler(message, addons_process)
                
            elif message.text == "⏪Назад⏪":
                back(message)

        else:
            pass

    else:
        info_user(message)

def files_process(message):
    if str(message.from_user.id) == my_id:
        bot.send_chat_action(my_id, 'typing')
        if message.text == "❌Завершить процесс":
            bot.send_message(my_id, "Укажите название процесса: ")
            bot.register_next_step_handler(message, kill_process)

        elif message.text == "✔️Запустить":
            bot.send_message(my_id, "Укажите путь до файла: ")
            bot.register_next_step_handler(message, start_process)

        elif message.text == "⬇️Скачать файл":
            bot.send_message(my_id, "Укажите путь до файла: ")
            bot.register_next_step_handler(message, downfile_process)

        elif message.text == "⬆️Загрузить файл":
            bot.send_message(my_id, "Отправьте необходимый файл")
            bot.register_next_step_handler(message, uploadfile_process)

        elif message.text == "🔗Загрузить по ссылке":
            bot.send_message(my_id, "Укажите прямую ссылку скачивания:")
            bot.register_next_step_handler(message, uploadurl_process)

        elif message.text == "⏪Назад⏪":
            back(message)

        else:
            pass
    else:
        info_user(message)

def record_screen():
    global is_recording
    screen_size = (1920, 1080)  
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("screen_recording.avi", fourcc, 20.0, screen_size)

    is_recording = True
    while is_recording:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()

def start_recording(message):
    bot.send_message(my_id, "Начинаю запись экрана...")
    recording_thread = threading.Thread(target=record_screen)
    recording_thread.start()
    
    bot.send_message(my_id, "Запись экрана идет. Чтобы остановить запись, введите/нажмите на кнопку '🎥Остановить запись'.")

def stop_recording(message):
    global is_recording
    is_recording = False  
    bot.send_message(my_id, "Запись экрана завершена. Отправляю файл...")
    send_recording(my_id)
    send_main_menu(message)

def send_recording(message):
    try:
        with open("screen_recording.avi", "rb") as video_file:
            bot.send_video(my_id, video_file)
        bot.send_message(my_id, "Запись экрана успешно отправлена.")
    except Exception as e:
        bot.send_message(my_id, f"Ошибка при отправке записи экрана: {str(e)}")

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

def mouse_process(message):
    if str(message.from_user.id) == my_id:
        if message.text == "⬆️":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX, currentMouseY - User.curs)
            screen_process(message)

        elif message.text == "⬇️":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX, currentMouseY + User.curs)
            screen_process(message)

        elif message.text == "⬅️":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX - User.curs, currentMouseY)
            screen_process(message)

        elif message.text == "➡️":
            currentMouseX, currentMouseY = mouse.get_position()
            mouse.move(currentMouseX + User.curs, currentMouseY)
            screen_process(message)

        elif message.text == "🆗":
            mouse.click()
            screen_process(message)

        elif message.text == "Указать размах курсора":
            bot.send_chat_action(my_id, 'typing')
            system_info(message)

        elif message.text == "⏪Назад⏪":
            back(message)

        else:
            pass
    else:
        info_user(message)

def generate_random_code(length):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

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
     
def send_notification(message):
    toaster = ToastNotifier()
    toaster.show_toast(
        "Уведомление",  
        message,        
        duration=10     
    )

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
        bot.register_next_step_handler(message, mouse_process)
        os.remove("screen.png")
        os.remove("screen_with_mouse.png")
    except:
        bot.register_next_step_handler(message, mouse_process)

def mousecurs_settings(message):
    bot.send_chat_action(my_id, 'typing')
    if is_digit(message.text) == True:
        User.curs = int(message.text)
        bot.send_message(my_id, f"Размах курсора изменен на {str(User.curs)}px", reply_markup=mouse_keyboard)
        bot.register_next_step_handler(message, mouse_process)
    else:
        bot.send_message(my_id, "Введите целое число: ", reply_markup=mouse_keyboard)
        bot.register_next_step_handler(message, mousecurs_settings)

def messaga_process(message):
	bot.send_chat_action(my_id, 'typing')
	try:
		MessageBox(None, message.text, 'WindowsToolsBot', 0)
		bot.send_message(my_id, f"Уведомление с текстом \"{message.text}\" было закрыто")
	except:
		bot.send_message(my_id, "Ошибка")

def set_curs_range(message):
    global curs_range
    try:
        curs_range = int(message.text)
        bot.send_message(my_id, f"Размах курсора изменен на {curs_range}px")
    except:
        pass

def run_diagnostics(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        # Запуск проверки диска
        disk_check = subprocess.run(['chkdsk'], capture_output=True, text=True)
        memory_check = subprocess.run(['mdsched.exe'], capture_output=True, text=True)

        # Формируем сообщение с результатами
        result = f"Результаты проверки диска:\n{disk_check.stdout}\n\n"
        result += f"Результаты проверки памяти:\n{memory_check.stdout}"

        bot.send_message(my_id, result)
    except Exception as e:
        bot.send_message(my_id, f"Ошибка при выполнении диагностики: {str(e)}")

def toggle_firewall(state):
    try:
        if state == "enable":
            os.system('netsh advfirewall set allprofiles state on')
            return "Брандмауэр включен."
        elif state == "disable":
            os.system('netsh advfirewall set allprofiles state off')
            return "Брандмауэр выключен."
    except Exception as e:
        return f"Ошибка при изменении состояния брандмауэра: {str(e)}"

def uploadurl_2process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        User.fin = message.text
        obj = SmartDL(User.urldown, User.fin, progress_bar=False)
        obj.start()
        bot.send_message(my_id, f"Файл успешно сохранён по пути \"{User .fin}\"")
        bot.register_next_step_handler(message, files_process)
    except:
        bot.send_message(my_id, "Указаны неверная ссылка или путь")
        bot.register_next_step_handler(message, addons_process)

def send_message_with_keyboard(user_id, text, keyboard):
    bot.send_message(user_id, text, reply_markup=keyboard)

def back(message):
    bot.register_next_step_handler(message, get_text_messages)
    send_message_with_keyboard(my_id, "Вы в главном меню", menu_keyboard)

def info_user(message):
    if str(message.from_user.id) != my_id:
        bot.send_chat_action(my_id, 'typing')
        alert = f"Кто-то пытался задать команду: \"{message.text}\"\n\n"
        alert += f"user id: {str(message.from_user.id)}\n"
        alert += f"first name: {str(message.from_user.first_name)}\n"
        alert += f"last name: {str(message.from_user.last_name)}\n" 
        alert += f"username: @{str(message.from_user.username)}"
        send_message_with_keyboard(my_id, alert, menu_keyboard)

def kill_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        os.system("taskkill /IM " + message.text + " -F")
        bot.send_message(my_id, f"Процесс \"{message.text}\" был завершен", reply_markup=files_keyboard)
        bot.register_next_step_handler(message, files_process)
    except:
        bot.send_message(my_id, "Ошибка! Процесс не найден", reply_markup=files_keyboard)
        bot.register_next_step_handler(message, files_process)

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

def start_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        os.startfile(r'' + message.text)
        bot.send_message(my_id, f"Файл по пути \"{message.text}\" запустился", reply_markup=files_keyboard)
        bot.register_next_step_handler(message, files_process)
    except:
        bot.send_message(my_id, "Ошибка! Указан неверный файл", reply_markup=files_keyboard)
        bot.register_next_step_handler(message, files_process)

def web_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        webbrowser.open(message.text, new=0)
        bot.send_message(my_id, f"Переход по ссылке \"{message.text}\" осуществлён", reply_markup=additionals_keyboard)
        bot.register_next_step_handler(message, addons_process)
    except:
        bot.send_message(my_id, "Ошибка! ссылка введена неверно")
        bot.register_next_step_handler(message, addons_process)

def cmd_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        os.system(message.text)
        bot.send_message(my_id, f"Команда \"{message.text}\" выполнена", reply_markup=additionals_keyboard)
        bot.register_next_step_handler(message, addons_process)
    except:
        bot.send_message(my_id, "Ошибка! Неизвестная команда")
        bot.register_next_step_handler(message, addons_process)

def say_process(message):
    bot.send_chat_action(my_id, 'typing')
    bot.send_message(my_id, "В разработке...", reply_markup=menu_keyboard)

def downfile_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        file_path = message.text
        if os.path.exists(file_path):
            bot.send_message(my_id, "Файл загружается, подождите...")
            bot.send_chat_action(my_id, 'upload_document')
            file_doc = open(file_path, 'rb')
            bot.send_document(my_id, file_doc)
            bot.register_next_step_handler(message, files_process)
        else:
            bot.send_message(my_id, "Файл не найден или указан неверный путь (ПР.: C:\\Documents\\File.doc)")
            bot.register_next_step_handler(message, files_process)
    except:
        bot.send_message(my_id, "Ошибка! Файл не найден или указан неверный путь (ПР.: C:\\Documents\\File.doc)")
        bot.register_next_step_handler(message, files_process)

def uploadfile_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(my_id, "Файл успешно загружен")
        bot.register_next_step_handler(message, files_process)
    except:
        bot.send_message(my_id, "Ошибка! Отправьте файл как документ(нельзя сжимать)")
        bot.register_next_step_handler(message, files_process)

def uploadurl_process(message):
    bot.send_chat_action(my_id, 'typing')
    User.urldown = message.text
    bot.send_message(my_id, "Укажите путь сохранения файла:")
    bot.register_next_step_handler(message, uploadurl_2process)

def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

def confirm_kill_process(message):
    if str(message.from_user.id) == my_id:
        response = message.text.strip().lower()
        
        if response == 'да':
            bot.send_message(my_id, 'Укажите номер процесса, который хотите завершить:')
            bot.register_next_step_handler(message, kill_process_by_number)  # Переход к функции завершения процесса по номеру
        elif response == 'нет':
            bot.send_message(my_id, 'Вы решили не завершать процессы. Возвращаемся в главное меню.')
            back(message)  # Возвращаемся в главное меню
        else:
            bot.send_message(my_id, 'Пожалуйста, ответьте "да" или "нет".')
            bot.register_next_step_handler(message, confirm_kill_process)  # Повторяем запрос

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(2)