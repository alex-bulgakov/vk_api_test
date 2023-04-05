from selenium.webdriver.chrome import webdriver


def make_screen(path_to_file, url):
    # ������� ��������� ������� webdriver, ��������� �����
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    # ��������� ��������
    driver.get(url)
    # ������ �������� �������� � ��������� ��� � ����
    screenshot_path = path_to_file
    driver.save_screenshot(screenshot_path)
    # ��������� �������
    driver.quit()
