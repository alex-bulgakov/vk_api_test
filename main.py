import tkinter as tk
import vk_api
from datetime import datetime, timedelta

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

# Функция поиска
def search(vk, group_checkboxes, query, start_date, end_date):
    selected_group_ids = [checkbox[1] for checkbox in group_checkboxes if checkbox[2].get()]
    posts = []
    for group_id in selected_group_ids:
        posts.extend(vk.wall.search(owner_id=-group_id, query=query, count=100, start_time=start_date.timestamp(), end_time=end_date.timestamp())["items"])
    for post in posts:
        print(post["text"])

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

start_date_label = tk.Label(root, text='Start Date')
start_date_label.pack()
start_date_entry = tk.Entry(root)
start_date_entry.pack()

end_date_label = tk.Label(root, text='End Date')
end_date_label.pack()
end_date_entry = tk.Entry(root)
end_date_entry.pack()

search_button = tk.Button(root, text='Search', command=lambda: search(vk, group_checkboxes, search_entry.get(), datetime.strptime(start_date_entry.get(), '%d.%m.%Y'), datetime.strptime(end_date_entry.get(), '%d.%m.%Y')))
search_button.pack()

root.mainloop()
