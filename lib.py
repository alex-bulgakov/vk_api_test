import msvcrt
import os
import re
import threading
from datetime import datetime

import requests
import vk_api

from screens import make_screen, get_webdriver
from status import set_status

stop = False

driver = None

lock = threading.Lock()
is_searching = False

def set_stop(set):
    global stop
    stop = set

# Функция получения названия группы по ID
def get_group_name(group_id):
    for key in get_groups():
        if group_id in key:
            return key[0]

# Функция авторизации в VK API


def search_group(vk, group_id, queries, start_date, posts):
    result = []
    try:
        set_status('Ищем в группе - ' + str(get_group_name(group_id)))
    except:
        pass
    offset = 0
    flag = True
    is_pinned = False

    while flag:
        if stop:
            return
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
                # ищем в посте
                post_id = post["id"]
                if post['comments']['count'] > 0:
                    comments = vk.wall.getComments(owner_id=-group_id, post_id=post_id, count=100, sort='desc',
                                                   preview_length=0, extended=1)
                    for comment in comments['items']:
                        # ищем в комментах к посту
                        comment_text = re.sub(r"[^a-zA-ZА-Яа-я0-9]+", " ", comment['text']).lower().strip()
                        comment_text_words = comment_text.split()

                        for query in queries:
                            query_text = query.lower().strip()
                            if stop:
                                return []
                            if query_text in comment_text_words:
                                set_status('Нашли в комменте - ' + comment_text[0:30])
                                result_line = {
                                    'group_id': group_id,
                                    'post_id': post_id,
                                    'id': comment['id'],
                                    'from_id': comment['from_id'],
                                    'text': comment['text']
                                }
                                if not (result_line in result):
                                    set_status('Записываем коммент в файлы')
                                    save_comment(result_line)
            else:
                flag = False
                break
        offset += 100
        if offset >= response["count"]:
            break

    return result

def search_word(key_word, string):
    words = string.split()

    for w in words:
        if w.stripe() == key_word:
            return True
        else:
            return False

def search_and_save(vk, group_checkboxes, query, start_date):
    global driver
    driver = get_webdriver()
    global is_searching
    with lock:
        is_searching = True
    if query == '':
        set_status('Не задана строка поиска')
        return

    global stop
    set_status('Начинаем поиск')
    if start_date == '':
        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day)
    else:
        start_date = datetime.strptime(start_date, '%d.%m.%Y')

    queries = query.split('\n')
    selected_group_ids = [checkbox[1] for checkbox in group_checkboxes if checkbox[2].get()]
    posts = []

    for group_id in selected_group_ids:
        if stop:
            set_status('Поиск прерван')
            stop = False
            return
        else:
            search_group(vk, group_id, queries, start_date, posts)

    driver.quit()


    # file_name = set_dir('./results', 'result.txt')

    # for post in posts:
    #     save_comment(post)
    #     if stop:
    #         set_status('Поиск прерван')
    #         stop = False
    #         return
    #
    # set_status('Делаем скриншоты')
    # make_screenshots()
    set_status('Готово')
    with lock:
        is_searching = False


def save_comment(post):

    post_url = f"https://vk.com/wall-{post['group_id']}_{post['post_id']}"
    user_url = f"https://vk.com/id{post['from_id']}"
    comment_url = f"https://vk.com/wall-{post['group_id']}_{post['post_id']}?reply={post['id']}"
    post_str = re.sub(r"[^a-zA-ZА-Яа-я0-9]+", " ", post['text'])

    set_status('Записываем коммент - ' + post_str[0: 50])

    path = './results/' + str(post['from_id']) + '/'
    file_name = path + 'result.txt'
    result_line = (post_url + ',' + user_url + ',' + comment_url + ',' + post_str + '\n')

    if not os.path.exists(path):
        os.makedirs(path)
    try:
        with open(file_name, mode='r', encoding='cp1251', newline='') as f:
            file_lines = f.readlines()
    except FileNotFoundError:
        file_lines = []
        print('Файл еще не создан, создаем')

    with open(file_name, mode='w', encoding='cp1251', newline='') as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, os.path.getsize(file_name))
        if not (result_line in file_lines):
            f.write(result_line)
    save_html(comment_url, './results/' + str(post['from_id']) + '/' + post_str[0:50].replace(' ', '_') + '.html')
    set_status('Делаем скрин коммента - ' + post_str[0:50])
    make_screen('./results/' + str(post['from_id']) + '/' + post_str[0:30].strip() + '.png', comment_url, driver)
    make_screen('./results/' + str(post['from_id']) + '/profile.png', user_url, driver)


def start_search(vk, groups, search, start):
    # Создаем поток для выполнения функции search_and_save
    search_thread = threading.Thread(target=search_and_save, args=(vk, groups, search, start))
    search_thread.start()
    # search_and_save(vk, groups, search, start)


def get_groups(vk):
    groups = vk.groups.get(extended=1, fields="name")["items"]
    return groups

def stop_thread():
    global stop
    stop = True


def set_dir(dirname, filename):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return os.path.join(dirname, filename)


def save_html(url, path_to_file):
    token = ''
    with open('access_token', 'r') as file:
        token = file.read().strip()
    vk_session = vk_api.VkApi(token=token)

    # Создаем сессию для сохранения авторизации
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    # Применяем сохраненную сессию авторизации к сессии сохранения страницы
    session.cookies.update(dict(vk_session.http.cookies))

    # Получаем HTML страницу по ссылке и сохраняем ее в файл
    response = session.get(url)

    with open(path_to_file, 'w', encoding='utf-8') as file:
        file.write(response.text)
