import csv
import vk_api

# устанавливаем логин и пароль для входа
login = ''
password = ''

# создаем сессию авторизации
vk_session = vk_api.VkApi(login, password)

# пытаемся авторизоваться
try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)


# получаем доступ к API
vk = vk_session.get_api()

# получаем список групп, в которых состоит пользователь
groups = vk.groups.get()

# задаем текст, который будем искать в комментариях
search_text = 'Джон'

# создаем список для хранения результатов
results = []

# проходимся по каждой группе и ищем комментарии с заданным текстом
for group_id in groups['items']:
    # получаем список постов в группе
    print('Ищем в группе ' + str(group_id))
    posts = vk.wall.get(owner_id=-group_id, count=5)

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
                print('Найден текст - ' + search_text + ' в комментарии по ссылке ' + post_url)

# сохраняем результаты в CSV файл
with open('results.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Profile URL', 'Post URL'])
    writer.writerows(results)

print('Результаты сохранены в файл results.csv')
