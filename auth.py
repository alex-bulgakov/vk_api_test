from vk_api import vk_api

from read_config import get_config

vk = None
is_authorize = False


def vk_auth(login, password):
    # текущая папка
    if login == '' or password == '':
        config = get_config()
        if len(config) >= 1:
            login = config[0]
            password = config[1]
        return get_api(login, password)
    else:
        return get_api(login, password)


def get_api(login,password):
    result = {'result': None, 'status': ''}
    try:
        vk_session = vk_api.VkApi(login, password)
        vk_session.auth()
        api = vk_session.get_api()
        result['result'] = api
        result['status'] = 'Авторизация успешна'
        return result
    except vk_api.AuthError as error_msg:
        result['status'] = error_msg
        return result


if __name__ == '__main__':
        pass


