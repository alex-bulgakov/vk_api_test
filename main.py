import csv
import tkinter as tk
import vk_api

def start_search():
    # получаем данные из полей ввода
    login = login_entry.get()
    password = password_entry.get()
    search_text = search_text_entry.get()

    # создаем сессию авторизации
    vk_session = vk_api.VkApi(login, password)

    # пытаемся авторизоваться
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        result_label.config(text='Ошибка авторизации')
        return

    # получаем доступ к API
    vk = vk_session.get_api()

    # получаем список групп, в которых состоит пользователь
    groups = vk.groups.get()

    # создаем список для хранения результатов
    results = []

    # проходимся по каждой группе и ищем комментарии с заданным текстом
    for group_id in groups['items']:
        # получаем список постов в группе
        posts = vk.wall.get(owner_id=-group_id, count=100)

        # проходимся по каждому посту и ищем комментарии с заданным текстом
        for post in posts['items']:
            # получаем список комментариев к посту
            comments = vk.wall.getComments(owner_id=-group_id, post_id=post['id'], count=100)

            # проходимся по каждому комментарию и ищем заданный текст
            for comment in comments['items']:
                if search_text in comment['text']:
                    # добавляем результаты в список
                    profile_url = 'https://vk.com/id{}'.format(comment['from_id'])
                    post_url = 'https://vk.com/wall{}_{}'.format(-group_id, post['id'])
                    results.append((profile_url, post_url))

    # сохраняем результаты в CSV файл
    with open('results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Profile URL', 'Post URL'])
        writer.writerows(results)

    result_label.config(text='Результаты сохранены в файл results.csv')

def on_paste(event):
    search_text_entry.insert(tk.INSERT, window.clipboard_get())

# создаем окно
window = tk.Tk()
window.title('Поиск комментариев')
window.geometry('400x200')

# создаем элементы интерфейса
login_label = tk.Label(window, text='Логин')
login_entry = tk.Entry(window)
login_entry.bind("<Control-v>", on_paste)
password_label = tk.Label(window, text='Пароль')
password_entry = tk.Entry(window, show='*')
password_entry.bind("<Control-v>", on_paste)
search_text_label = tk.Label(window, text='Искомый текст')
search_text_entry = tk.Entry(window)
search_text_entry.bind("<Control-v>", on_paste)
search_button = tk.Button(window, text='Поиск', command=start_search)
result_label = tk.Label(window, text='')

# размещаем элементы интерфейса на окне
login_label.pack()
login_entry.pack()
password_label.pack()
password_entry.pack()
search_text_label.pack()
search_text_entry.pack()
search_button.pack()
result_label.pack()

# запускаем главный цикл окна
window.mainloop()
