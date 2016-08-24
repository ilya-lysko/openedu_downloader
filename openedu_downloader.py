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
    print("finish")
