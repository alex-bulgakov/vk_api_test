import csv
import re
from datetime import datetime
import os
import sys
import threading
import time
import tkinter as tk
import msvcrt

import requests
import vk_api

import json


debug_flag = False
def debug_msg(msg):
    if debug_flag:
        print(msg)


vk = None
group_checkboxes = []
status_text = ''
file_name = 'result.csv'
stop = False


def set_status(msg):
    status.configure(text=msg)

def update_label(label):
    while True:
        label.configure(text=status_text)
        time.sleep(1)


# Функция получения названия группы по ID
def get_group_name(group_id):
    for key in group_checkboxes:
        if group_id in key:
            return key[0]

# Функция авторизации в VK API
def vk_auth(login, password):

    #Создадим файл для записи результата
    with open(file_name, 'w+') as f:
        f.write('')


    if login == '' or password == '':
        # получаем путь к директории, содержащей исполняемый файл
        dir_path = os.path.dirname(os.path.abspath(sys.executable))

        with open(dir_path +'\\auth.txt', 'r') as f:
            login = f.readline().strip()
            password = f.readline().strip()
    try:
        global vk, group_checkboxes, group_name
        vk_session = vk_api.VkApi(login, password)
        vk_session.auth()
        vk = vk_session.get_api()
        groups = vk.groups.get(extended=1, fields="name")["items"]
        check_row = 0
        for group in groups:
            group_checkboxes.append((group["name"], group["id"], tk.BooleanVar()))
        for checkbox in group_checkboxes:
            tk.Checkbutton(inner_frame, text=checkbox[0], variable=checkbox[2], bg=canvas_color, fg='#888888').grid(row=check_row, column=2, sticky='w', padx=5)
            check_row += 1

        set_status('Авторизация успешна')
    except vk_api.AuthError as error_msg:
        print(error_msg)


def search_group(vk, group_id, queries, start_date, posts):
    result = []
    try:
        set_status('Ищем в группе - ' + str(get_group_name(group_id)))
    except:
        pass
    offset = 0
    global flag
    flag = True
    is_pinned = False


    while flag:
        if stop: return
        response = vk.wall.get(owner_id=-group_id, count=100, offset=offset, extended=1)
        items = response["items"]
        for post in items:
            if stop: return
            post_date = datetime.fromtimestamp(post["date"])

            is_pinned = False
            try:
                is_pinned = post['is_pinned'] == 1
            except:
                pass

            if post_date >= start_date or is_pinned:
                post_id = post["id"]
                if post['comments']['count'] > 0:
                    comments = vk.wall.getComments(owner_id=-group_id, post_id=post_id, count=100, sort='desc',
                                                   preview_length=0, extended=1)
                    for comment in comments['items']:
                        for query in queries:
                            if stop:
                                return []
                            if query.strip() in comment['text']:
                                try:
                                    set_status('Нашли в комменте - ' + str(comment['text'][0:30]))
                                except:
                                    pass
                                result.append({
                                    'group_id' : group_id,
                                    'post_id': post_id,
                                    'id': comment['id'],
                                    'from_id': comment['from_id'],
                                    'text': comment['text']
                                })

            else:
                flag = False
                break
        offset += 100
        if offset >= response["count"]:
            break

    return result


def search_and_save(vk, group_checkboxes, query, start_date):
    global stop
    set_status('Начинаем поиск')
    if start_date == '':
        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day)
    else:
        start_date = datetime.strptime(start_date, '%d.%m.%Y')

    queries = query.split(',')
    selected_group_ids = [checkbox[1] for checkbox in group_checkboxes if checkbox[2].get()]
    posts = []

    for group_id in selected_group_ids:
        if stop:
            set_status('Поиск прерван')
            stop = False
            return
        posts += search_group(vk, group_id, queries, start_date, posts)

    set_status('Записываем результат в файл')
    with open(file_name, mode='w', encoding='cp1251', newline='') as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, os.path.getsize(file_name))
        writer = csv.writer(f)
        writer.writerow(['Post URL', 'User URL', 'Comment Text'])
        for post in posts:
            post_str = re.sub(r"[^a-zA-ZА-Яа-я0-9]+", " ", post['text'])
            writer.writerow([f"https://vk.com/wall-{post['group_id']}_{post['post_id']}",
                             f"https://vk.com/id{post['from_id']}",
                             post_str[0:100]])
            if stop:
                set_status('Поиск прерван')
                stop = False
                return
    set_status('Готово')

def start_search():
    # Создаем поток для выполнения функции search_and_save
    search_thread = threading.Thread(target=search_and_save, args=(vk, group_checkboxes, search_entry.get(), start_date_entry.get()))
    search_thread.start()


def stop_thread():
    global stop
    stop = True

# Создание графического интерфейса

button_bg_color = '#101010'
button_color = 'white'
canvas_color = '#2d2d2d'

root = tk.Tk()
root.title('VK Поиск')

# Определяем размер экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Вычисляем размер окна
window_width = screen_width // 2
window_height = screen_height // 2

# Вычисляем координаты окна, чтобы оно отображалось по центру экрана
x_position = screen_width // 4
y_position = screen_height // 4

root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_position, y_position))
print('Root ' + str(root.winfo_width()) + 'x' + str(root.winfo_height()))


# # создаем фрейм для canvas и полосы прокрутки
frame = tk.Frame(root, bg='#222222')


frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)
frame.grid(row=0, column=0, sticky="nsew")
frame.pack(expand=True, fill='both')

# создаем canvas и добавляем его на фрейм
canvas = tk.Canvas(frame, bg=canvas_color)
canvas.grid(row=0, column=0, sticky="nsew")

canvas.config(width=frame.winfo_width(), height=frame.winfo_height())


# добавляем полосу прокрутки на фрейм
scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.set(1, 1)

# создаем фрейм в canvas
inner_frame = tk.Frame(canvas, bg=canvas_color, padx=10, pady=10)
canvas.create_window((5, 5), window=inner_frame, anchor="nw")

# Поля ввода логина и пароля
login_label = tk.Label(inner_frame, text='Логин', bg=canvas_color, fg=button_color)
login_label.grid(row=0, column=0)
login_entry = tk.Entry(inner_frame)
login_entry.grid(row=0, column=1)

password_label = tk.Label(inner_frame, text='Пароль', bg=canvas_color, fg=button_color)
password_label.grid(row=1, column=0)
password_entry = tk.Entry(inner_frame, show='*')
password_entry.grid(row=1, column=1)

# Кнопка авторизации
auth_button = tk.Button(inner_frame, text='Войти', command=lambda: vk_auth(login_entry.get(), password_entry.get()), bg=canvas_color, fg=button_color)
auth_button.grid(row=0, column=2, sticky='w')

# Дата поиска
start_date_label = tk.Label(inner_frame, text='Искать до даты', bg=canvas_color, fg=button_color)
start_date_label.grid(row=2, column=0)
start_date_entry = tk.Entry(inner_frame)
start_date_entry.grid(row=2, column=1)

# Поле ввода поиска и кнопка поиска
search_label = tk.Label(inner_frame, text='Поиск', bg=canvas_color, fg=button_color)
search_label.grid(row=3, column=1)
search_entry = tk.Entry(inner_frame)
search_entry.grid(row=3, column=1)

# search_button = tk.Button(inner_frame, text='Поиск', command=lambda: start_search(vk, group_checkboxes, search_entry.get(), start_date_entry.get()), bg=canvas_color, fg=button_color)
search_button = tk.Button(inner_frame, text='Поиск', command=start_search, bg=canvas_color, fg=button_color)
search_button.grid(row=4, column=1)
# search_button1 = tk.Button(inner_frame, text='Поиск не в фоне', command=lambda: search_and_save(vk, group_checkboxes, search_entry.get(), start_date_entry.get()), bg=canvas_color, fg=button_color)
# search_button1.grid(row=5, column=1)
search_button1 = tk.Button(inner_frame, text='Остановить поиск', command=stop_thread, bg=canvas_color, fg=button_color)
search_button1.grid(row=5, column=1)


# поле с информацией о ходе процесса
status = tk.Label(frame, bg=canvas_color, fg='white')
status.grid(row=1, column=0, sticky=tk.S+tk.W)
root.rowconfigure(1, weight=1)

thread = threading.Thread(target=update_label, args=status)
thread.start()

# устанавливаем минимальный размер фрейма с виджетами
inner_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()
