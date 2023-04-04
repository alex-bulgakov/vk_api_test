from auth import vk_auth
from lib import get_groups
from status import set_status
from window import draw_window
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


set_status('Текущий статус')
draw_window()


# path_to_file = 'd/Python/pythonProject/results/704849317/'
#
# # Создаем экземпляр объекта webdriver, используя опции
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=options)
#
# # Задаем ссылку на страницу, которую нужно сделать скриншотом
# url = 'https://vk.com/wall-150004099_130801'
#
# # Загружаем страницу
# driver.get(url)
#
# # Делаем скриншот страницы и сохраняем его в файл
# screenshot_path = 'screenshot.png'
# driver.save_screenshot(screenshot_path)
#
# # Закрываем браузер
# driver.quit()