import telebot
from telebot import types
import json
import tkinter as tk
import webbrowser
import os
import ctypes
import cv2
import pyautogui
import numpy as np
import mouse
import pyperclip
import random
import string
import subprocess
from win10toast import ToastNotifier
import PIL.ImageGrab
from PIL import Image, ImageDraw

config_file = 'config.json'
my_id = None
bot_token = None
is_recording = False
bot = None
MessageBox = ctypes.windll.user32.MessageBoxW

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


def messaga_process(message):
	bot.send_chat_action(my_id, 'typing')
	try:
		MessageBox(None, message.text, 'WindowsToolsBot', 0)
		bot.send_message(my_id, f"Уведомление с текстом \"{message.text}\" было закрыто")
	except:
		bot.send_message(my_id, "Ошибка")
          
def start_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        os.startfile(r'' + message.text)
        bot.send_message(my_id, f"Файл по пути \"{message.text}\" запустился")
    except:
        bot.send_message(my_id, "Ошибка! Указан неверный файл")

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
    
def send_recording(message):
    try:
        with open("screen_recording.avi", "rb") as video_file:
            bot.send_video(my_id, video_file)
        bot.send_message(my_id, "Запись экрана успешно отправлена.")
    except Exception as e:
        bot.send_message(my_id, f"Ошибка при отправке записи экрана: {str(e)}")

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

def paste_text(message):
    bot.send_chat_action(my_id, 'typing')
    text_to_paste = message.text.strip()
    pyperclip.copy(text_to_paste)
    pyautogui.hotkey('ctrl', 'v')  
    bot.send_message(my_id, f"Текст \"{text_to_paste}\" вставлен в активное поле ввода.")
    send_main_menu(message) 

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

def generate_random_code(length):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def uploadfile_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(my_id, "Файл успешно загружен")
    except:
        bot.send_message(my_id, "Ошибка! Отправьте файл как документ(нельзя сжимать)")

def info_user(message):
    if str(message.from_user.id) != my_id:
        bot.send_chat_action(my_id, 'typing')
        alert = f"Кто-то пытался задать команду: \"{message.text}\"\n\n"
        alert += f"user id: {str(message.from_user.id)}\n"
        alert += f"first name: {str(message.from_user.first_name)}\n"
        alert += f"last name: {str(message.from_user.last_name)}\n" 
        alert += f"username: @{str(message.from_user.username)}"
        send_message_with_keyboard(my_id, alert)

def send_message_with_keyboard(user_id, text):
    bot.send_message(user_id, text)

def kill_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        os.system("taskkill /IM " + message.text + " -F")
        bot.send_message(my_id, f"Процесс \"{message.text}\" был завершен")
    except:
        pass

def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False
        
def uploadurl_process(message):
    bot.send_chat_action(my_id, 'typing')
    User.urldown = message.text
    bot.send_message(my_id, "Укажите путь сохранения файла:")

def back(message):
    bot.register_next_step_handler(message, send_main_menu)
    send_message_with_keyboard(my_id, "Вы в главном меню", send_main_menu)

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




def set_curs_range(message):
    global curs_range
    try:
        curs_range = int(message.text)
        bot.send_message(my_id, f"Размах курсора изменен на {curs_range}px")
    except:
        pass

def web_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        webbrowser.open(message.text, new=0)
        bot.send_message(my_id, f"Переход по ссылке \"{message.text}\" осуществлён")
        
    except:
        bot.send_message(my_id, "Ошибка! ссылка введена неверно")
        

def cmd_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        os.system(message.text)
        bot.send_message(my_id, f"Команда \"{message.text}\" выполнена")
        
    except:
        bot.send_message(my_id, "Ошибка! Неизвестная команда")

def say_process(message):
    bot.send_chat_action(my_id, 'typing')
    bot.send_message(my_id, "В разработке...")

def downfile_process(message):
    bot.send_chat_action(my_id, 'typing')
    try:
        file_path = message.text
        if os.path.exists(file_path):
            bot.send_message(my_id, "Файл загружается, подождите...")
            bot.send_chat_action(my_id, 'upload_document')
            file_doc = open(file_path, 'rb')
            bot.send_document(my_id, file_doc)
            
        else:
            bot.send_message(my_id, "Файл не найден или указан неверный путь (ПР.: C:\\Documents\\File.doc)")

    except:
        bot.send_message(my_id, "Ошибка! Файл не найден или указан неверный путь (ПР.: C:\\Documents\\File.doc)")

def generate_random_code(length):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def send_notification(message):
    toaster = ToastNotifier()
    toaster.show_toast(
        "Уведомление",  
        message,        
        duration=10     
    )