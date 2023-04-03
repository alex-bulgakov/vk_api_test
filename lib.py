import datetime
import threading

from read_config import get_config
from serialize_api import get_api

stop = False

def set_stop(set):
    global stop
    stop = set

# Функция получения названия группы по ID
def get_group_name(group_id):
    for key in group_checkboxes:
        if group_id in key:
            return key[0]

# Функция авторизации в VK API


def search_group(group_id, queries, start_date, posts):
    vk = get_api()
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


def start_search(vk):
    # Создаем поток для выполнения функции search_and_save
    search_thread = threading.Thread(target=search_and_save, args=(vk, group_checkboxes, search_entry.get(), start_date_entry.get()))
    search_thread.start()


def get_groups(vk):
    groups = vk.groups.get(extended=1, fields="name")["items"]
    return groups

def stop_thread():
    global stop
    stop = True