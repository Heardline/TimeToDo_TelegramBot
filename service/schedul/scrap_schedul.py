import os
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36"
}
URL = "https://www.mirea.ru/schedule/"

SCHEDULE_PATTERNS = ["Экз", "экз", "Экз_", "Зач", "зач", "сессия", "Колледж", "РТУ", "pdf", "doc"]
EXAM_PATTERNS = ["Экз", "экз", "Экз_", "Зач", "зач"]


def get_schedule_urls(patterns):
    try:
        r = requests.get(url=URL, headers=HEADERS)
        r.raise_for_status()
    except requests.HTTPError as errh:
        print("Http Error:", errh)
        return []
    except requests.ConnectionError as errc:
        print("Error Connecting:", errc)
        return []
    except requests.Timeout as errt:
        print("Timeout Error:", errt)
        return []
    except requests.RequestException as err:
        print("Something Else:", err)
        return []

    soup = BeautifulSoup(r.text, 'lxml')
    scheduler_cards = soup.find_all('a', class_="uk-link-toggle")

    schedul_urls = []
    for schedul in scheduler_cards:
        schedul_url = schedul.get('href')
        if not any(re.search(pattern, schedul_url) for pattern in patterns):
            schedul_urls.append(schedul_url)

    return schedul_urls


def download_files(output_dir, url_list):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for schedul_url in url_list:
        try:
            resp = requests.get(schedul_url)
            resp.raise_for_status()
        except requests.HTTPError as errh:
            print("Http Error:", errh)
            continue
        except requests.ConnectionError as errc:
            print("Error Connecting:", errc)
            continue
        except requests.Timeout as errt:
            print("Timeout Error:", errt)
            continue
        except requests.RequestException as err:
            print("Something Else:", err)
            continue

        file_name = os.path.join(output_dir, schedul_url.split("/")[-1])
        with open(file_name, 'wb') as output:
            output.write(resp.content)


def main():
    schedule_urls = get_schedule_urls(SCHEDULE_PATTERNS)
    download_files("data/xlsx", schedule_urls)

    exam_urls = get_schedule_urls(EXAM_PATTERNS)
    download_files("data/exam_xlsx", exam_urls)
