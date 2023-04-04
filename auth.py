from vk_api import vk_api
from status import set_status
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
    try:
        vk_session = vk_api.VkApi(login, password)
        vk_session.auth()
        api = vk_session.get_api()
        set_status('Авторизация успешна')
        return api
    except vk_api.AuthError as error_msg:
        set_status(error_msg)


if __name__ == '__main__':
        pass


