import pickle
import pprint
import time
from selenium import webdriver

URL = 'https://www.instagram.com/kazachenko_s.9/'


def save_cookies(driver, location):
    pickle.dump(driver.get_cookies(), open(location, "wb"))


def load_cookies(driver, location, url=None):
    cookies = pickle.load(open(location, "rb"))
    # have to be on a page before you can add any cookies, any page - does not matter which
    driver.get(URL if url is None else url)
    for cookie in cookies:
        if isinstance(cookie.get('expiry'), float):  # Checks if the instance expiry a float
            cookie['expiry'] = int(cookie['expiry'])  # it converts expiry cookie to a int
        driver.add_cookie(cookie)


def delete_cookies(driver, domains=None):
    if domains is not None:
        cookies = driver.get_cookies()
        original_len = len(cookies)
        for cookie in cookies:
            if str(cookie["domain"]) in domains:
                cookies.remove(cookie)
        if len(cookies) < original_len:  # if cookies changed, we will update them
            # deleting everything and adding the modified cookie object
            driver.delete_all_cookies()
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        driver.delete_all_cookies()


user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", user_agent)
driver = webdriver.Firefox(profile)
driver.set_window_size(360, 640)
# driver = webdriver.Firefox()
driver.set_page_load_timeout(120)

# Path where you want to save/load cookies to/from aka C:\my\fav\directory\cookies.txt
cookies_location = "insta.txt"

# Initial load of the domain that we want to save cookies for
# chrome = webdriver.Chrome()
# chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#     "source": """
#           const newProto = navigator.__proto__
#           delete newProto.webdriver
#           navigator.__proto__ = newProto
#           """
# })
driver.get(URL)
input('ENTER')
save_cookies(driver, cookies_location)
driver.quit()

# Load of the page you cant access without cookies, this one will go through
# chrome = webdriver.Chrome()
# chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#     "source": """
#           const newProto = navigator.__proto__
#           delete newProto.webdriver
#           navigator.__proto__ = newProto
#           """
# })
user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", user_agent)
driver1 = webdriver.Firefox(profile)
driver1.set_window_size(360, 640)
driver1.set_page_load_timeout(120)

load_cookies(driver1, cookies_location, URL)
driver1.get(URL)
