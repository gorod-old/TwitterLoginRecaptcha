import os

import requests
import time


def get_api_key():
    return os.environ.get('CAPTCHA_GURU_API_KEY')


def solve_recaptcha_guru(url: str, google_site_key: str):
    if url is None or google_site_key is None:
        return None
    print('captcha.guru.ru -> solve_recaptcha')
    api_key = get_api_key()
    method = 'userrecaptcha'
    r = requests.get('http://api.captcha.guru/in.php?key=' + api_key + '&method=' + method + '&googlekey='
                     + google_site_key + '&pageurl=' + url)
    print(r.text)
    if r.ok and r.text.find('OK') > -1:
        req_id = r.text[r.text.find('|') + 1:]
        for timeout in range(40):
            r = requests.get('http://api.captcha.guru/res.php?key=' + api_key + '&action=get&id=' + req_id)
            if r.text.find('CAPCHA_NOT_READY') > -1:
                time.sleep(10)
            if r.text.find('ERROR') > -1:
                print(r.text)
                break
            if r.text.find('OK') > -1:
                return r.text[r.text.find('|') + 1:]
    return None


def solve_img_captcha_guru(img: str):
    if img is None:
        return None
    print('captcha.guru.ru -> solve_img_recaptcha')
    api_key = get_api_key()
    url = 'http://api.captcha.guru/in.php'
    files = {'file': open(img, 'rb')}
    data = {'key': api_key, 'method': 'post'}
    r = requests.post(url, files=files, data=data)
    if r.ok and r.text.find('OK') > -1:
        req_id = r.text[r.text.find('|') + 1:]
        for timeout in range(40):
            r = requests.get('http://api.captcha.guru/res.php?key=' + api_key + '&action=get&id=' + req_id)
            if r.text.find('CAPCHA_NOT_READY') > -1:
                time.sleep(3)
            if r.text.find('ERROR') > -1:
                print(r.text)
                break
            if r.text.find('OK') > -1:
                result = r.text[r.text.find('|') + 1:]
                return result
    return None
