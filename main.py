import csv
import tkinter as tk
import vk_api
from datetime import datetime, timedelta
import json

# Функция авторизации в VK API

vk = None
group_checkboxes = []

def vk_auth(login, password):
    try:
        global vk, group_checkboxes
        # vk_session = vk_api.VkApi(login, password)
        vk_session = vk_api.VkApi('+79182993975', 'fgkjfl84')
        vk_session.auth()
        vk = vk_session.get_api()
        groups = vk.groups.get(extended=1, fields="name")["items"]
        for group in groups:
            group_checkboxes.append((group["name"], group["id"], tk.BooleanVar()))
        for checkbox in group_checkboxes:
            tk.Checkbutton(root, text=checkbox[0], variable=checkbox[2]).pack()
    except vk_api.AuthError as error_msg:
        print(error_msg)

# Функция поиска и сохранения результата в CSV файл
def search_and_save(vk, group_checkboxes, query, start_date):
    selected_group_ids = [checkbox[1] for checkbox in group_checkboxes if checkbox[2].get()]
    posts = []
    for group_id in selected_group_ids:
        offset = 0
        flag = True
        while flag:
            response = vk.wall.get(owner_id=-group_id, count=100, offset=offset, extended=1)
            items = response["items"]
            for post in items:
                post_date = datetime.fromtimestamp(post["date"])
                if post_date >= start_date:
                    post_id = post["id"]
                    if post['comments']['count'] > 0:
                        comments = vk.wall.getComments(owner_id=-group_id, post_id=post_id, count=100, sort='desc',
                                                       preview_length=0, extended=1)
                        for comment in comments['items']:
                            if query in comment['text']:
                                posts.append({
                                    'post_id': post_id,
                                    'id': comment['id'],
                                    'from_id': comment['from_id'],
                                    'text': comment['text']
                                })
                    else:
                        break
                else:
                    flag = False
                    break
            offset += 100
            if offset >= response["count"]:
                break

    with open('search_results.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Post URL', 'User URL', 'Comment Text'])
        for post in posts:
            writer.writerow([f"https://vk.com/wall-{group_id}_{post['post_id']}",
                             f"https://vk.com/id{post['from_id']}",
                             post['text']])



def check_post_date(post):
    post_date = datetime.fromtimestamp(post["date"])
    if post_date >= start_date and post_date <= end_date:
        post_id = post["id"]
        if post['comments']['count'] > 0:
            print('Пост ' + post['text'])
            comments = vk.wall.getComments(owner_id=-group_id, post_id=post_id, count=100, sort='desc',
                                           preview_length=0, extended=1)
            comments = json.dumps(comments, ensure_ascii=False)
            comments = json.loads(comments)
            posts.extend([comment['thread'] for comment in comments['items']])


# Создание графического интерфейса
root = tk.Tk()
root.title('VK Search')
root.geometry('400x400')

# Поля ввода логина и пароля
login_label = tk.Label(root, text='Login')
login_label.pack()
login_entry = tk.Entry(root)
login_entry.pack()

password_label = tk.Label(root, text='Password')
password_label.pack()
password_entry = tk.Entry(root, show='*')
password_entry.pack()

# Кнопка авторизации
auth_button = tk.Button(root, text='Authorize', command=lambda: vk_auth(login_entry.get(), password_entry.get()))
auth_button.pack()

# Поле ввода поиска и кнопка поиска
search_label = tk.Label(root, text='Search')
search_label.pack()
search_entry = tk.Entry(root)
search_entry.pack()

start_date_label = tk.Label(root, text='Date')
start_date_label.pack()
start_date_entry = tk.Entry(root)
start_date_entry.pack()

# end_date_label = tk.Label(root, text='End Date')
# end_date_label.pack()
# end_date_entry = tk.Entry(root)
# end_date_entry.pack()

# search_button = tk.Button(root, text='Search', command=lambda: search_and_save(vk, group_checkboxes, search_entry.get(), datetime.strptime(start_date_entry.get(), '%d.%m.%Y'), datetime.strptime(end_date_entry.get(), '%d.%m.%Y')))
search_button = tk.Button(root, text='Search', command=lambda: search_and_save(vk, group_checkboxes, 'что', datetime.strptime('01.03.2023', '%d.%m.%Y')))
search_button.pack()

root.mainloop()
