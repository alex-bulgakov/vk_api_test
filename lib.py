import csv
import os
import re
from datetime import datetime
import msvcrt
import threading
import requests
import vk_api
from read_config import get_config
from screens import make_screenshots
from status import set_status

stop = False

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
                        comment_text = re.sub(r"[^a-zA-ZА-Яа-я0-9]+", " ", comment['text']).lower().strip()

                        for query in queries:
                            query_text = query.lower().strip()
                            if stop:
                                return []
                            if query_text in comment_text:
                                set_status('Нашли в комменте - ' + comment_text[0:30])
                                result.append({
                                    'group_id': group_id,
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
    global is_searching
    with lock:
        is_searching = True
    if query == '':
        set_status('Не задана строка поиска')
        return
    config = get_config()
    file_name = 'result.csv'
    try:
        file_name = config[2]
    except:
        pass

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
        else:
            posts += search_group(vk, group_id, queries, start_date, posts)

    set_status('Записываем результаты в файлы')
    file_name = set_dir('./results', 'result.txt')


    for post in posts:
        post_url = f"https://vk.com/wall-{post['group_id']}_{post['post_id']}"
        user_url = f"https://vk.com/id{post['from_id']}"
        comment_url = f"https://vk.com/wall-{post['group_id']}_{post['post_id']}?reply={post['id']}"
        post_str = re.sub(r"[^a-zA-ZА-Яа-я0-9]+", " ", post['text'])

        file_name = set_dir('./results/' + str(post['from_id']), 'result.txt')
        with open(file_name, mode='w', encoding='cp1251', newline='') as f:
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, os.path.getsize(file_name))
            writer = csv.writer(f)
            writer.writerow(['Post URL', 'User URL', 'Comment URL', 'Comment Text'])
            writer.writerow([post_url, user_url, comment_url, post_str])
            if stop:
                set_status('Поиск прерван')
                stop = False
                return
        save_html(comment_url, './results/' + str(post['from_id']) + '/' + post_str[0:50].replace(' ', '_') + '.html')

    set_status('Делаем скриншоты')
    make_screenshots()
    set_status('Готово')
    with lock:
        is_searching = False


def start_search(vk, groups, search, start):
    # Создаем поток для выполнения функции search_and_save
    search_thread = threading.Thread(target=search_and_save, args=(vk, groups, search, start))
    search_thread.start()


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
