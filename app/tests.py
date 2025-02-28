from django.test import TestCase

from lxml import html
import requests
import re

headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def get_kladr_code(city):
    s = requests.Session()
    q = city + ' site:kladr-rf.ru'
    q = '+'.join(q.split())
    url = 'https://www.google.com/search?q=' + q
    r = s.get(url, headers=headers_Get)
    tree = html.fromstring(r.content)
    list_link = tree.xpath('//div/div/div/a[contains(@href,"https://kladr-rf.ru/")]/@href')
    items_list_link = list_link[0].split('/')
    kladr_code = items_list_link[4]
    return kladr_code


def get_dict_subject_rf():
    # Мировые судьи
    s = requests.Session()
    url = 'https://sudrf.ru/index.php?id=300&var=true'
    r = s.get(url, headers=headers_Get, verify=False)
    tree = html.fromstring(r.content)
    list_options = tree.xpath('//select/option')
    dict = {}
    for item in list_options:
        dict[item.xpath('./@value')[0]] = item.text
    return dict


def get_sudrf():

    def get_sud_address(url):
        url = 'http://119.irk.msudrf.ru'
        r = s.get(url, headers=headers_Get)
        tree = html.fromstring(r.content)
        sud_adr = tree.xpath('//p[@id="court_address"]/text()')[0]
        return sud_adr

    s = requests.Session()
    url = "https://sudrf.ru/index.php?id=300&act=go_ms_search&searchtype=ms&var=true&ms_type=ms&" \
          "court_subj=38&" \
          "ms_city=%C8%F0%EA%F3%F2%F1%EA&" \
          "ms_street=%CB%E5%ED%E8%ED%E0"
    r = s.get(url, headers=headers_Get, verify=False)
    tree = html.fromstring(r.content)

    table_rows = tree.xpath('//table[@class="msSearchResultTbl msFullSearchResultTbl"]/tr')

    dict_sud = {}
    dict_sud_list = {}
    dict_sud_list['court'] = []
    for item in table_rows:
        sud_name = item.xpath('./td[1]/a/text()')
        sud_url = item.xpath('./td[1]/div//a/@href')
        sud_terr = item.xpath('./td[3]/text()')
        sud_comment = item.xpath('./td[4]/text()')

        test = {}
        if len(sud_name) > 0:
            test['name'] = sud_name[0]
            test['url'] = sud_url[0]
            test['terr'] = sud_terr[0]
            test['comment'] = sud_comment[0]
            dict_sud_list['court'].append(test)

    print(f'simple dict_test - {dict_sud_list}')

    dict_sud_list['court'][0].update({'email': 'mail'})
    print(dict_sud_list['court'][0])

    for key in dict_sud_list:
        print(f'for key - {key}')
        # address = get_sud_address(dict_sud[key][0])
        # dict_sud[key].append(address)

# ___________________________________________________________

#
# results = [t for t in polygonData if t[0] > 55.607 and t[1] < 37.494]
# print(results)
# print(f'Количество элементов в polygonData - {len(polygonData[0])}')
# print(f'Первый элемент в polygonData - {polygonData[0][1]}')
# print(f'Ширина в первом элементе polygonData - {polygonData[0][1][0]}')
# print(f'Долгота в первом элементе polygonData - {polygonData[0][1][1]}')
#
# latitude_list = []
# longitude_list = []
#
# for i in range(len(polygonData[0])):
#     latitude_list.append(polygonData[0][i][0])
#     longitude_list.append(polygonData[0][i][1])
#
# # print(max(longitude_list))
# # print(min(latitude_list))
#
# latitude_list = []
# longitude_list = []
#
# for i in range(len(polygonData_test)):
#     print(f'----- {i} ')
#     for j in range(len(polygonData_test[i])):
#         latitude_list.append(polygonData_test[i][j][0])
#         longitude_list.append(polygonData_test[i][j][1])
#     print(max(longitude_list))
#     print(min(latitude_list))


# url = 'https://mos-sud.ru/api/courts'
# def get_courts(url):
#     s = requests.Session()
#     r = s.get(url, headers=headers_get)
#
#     # tree = html.fromstring(r.content)
#     court = r.json()
#     # for i in range(len(court)):
#     #     print(court[i]['address'])
#
#     for item in court:
#         print(f"| {item['number']} | {item['address']} *** {item['fullName']}")
#
# get_courts(url)

import num2words
import transliterate
import json

print(num2words.num2words(10101.88, lang='ru', to='currency', currency='RUB'))

print(transliterate.translit('Иванов_Иван_Иванович', reversed=True))

headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

import datetime

# r = requests.post('https://mos-gorsud.ru/territorial/search', data={'court':'77RS0009'}, headers=headers_get)

# url = 'https://sudrf.ru/index.php?id=300&act=podsud_search&searchtype=podsud&court_subj=50&fs_city=&fs_street='
# r = requests.get(url, headers=headers_get, verify=False)
# tree = html.fromstring(r.text)
# courts = tree.xpath('//div[@class="sud_info"]')
#
#
# print(f'size - {len(courts)}')
# for item in courts:
#     sud_name = item.xpath('./div[@class="sud_name"]/text()')[0]
#     sud_ter_name = item.xpath('./div[@class="sud_ter_name"]/text()')[0]
#     code = item.xpath('./text()')[2]
#     address = item.xpath('./text()')[3]
#     phone = item.xpath('./text()')[4]
#     email = item.xpath('./a/text()')[0]
#     url = item.xpath('./div/a/text()')[0]
#     print(f'{sud_name} : {sud_ter_name} : {code} : {address} : {phone} : {email} : {url}')


url = 'https://www.cbr.ru/hd_base/KeyRate/'
r = requests.get(url, headers=headers_get)
pattern = r'\bvar\s+settings\s*=\s*(\{.*?\})\s*;\s*\n'
tree = html.fromstring(r.text)
scripts = tree.xpath('//div[@class="container-fluid"]//script/text()')
categories = re.findall('"categories":.*?]', scripts[2])
print(f'categories - {categories}')
data = re.findall('"data":.*?]', scripts[2])
print(f'data - {data}')
categories.append(data[0])
print(f'append categories - {categories}')

res = '{' + categories[0].replace('"','\'') + ',' + categories[1].replace('"','\'') + '}'
result = eval(res)

for i in range(0, len(result['categories'])):
    date_time_obj = datetime.datetime.strptime(result['categories'][i], '%d.%m.%Y')
    print(date_time_obj.date())
    print(result['categories'][i] + '---' + str(result['data'][i]))

print(len(result['categories']))
print(len(result['data']))







