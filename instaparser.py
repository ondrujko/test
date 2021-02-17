import pickle
import random
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from subprocess import call
import config

opt_list = ['disable-3d-apis',
            'disable-audio',
            'disable-bookmark-autocomplete-provider',
            'disable-bundled-ppapi-flash',
            'disable-cloud-policy-service',
            'disable-desktop-notifications',
            'disable-extensions',
            'disable-flash-3d',
            'disable-flash-stage3d',
            'disable-full-history-sync',
            'disable-gpu',
            'disable-improved-download-protection',
            'disable-java',
            'disable-media-history',
            'disable-media-source',
            'disable-ntp-other-sessions-menu',
            'disable-pepper-3d',
            'disable-plugins',
            'disable-popup-blocking',
            'disable-print-preview',
            'disable-restore-background-contents',
            'disable-scripted-print-throttling',
            'disable-smooth-scrolling',
            'disable-speech-input',
            'disable-web-media-player-ms',
            'disable-web-security',
            'disable-webaudio',
            'disable-webgl',
            'disable-xss-auditor']


def load_cookies(driver, location, url=None):
    cookies = pickle.load(open(location, "rb"))
    driver.delete_all_cookies()
    # have to be on a page before you can add any cookies, any page - does not matter which
    driver.get("https://instagram.com/therock/feed/" if url is None else url)
    for cookie in cookies:
        if isinstance(cookie.get('expiry'), float):  # Checks if the instance expiry a float
            cookie['expiry'] = int(cookie['expiry'])  # it converts expiry cookie to a int
        driver.add_cookie(cookie)


class Scrap:
    # Инициализация класса
    def __init__(self):
        self.kill_edge = 1000
        self.polling = True
        self.y = random.randint(500, 1000)
        self.count = 100
        self.number_of_posts = 100
        self.last_l = 0
        self.counter_repeat = 0
        self.posts = []
        self.marks = []
        self.user = None
        self.driver = None
        self.usernames = None
        self.process_busy = False
        self.d = {}

    # Разделить юзернеймы
    def split_usernames(self, text):  # split text to list
        text = text.replace(' ', '').replace('@', '')  # delete useless chars
        self.usernames = text.split(',')  # split str to list
        self.usernames = list(set(self.usernames))
        return self.usernames

    # Главная функция
    def scrap(self, usernames, count, kill_edge=1000):
        self.count = count
        self.process_busy = True
        self.kill_edge = kill_edge
        call("process_kill.bat")

        # Создать драйвер
        def launch_driver(headless=True):  # Start ChromeDriver
            # options = webdriver.ChromeOptions()
            # mobile_emulation = {"deviceName": "iPhone X"}  # name of mobile device
            # options.add_experimental_option("mobileEmulation", mobile_emulation)  # mobile emulation
            #
            # for opt in opt_list:
            #     options.add_argument(opt)
            # if headless:
            #     options.add_argument('--headless')
            # driver = webdriver.Chrome(options=options)
            # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {  # This is help bypass protection maybe
            #     "source": """
            #           const newProto = navigator.__proto__
            #           delete newProto.webdriver
            #           navigator.__proto__ = newProto
            #           """
            # })

            # driver = webdriver.Firefox(firefox_binary=binary, desired_capabilities=capabilities)
            user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
            options = FirefoxOptions()
            options.add_argument("--headless")
            profile = webdriver.FirefoxProfile()
            profile.set_preference("general.useragent.override", user_agent)
            driver = webdriver.Firefox(profile, options=options)
            driver.set_window_size(360, 640)
            driver.set_page_load_timeout(120)
            load_cookies(driver, config.cookies_path)
            return driver

        # Найти отметки людей на фото
        def find_marks():  # Func for search marks
            '''Функция find_marks ищет все отметки на фотографиях, что видит'''
            try:
                marks_not_processed = self.driver.find_elements_by_class_name('JYWcJ ')  # Find all marks
                for mark in marks_not_processed:
                    atr = mark.get_attribute('href')  # Get url from mark
                    self.marks.append(atr)  # Append url in list
                    self.marks = list(set(self.marks))  # Uniqueize list
            except Exception as e:
                print(f'Не удалось найти элемент\nERROR: {e}')

        # Поиск логинов в описании
        def search_in_description():
            try:
                descriptions = self.driver.find_elements_by_class_name('notranslate')  # Находит все описания
                for description in descriptions:
                    try:
                        text = description.text
                        usernames_in_description = re.findall(r'@[\w\.|_-]+', text)
                        if usernames_in_description:
                            for username_in_description in usernames_in_description:
                                username_in_description = username_in_description.replace(' ', '').replace('@', '')
                                self.marks.append(username_in_description)
                                self.marks = list(set(self.marks))

                    except:
                        pass
                self.marks = list(set(self.marks))
            except:
                pass

        # Счетчик постов
        def counter_of_posts():
            '''Данная функция ищет все посты на странице, которые видит'''
            materials = []
            try:
                material_v = self.driver.find_elements_by_class_name('fXIG0')
                materials.append(material_v)
            except:
                pass
            try:
                material_f = self.driver.find_elements_by_class_name('_9AhH0')
                materials.append(material_f)
            except:
                pass
            for material in materials:
                for m in material:
                    self.posts.append(m)  # Добавить посты в список
                    self.posts = list(set(self.posts))  # Уникализирует список

        # Сохранить список в TXT
        def save_in_txt(lst):
            '''Сохраняет значения списка в txt файл'''
            try:
                with open("result_parser.txt", "w") as file:
                    for elem in lst:
                        if elem is not None:
                            try:
                                elem = elem.replace('https://www.instagram.com/', '').replace('/', '')
                            except Exception as e:
                                print(str(e), 'Не удалось удалить рудименты')
                            try:
                                file.write('{}\n'.format(elem))
                            except:
                                print('Не удалось записать')

            except Exception as e:
                print(e)

        # Скролл вниз
        def scroll_down():  # Скролл вниз
            # self.driver.execute_script("window.scrollTo(0, " + str(self.y) + ")")
            # self.y += random.randint(100, 250)
            action = ActionChains(self.driver)
            action.key_down(Keys.PAGE_DOWN).perform()
            action.key_up(Keys.PAGE_DOWN).perform()

        def scroll_down_fast():
            self.driver.execute_script("window.scrollTo(0, " + str(self.y) + ")")
            self.y += random.randint(100, 250)

        # Количество постов на странице
        def num_of_posts():
            try:  # How many posts in this account
                self.number_of_posts = self.driver.find_element_by_class_name('g47SY').text.replace(' ', '')
            except:
                try:
                    self.number_of_posts = self.driver.find_element_by_class_name('g47SY lOXF2').text.replace(' ', '')
                except:
                    pass

        for self.user in usernames:
            self.driver = launch_driver(headless=False)
            self.driver.get(f'https://instagram.com/{self.user}/feed/')
            time.sleep(5)
            num_of_posts()

            # the loop will stop when the action is executed
            while len(self.posts) <= int(self.number_of_posts) - int(self.number_of_posts) * 0.2 and len(
                    self.marks) <= int(self.count) and self.polling is True:
                find_marks()
                search_in_description()
                counter_of_posts()
                scroll_down()
                print(len(self.posts))
                if len(self.posts) == self.last_l:
                    self.counter_repeat = self.counter_repeat + 1
                    print(self.counter_repeat)
                    if self.counter_repeat >= self.kill_edge:
                        break
                else:
                    self.counter_repeat = 0
                    self.last_l = len(self.posts)
            try:
                self.process_busy = False
                self.driver.quit()
            except:
                self.process_busy = False

        try:
            self.driver.quit()
        except:
            pass

    def state(self):  # Возвращает словарь с инфой о текущих состояниях
        self.d = {'user', 'marks', 'posts', 'number of posts', 'count'}
        self.d['user'] = self.user
        self.d['marks'] = len(self.marks)
        self.d['posts'] = len(self.posts)
        self.d['number of posts'] = self.number_of_posts
        self.d['count'] = self.count
        return self.d

    def close_all_drivers(self):
        try:
            self.driver.quit()
            self.polling = False
        except:
            print('Драйвер не активен')
            self.polling = False

    def saved(self, lst):
        try:
            with open("result_parser.txt", "w") as file:
                for elem in lst:
                    if elem is not None:
                        try:
                            elem = elem.replace('https://www.instagram.com/', '').replace('/', '')
                        except Exception as e:
                            print(str(e), 'Не удалось удалить рудименты')
                        try:
                            file.write('{}\n'.format(elem))
                        except:
                            print('Не удалось записать')
                return True
        except Exception as e:
            print(e)
            return False
