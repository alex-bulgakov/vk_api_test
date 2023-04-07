import os
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from status import get_status


def make_screen(path_to_file, url, driver):
    driver.get(url)
    driver.save_screenshot(path_to_file)
    # driver.quit()

#write for loop


def get_css_selector(url):
    digits_and_underscore = ''.join(filter(lambda x: x.isdigit() or x == '_' or x == '=', url))
    parts = digits_and_underscore.split('_')
    num_blocks = list(filter(lambda x: any(char.isdigit() for char in x), parts))
    result = '#post-' + str(num_blocks[0]) + '_' + str(num_blocks[1].split('=')[1])
    return result


# def make_screenshots():
#
#     current_dir = os.getcwd()
#     current_dir = current_dir.replace('\\', '/') + '/results/'
#
#     for folder_name in os.listdir(current_dir):
#         if os.path.isdir(current_dir + folder_name):
#             result_file_path = current_dir + folder_name + '/result.txt'
#             if os.path.exists(result_file_path):
#                 with open(result_file_path, 'r') as result_file:
#                     for line in result_file.readlines()[1:]:
#                         if get_status() == 'Поиск прерван':
#                             driver.quit()
#                             return
#                         parts = line.strip().split(',')
#                         comment = parts[2]
#                         make_screen(current_dir + folder_name + '/' + parts[3] + '.png', comment, '', driver)
#                         make_screen(current_dir + folder_name + '/profile.png', parts[1], '', driver)
#     driver.quit()


def get_webdriver():
    chrome_options = Options()
    chrome_options.headless = True
    # Get the current user's home directory path
    home_dir = os.path.expanduser("~")
    # Concatenate the Chrome user data directory path with the home directory path
    chrome_user_data_dir = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data")
    # Set the Chrome user data directory path as a Chrome option
    chrome_options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    return driver
