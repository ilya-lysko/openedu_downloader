import requests
import re
import os 
import sys
import collections
import lxml.html as html
import json

def create_folder(path, folder_name): 
#Функция создает директорию по заданному пути 
    if not os.path.exists(path + "\\" + folder_name): 
        os.makedirs(path + "\\" + folder_name) 

def downloader(url, name, file_type='.mp4'): 
#Функция осуществляет загрузку видео-файла по url, в файл name 
    name+=file_type 
    r = requests.get(url, stream=True) 
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
    #функция ищет все видео с темы
    videos_with_names = []
    if re.findall(r'http://.*\.mp4', page) != []:
        return re.findall(r'http://.*\.mp4', page)[::2]
        
username = input('Введите логин для авторизации: ')
password = input('Введите пароль для авторизации: ')
url_course = input('Введите ссылку на главную страницу курса: ')
path = input('Введите путь к директории для скачивания: ')
folder = input('Введите название папки, в которую будет происходит скачивание: ')
create_folder(path, folder)
client = authorizer_and_pagegetter(username, password)
page = client.get(url_course).text
dict_with_pages = page_parser(page)

for key in dict_with_pages:
    create_folder(path+'\\'+folder, key)
    path_f_v=path+'\\'+folder+'\\'+key+'\\'
    for i in range(len(dict_with_pages[key])):
        videos = video_finder(client.get(dict_with_pages[key][i][1]).text)
        print(videos)
        if len(videos)>1:
            for j in range(len(videos)):
                name = dict_with_pages[key][i][0]+str(j+1)
                downloader(videos[j], path_f_v+name)
        else:
            downloader(videos[0], path_f_v+dict_with_pages[key][i][0])
client.close()
print('Скачивание закончено')
