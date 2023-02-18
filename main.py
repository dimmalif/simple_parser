import json
import re
import sys

import requests
import time
from bs4 import BeautifulSoup
import lxml
import random

url = 'https://www.local.ch/en/q?what=Clinique&where=Switzerland&rid=Dz33&slot=tel'
links = []
all_page = []
to_write = []
to_json = []
to_write.append(url)
progress = 0
page2 = ''
headers = {
    "Accept": "*/*",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

# get HTML file and use it next

req = requests.get(url, headers=headers)
all_page.append(url)
with open('req_website.html', 'w', encoding='utf-8') as file_w:
    file_w.write(req.text)

with open('req_website.html', 'r', encoding='utf-8') as file_r:
    req_website = file_r.read()  # the first old site in html
soup = BeautifulSoup(req_website, 'lxml')

# get all link
try:
    print('Search all page links')
    next_page_for_link = soup.find('a', {'rel': 'next'}).get('href')
    all_page.append(f"https://www.local.ch/{next_page_for_link}")
    url_next_page = f"https://www.local.ch/{next_page_for_link}"
    to_write.append(url_next_page)
    progress = 0
    while True:
        progress += 1
        req_page = requests.get(url_next_page, headers=headers)
        soup_page = BeautifulSoup(req_page.text, 'lxml')
        next_page = soup_page.find('a', {'rel': 'next'}).get('href')
        url_next_page = f"https://www.local.ch/{next_page}"
        all_page.append(url_next_page)
        sys.stdout.write(f"{progress}*")
        sys.stdout.flush()
        time.sleep(random.randrange(1, 3))
except Exception:
    print(Exception)

finally:
    with open('all_page_link', 'w', encoding='utf-8') as file:
        for i in all_page:
            print(i)
            to_write.append(i)
        file.write(f"{to_write}")


# search for data in all links
with open('all_page_link', 'r', encoding='utf-8') as all_page_f:
    all_page_in_page = all_page_f.readline()

try:
    for i in all_page_in_page.split():
        iter = i.replace('[', '').replace(']', '').replace("'", "").replace(',', '')
        progress += 1
        sys.stdout.write(f"{progress}*")
        sys.stdout.flush()
        request = requests.get(iter, headers=headers)
        soup = BeautifulSoup(request.text, 'lxml')

        class_with_links = soup.findAll('a',
                                        class_='card-info clearfix js-gtm-event')  # search class with all links from first page
        for i in range(len(class_with_links)):
            links.append(class_with_links[i].get('href'))

        try:
            for i in range(len(links)):

                try:
                    hospital_req = requests.get(url=links[i], headers=headers)  # get info from first website
                except Exception:
                    print(f"Exception: {Exception}\nCant give info")
                    continue

                hospital_website = BeautifulSoup(hospital_req.text.encode('utf-8'), 'lxml', from_encoding='utf-8')

                try:
                    hospital_name = hospital_website.find('span', {'itemprop': 'name'}).text.encode('utf-8')
                except Exception:
                    hospital_name = ''.encode('utf-8')
                try:
                    hospital_contact = hospital_website.find('div',
                                                             class_='js-routing-modal js-gtm-event js-kpi-event address-lines js-mobile-routing'
                                                             ).findAll('div', class_='row')
                except Exception:
                    hospital_contact = ''

                try:
                    mailing_adress = hospital_contact[0].text.strip().encode('utf-8')
                except Exception:
                    mailing_adress = ''.encode('utf-8')

                try:
                    hospital_adress = mailing_adress.split()[0]
                except Exception:
                    hospital_adress = ''

                try:
                    hospital_poshtal_code = hospital_contact[1].text.split()[0].encode('utf-8')
                except Exception:
                    hospital_poshtal_code = ''.encode('utf-8')

                try:
                    hospital_phone = hospital_website.find('span', class_='js-btn-label').get('data-overlay-label')
                except Exception:
                    hospital_phone = ''

                try:
                    hospital_email = hospital_website.find('a',
                                                           class_='contact-card-link js-gtm-event js-kpi-event').get(
                        'href').encode('utf-8')
                except Exception:
                    hospital_email = ''.encode('utf-8')

                to_json.append(
                    f"'links': {links[i]}\n"
                    f"'name': {hospital_name.decode('utf-8')}\n"
                    f"'maiing adress': {mailing_adress.decode('utf-8')}\n"
                    f"'postcode': {hospital_poshtal_code.decode('utf-8')}\n"
                    f"'city': {hospital_adress.decode('utf-8')}\n"
                    f"'phone': {hospital_phone.strip('Call')}\n"
                    f"'email': {hospital_email.decode('utf-8')}\n\n\n\n"
                )
        except Exception:
            print(f'Exception: {Exception}')
        # finally:
    with open(f'info_all_hospital_in{str(progress)}.txt', 'a+', encoding='utf-8') as file:
        for i in to_json:
            file.write(i)
except:
    with open(f'info_all_hospital_in{str(progress)}.txt', 'a+', encoding='utf-8') as file:
        for i in to_json:
            file.write(i)
    print('error')
finally:
    print('Finaly!')
