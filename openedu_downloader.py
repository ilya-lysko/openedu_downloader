import requests
import re
import os
from itertools import groupby
import sys
import lxml.html as html
import json

def create_folder(path, folder_name): 
    #Функция создает директорию по заданному пути
    if not os.path.exists(path + "/" + re.sub('[^\w_.)( -]', '', folder_name)):
        os.makedirs(path + "/" + re.sub('[^\w_.)( -]', '', folder_name))

def downloader(url, name, file_type='.mp4'): 
    #Функция осуществляет загрузку видео-файла по url, в файл name 
    name += file_type 
    r = requests.get(url, stream=True)
    if not os.path.exists(name):
        with open(name, 'wb') as f: 
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: 
                    f.write(chunk)

def authorizer_and_pagegetter(username, password, URL='https://sso.openedu.ru/login/', next_page='/oauth2/authorize%3Fstate%3DYpbWrm0u6VoE6nOvTi47PQLaC5CB5ZFJ%26redirect_uri%3Dhttps%3A//openedu.ru/complete/npoedsso/%26response_type%3Dcode%26client_id%3D808f52636759e3616f1a%26auth_entry%3Dlogin'): 
    #Функция авторизуется и загружает страницу курса для парсинга. Возвращает страницу курса
    client = requests.session()
    csrf = client.get(URL).cookies['csrftoken'] 
    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrf, next=next_page) 
    r = client.post(URL, data=login_data, headers=dict(Referer=URL)) 
    return client

def page_parser(page):
    #Функция осуществляет парсинг страниц. Возвращает словарь со следующе структурой: ключ - название модуля, значение - список из 2-х элементов
    #первый - название урока, второй - ссылка на страницу урока
    modules = {}
    html_page = html.fromstring(page)
    for x in html_page.find_class('chapter-content-container'):
        modul_name = x.attrib['aria-label'][0:-8]
        lst=[]
        for y in x.find_class('accordion-nav'):
            lst.append([y.find_class('accordion-display-name')[0].text_content(),y.attrib['href']])
        modules[modul_name]=lst
    return modules

def video_finder(page):
    #функция ищет все видео с темы + названия видео
    if re.findall(r'http://.*\.mp4', page) != [] and re.findall(r'data-page-title="(.*)"', page) != []:
        return list(zip(re.findall(r'http://.*\.mp4', page)[::2], 
                               re.findall(r'data-page-title="(.*)"', page)))
    else:
        return 1
        
def main():
    username = input('Ваш логин или email: ')
    password = input('Ваш пароль: ')
    course_url = input('Ссылка на курс  (на вкладку "Курс"): ')
    download_path = re.sub(r'\\', '/', (input('Ссылка на папку загрузки: ')))

    client = authorizer_and_pagegetter(username, password)
    page = client.get(course_url).text
    download_path += "/" + re.findall(r'<div class="course-header">\n            \n            (.*)', page)[0]
    table = page_parser(page)

    for i in table:
        create_folder(download_path, i)
        for j in table[i]:
            video_list = video_finder(client.get("https://courses.openedu.ru" + j[1]).text)
            g = 1
            if video_list != 1:
                for x in video_list:
                    downloader(x[0], download_path + "/" + re.sub('[^\w_.)( -]', '', i) + "/" + "Лекция {0} ".format(g) + re.sub('[^\w_.)( -]', '', x[1]))
                    g += 1
    client.close()
    print("Закачка закончена. Если были какие-то замечания или пожелания - напишите авторам скрипта.")
    
if __name__ == '__main__':
    try:
        main()
    except:
        print('\n', 'Проверьте корректность введенных данных и наличие курса. \nТочно ссылка на вкладку "Курс"? \nВсе верно? Сообщите авторам скрипта.')
