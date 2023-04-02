import csv
import os
import sys
import threading
import tkinter as tk
import vk_api
from datetime import datetime, timedelta
import json

# Функция авторизации в VK API

debug_flag = False


def debug_msg(msg):
    if debug_flag:
        print(msg)


vk = None
group_checkboxes = []


def vk_auth(login, password):
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
            tk.Checkbutton(inner_frame, text=checkbox[0], variable=checkbox[2], bg=canvas_color, fg=button_color).grid(row=check_row, column=2, sticky='w', padx=5)
            check_row += 1
        debug_msg('Авторизация успешна')
    except vk_api.AuthError as error_msg:
        print(error_msg)


def search_group(vk, group_id, queries, start_date, posts):
    offset = 0
    flag = True
    is_pinned = False
    response = vk.wall.get(owner_id=-group_id, count=100, offset=offset, extended=1)
    items = response["items"]

    while flag:
        for post in items:
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
                            if query.strip() in comment['text']:
                                posts.append({
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

    return posts


def search_and_save(vk, group_checkboxes, query, start_date):
    if start_date == '':
        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day)
    else:
        start_date = datetime.strptime(start_date, '%d.%m.%Y')

    queries = query.split(',')
    selected_group_ids = [checkbox[1] for checkbox in group_checkboxes if checkbox[2].get()]
    posts = []

    # # Создание потоков для каждой выбранной группы
    # threads = []
    # for group_id in selected_group_ids:
    #     thread = threading.Thread(target=search_group, args=(vk, group_id, queries, start_date, posts))
    #     threads.append(thread)
    #     thread.start()
    #
    # # Ожидание завершения всех потоков
    # for thread in threads:
    #     thread.join()

    for group_id in selected_group_ids:
        posts += search_group(vk, group_id, queries, start_date, posts)

    with open('search_results.csv', mode='w', encoding='utf-8', newline='') as file:

        writer = csv.writer(file)
        writer.writerow(['Post URL', 'User URL', 'Comment Text'])
        for post in posts:
            writer.writerow([f"https://vk.com/wall-{post['group_id']}_{post['post_id']}",
                             f"https://vk.com/id{post['from_id']}",
                             post['text']])


def check_post_date(post):
    post_date = datetime.fromtimestamp(post["date"])
    if post_date >= start_date and post_date <= end_date:
        post_id = post["id"]
        if post['comments']['count'] > 0:
            comments = vk.wall.getComments(owner_id=-group_id, post_id=post_id, count=100, sort='desc',
                                           preview_length=0, extended=1)
            comments = json.dumps(comments, ensure_ascii=False)
            comments = json.loads(comments)
            posts.extend([comment['thread'] for comment in comments['items']])


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

start_date_label = tk.Label(inner_frame, text='Искать до даты', bg=canvas_color, fg=button_color)
start_date_label.grid(row=2, column=0)
start_date_entry = tk.Entry(inner_frame)
start_date_entry.grid(row=2, column=1)

# Поле ввода поиска и кнопка поиска
search_label = tk.Label(inner_frame, text='Поиск', bg=canvas_color, fg=button_color)
search_label.grid(row=3, column=1)
search_entry = tk.Entry(inner_frame)
search_entry.grid(row=3, column=1)

search_button = tk.Button(inner_frame, text='Поиск', command=lambda: search_and_save(vk, group_checkboxes, search_entry.get(), start_date_entry.get()), bg=canvas_color, fg=button_color)
search_button.grid(row=4, column=1)

# устанавливаем минимальный размер фрейма с виджетами
inner_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()
