from selenium.webdriver.chrome import webdriver


def make_screen(path_to_file, url):
    # Создаем экземпляр объекта webdriver, используя опции
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    # Загружаем страницу
    driver.get(url)
    # Делаем скриншот страницы и сохраняем его в файл
    screenshot_path = path_to_file
    driver.save_screenshot(screenshot_path)
    # Закрываем браузер
    driver.quit()
