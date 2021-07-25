import requests, re
import pandas as pd
from bs4 import BeautifulSoup

## Функция парсинга расписания с сайта Mirea 
def get_schedul():
    headers = {
        "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36"
    }
    url = "https://www.mirea.ru/schedule/"
    r = requests.get(url=url,headers=headers)

    soup = BeautifulSoup(r.text,'lxml')
    ## Получаем список ссылок на расписания. У нас они содержится в карточках uk-link-toggle. 
    scheduler_cards = soup.find_all('a', class_="uk-link-toggle")

    schedul_urls = []
    for schedul in scheduler_cards:
        schedul_url = schedul.get('href')
        ## Ищет названия расписаний, в которых не содержится экз и т.д.
        if re.search(r'"Экз|экз|Экз_',schedul_url) or re.search(r'Зач|зач|сессия|Колледж|РТУ',schedul_url) or re.search(r'pdf|doc',schedul_url) :
            pass
        else:
            schedul_urls.append(schedul_url)
    return schedul_urls ## Обязательно передать обратно список ссылок.

## Отдельная функция. Тоже самое что и сверху, только берет экзамены. Сделал на будущие
def get_schedul_exam():
    headers = {
        "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36"
    }
    url = "https://www.mirea.ru/schedule/"
    r = requests.get(url=url,headers=headers)

    soup = BeautifulSoup(r.text,'lxml')
    scheduler_cards = soup.find_all('a', class_="uk-link-toggle")

    schedul_urls = []
    for schedul in scheduler_cards:
        schedul_url = schedul.get('href')
        if re.search(r'"Экз|экз|Экз_',schedul_url) or re.search(r'Зач|зач',schedul_url):
            schedul_urls.append(schedul_url)
    return schedul_urls

## Можно не сохранять, однако я решил это делать, чтобы отслеживать изменения
def download_xlsx():
    for schedul_url in get_schedul():
        resp = requests.get(schedul_url)
        with open("data/xlsx/"+schedul_url.split("/")[-1],'wb') as output:
            output.write(resp.content)
