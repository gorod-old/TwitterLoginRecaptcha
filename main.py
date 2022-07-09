import os
import sys
from random import choice, uniform
from subprocess import CREATE_NO_WINDOW
from time import sleep

from dotenv import load_dotenv
from colorama import Fore, Style
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from MessagePack import print_exception_msg, print_info_msg
from ServiceApiPack import solve_recaptcha_guru
from WinSoundPack import beep
from patch import webdriver_folder_name, download_latest_chromedriver

HEADLESS = False
USER_AGENT = True
PROXY = True
DELAY_TIME = 3
ua_list = None
p_list = None


def get_user_agents_list():
    global ua_list
    ua_list = open('text_files/user-agents.txt').read().strip().split('\n')
    for ua in ua_list:
        if len(ua) == 0:
            ua_list.remove(ua)
    print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' user agent list count: ' + Fore.CYAN + f'{len(ua_list)}')
    return ua_list


def get_proxies_list():
    global p_list
    p_list = open('text_files/proxies.txt').read().strip().split('\n')
    for p in p_list:
        if len(p) == 0:
            p_list.remove(p)
    print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' proxies list count: ' + Fore.CYAN + f'{len(p_list)}')
    return p_list


def get_user_agent():
    ua_list_ = ua_list if ua_list else get_user_agents_list()
    return choice(ua_list_) if len(ua_list_) > 0 else None


def get_proxy():
    p_list_ = p_list if p_list else get_proxies_list()
    return choice(p_list_) if len(p_list_) > 0 else None


def delay(driver):
    driver.implicitly_wait(DELAY_TIME)


def waiting_for_element(driver, element: tuple, wait_time: int):
    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located(
            element))
    except Exception as e:
        print_exception_msg('element timeout exceeded')


def send_keys(driver, element: WebElement, key: str):
    action = webdriver.ActionChains(driver)
    action.send_keys_to_element(element, key).pause(uniform(.1, .5)) \
        .send_keys_to_element(element, Keys.ENTER).perform()


def get_driver():
    if not os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe'):
        sys.exit(
            "[ERR] Please make sure Chrome browser is installed "
            "(path is exists: C:/Program Files/Google/Chrome/Application/chrome.exe) "
            "and updated and rerun program"
        )
    # download latest chromedriver, please ensure that your chrome is up to date
    driver = None
    while True:
        try:
            # create chrome driver
            path_to_chromedriver = os.path.normpath(
                os.path.join(os.getcwd(), webdriver_folder_name, "chromedriver.exe")
            )
            service = Service(path_to_chromedriver)
            service.creationflags = CREATE_NO_WINDOW
            options = webdriver.ChromeOptions()
            options.headless = HEADLESS
            if USER_AGENT:
                u_agent = get_user_agent()
                print_info_msg(f" user-agent: {u_agent}")
                if u_agent:
                    options.add_argument('user-agent=' + u_agent)
            if PROXY:
                prx = get_proxy()
                print_info_msg(f'driver proxy: {prx}')
                if prx:
                    options.add_argument('--proxy-server=' + prx)
            driver = webdriver.Chrome(service=service, options=options)
            delay(driver)
            return driver
        except Exception as e:
            # patch chromedriver if not available or outdated
            if driver is None:
                is_patched = download_latest_chromedriver()
            else:
                is_patched = download_latest_chromedriver(
                    driver.capabilities["version"]
                )
            if not is_patched:
                sys.exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder "
                    "according to your chrome version: https://chromedriver.chromium.org/downloads"
                )


def check_element(driver, element_data, el_max_wait_time: float = 10):
    """check if an element exists on the page"""
    element = element_data[0]
    text = element_data[1]
    try:
        wait = WebDriverWait(driver, el_max_wait_time)
        wait.until(EC.presence_of_element_located(element))
        if text and text not in driver.find_element(*element).text:
            return False
    except Exception as e:
        print_exception_msg(str(e))
        return False
    return True


def submit_bt_click(driver, submit):
    try:
        driver.switch_to.default_content()
        sleep(uniform(1.0, 5.0))
        element = driver.find_element(*submit)
        webdriver.ActionChains(driver).move_to_element(element).click().perform()
    except Exception as e:
        print_exception_msg(f"recaptcha submit not find, {str(e)}")


def login(log_in, password):
    get_user_agents_list()
    driver = None
    for j in range(5):
        try:
            driver = get_driver()
            driver.get('https://twitter.com')
            sleep(2)
            # login button
            waiting_for_element(
                driver,
                (By.XPATH, '//a[@href="/login"]'), 5)
            login_bt = driver.find_element(
                By.XPATH, '//a[@href="/login"]')
            webdriver.ActionChains(driver).move_to_element(login_bt).click().perform()
            sleep(2)
            # login input
            waiting_for_element(
                driver,
                (By.CSS_SELECTOR, '#react-root input'), 5)
            inp = driver.find_element(
                By.CSS_SELECTOR,
                '#react-root input')
            send_keys(driver, inp, log_in)
            sleep(2)
            # password input
            waiting_for_element(
                driver,
                (By.CSS_SELECTOR, '#layers > div:nth-child(2) input'), 5)
            inp = driver.find_elements(
                By.CSS_SELECTOR,
                '#layers > div:nth-child(2) input')[1]
            send_keys(driver, inp, password)
            sleep(2)
            submit_check = [(By.XPATH, '//a[@href="/compose/tweet"]'), None]
            passed = recaptcha_solver_api(driver, submit_check_element=submit_check)

            # recaptcha check:
            # driver.get('https://www.google.com/recaptcha/api2/demo')
            # submit_check = [(By.CSS_SELECTOR, 'div.recaptcha-success'), 'Проверка прошла успешно… Ура!']
            # submit = None
            # passed = recaptcha_solver_api(driver, submit=submit,
            #                               submit_check_element=submit_check)

            if passed:
                break
        except Exception as e:
            print_exception_msg(str(e))
            driver.quit()


def recaptcha_solver_api(driver, submit=None, submit_check_element=None):
    start_url = driver.current_url

    def submit_check():
        if (submit_check_element and check_element(driver, submit_check_element)) \
                or driver.current_url != start_url:
            print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" recaptcha(api) is passed")
            return True
        else:
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" failed to confirm the data submission")
            print(Fore.YELLOW + '[INFO]  Submit check:', Fore.CYAN + f" recaptcha(api) is not passed")
            return False

    if submit_check():
        return True
    for j in range(10):
        try:
            src = driver.find_element(By.TAG_NAME, 'iframe').get_attribute('src')
            site_key = src.split('k=')[1].split('&')[0]
        except Exception as e:
            print_exception_msg(f" Unable to find recaptcha site key. {str(e)}")
            return False
        print(Fore.YELLOW + '[INFO]', f" Site key:" + Fore.CYAN + f" {site_key}")
        try:
            response_ = driver.find_element(By.CSS_SELECTOR, '#g-recaptcha-response')
            driver.execute_script("document.getElementById('g-recaptcha-response').style.display = 'block';")
        except Exception as e:
            print_exception_msg(f" Unable to find recaptcha response input. {str(e)}")
            return False
        # get captcha token from api
        key = solve_recaptcha_guru(driver.current_url, site_key)
        print(Fore.YELLOW + '[INFO]', f" Recaptcha Token:" + Fore.CYAN + f" {key}")
        if key is not None:
            # send key to input and submit
            action = webdriver.ActionChains(driver)
            action.send_keys_to_element(response_, key).perform()
            sleep(uniform(.5, 3))
            if not submit:
                driver.find_element(By.TAG_NAME, 'form').submit()
            else:
                submit_bt_click(driver, submit)
            sleep(3)
            # check element and text inside after submission
            if submit_check():
                return True
    else:
        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f" Failed to pass recaptcha(api)")
        beep(2)
        return False


if __name__ == "__main__":
    load_dotenv()
    login_ = os.environ.get('TWITTER_LOGIN')
    password_ = os.environ.get('TWITTER_PASSWORD')
    num_of_rep = 1
    for i in range(num_of_rep):
        print('step:', i + 1)
        login(login_, password_)
