import csv
import os
import sys
import threading
import tkinter as tk
import vk_api
from datetime import datetime, timedelta
import json

# Функция авторизации в VK API

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
        for group in groups:
            group_checkboxes.append((group["name"], group["id"], tk.BooleanVar()))
        for checkbox in group_checkboxes:
            tk.Checkbutton(root, text=checkbox[0], variable=checkbox[2]).pack()
        print('Авторизация успешна')
    except vk_api.AuthError as error_msg:
        print(error_msg)


# def search_group(vk, group_id, queries, start_date, posts):
#     offset = 0
#     flag = True
#     is_pinned = False
#     response = vk.wall.get(owner_id=-group_id, count=100, offset=offset, extended=1)
#     items = response["items"]
#
#     while flag:
#         for post in items:
#             post_date = datetime.fromtimestamp(post["date"])
#
#             is_pinned = False
#             try:
#                 is_pinned = post['is_pinned'] == 1
#             except:
#                 pass
#
#             if post_date >= start_date or is_pinned:
#                 post_id = post["id"]
#                 if post['comments']['count'] > 0:
#                     comments = vk.wall.getComments(owner_id=-group_id, post_id=post_id, count=100, sort='desc',
#                                                    preview_length=0, extended=1)
#                     for comment in comments['items']:
#                         for query in queries:
#                             if query.strip() in comment['text']:
#                                 posts.append({
#                                     'group_id' : group_id,
#                                     'post_id': post_id,
#                                     'id': comment['id'],
#                                     'from_id': comment['from_id'],
#                                     'text': comment['text']
#                                 })
#
#             else:
#                 flag = False
#                 break
#         offset += 100
#         if offset >= response["count"]:
#             break
#
#         return posts


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
root = tk.Tk()
root.title('VK Поиск')
root.geometry('400x400')

# Поля ввода логина и пароля
login_label = tk.Label(root, text='Логин')
login_label.pack()
login_entry = tk.Entry(root)
login_entry.pack()

password_label = tk.Label(root, text='Пароль')
password_label.pack()
password_entry = tk.Entry(root, show='*')
password_entry.pack()

# Кнопка авторизации
auth_button = tk.Button(root, text='Войти', command=lambda: vk_auth(login_entry.get(), password_entry.get()))
auth_button.pack()

# Поле ввода поиска и кнопка поиска
search_label = tk.Label(root, text='Поиск')
search_label.pack()
search_entry = tk.Entry(root)
search_entry.pack()

start_date_label = tk.Label(root, text='Искать до даты')
start_date_label.pack()
start_date_entry = tk.Entry(root)
start_date_entry.pack()



search_button = tk.Button(root, text='Поиск', command=lambda: search_and_save(vk, group_checkboxes, search_entry.get(), start_date_entry.get()))
search_button.pack()

root.mainloop()
