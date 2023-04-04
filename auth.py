import pickle
import tkinter as tk
import webbrowser

from vk_api import vk_api
from vk_api.exceptions import Captcha as capcha_e

from read_config import get_config
from status import set_status

vk = None
is_authorize = False
captcha_photo = None


def vk_auth(login, password):
    # текущая папка
    if login == '' or password == '':
        config = get_config()
        if len(config) >= 1:
            login = config[0]
            password = config[1]
    api = get_api(login, password)
    return api


def get_api(login, password):
    vk_session = vk_api.VkApi(login, password, captcha_handler=draw_captcha)
    api = vk_session.get_api()
    try:
        vk_session.auth()

        with open('access_token', 'w') as file:
            file.write(vk_session.token['access_token'])
        set_status('Авторизация успешна')
        return api
    except capcha_e as e:
        set_status(e)


def draw_captcha(captcha):

    root = tk.Tk()
    root.title('VK капча')

    # Определяем размер экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Вычисляем размер окна
    window_width = screen_width // 4
    window_height = screen_height // 4

    # Вычисляем координаты окна, чтобы оно отображалось по центру экрана
    x_position = screen_width // 4
    y_position = screen_height // 4

    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_position, y_position))
    print('Root ' + str(root.winfo_width()) + 'x' + str(root.winfo_height()))

    webbrowser.open(captcha.get_url())

    def push_button(captcha_result):
        captcha.try_again(captcha_result)
        root.destroy()

    # добавляем на окно кнопку отправки капчи
    button = tk.Button(root, text='Отправить капчу', command=lambda: push_button(captcha_entry.get()))
    button.pack()

    captcha_entry = tk.Entry(root)
    captcha_entry.pack()

    # ожидаем закрытия окна
    root.wait_window(root)

    # возвращаем введенное пользователем значение
    captcha.try_again(captcha_entry.get())

if __name__ == '__main__':
    vk = vk_auth('', '')

