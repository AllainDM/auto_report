from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup
import lxml


import config
import list_of_masters
# import address_filter


session = requests.Session()

url_login_get = "https://us.gblnet.net/"
url_login = "https://us.gblnet.net/body/login"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "_csrf": '',
    "return_page": "",
    "username": config.loginUS,
    "password": config.pswUS
}
# Создание сессии, получение токена и авторизация

session_users = requests.Session()

req = session_users.get(url_login_get)

csrf = None

def get_token():
    global csrf
    soup = BeautifulSoup(req.content, 'html.parser')
    # print(soup)
    print("###################")
    scripts = soup.find_all('script')

    for script in scripts:
        if script.string is not None:
            # print(script.string)
            script_lst = script.string.split(" ")
            # print(script_lst)
            for num, val in enumerate(script_lst):
                if val == "_csrf:":
                    csrf = script_lst[num+1]
    print(f"csrf {csrf}")

get_token()


def create_users_sessions():
    while True:
        try:
            data_users["_csrf"] = csrf[1:-3]
            # print(f"data_users {data_users}")
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # print("Сессия Юзера создана 2")
            # print(f"response_users2 {response_users2}")
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            # TODO функция отправки тут отсутствует
            # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            # time.sleep(300)


response_users = create_users_sessions()


async def get_service(date, master=877):
    url_task = "https://us.gblnet.net/task/"
    start_date = date
    # start_date = "23.02.2025"
    end_date = start_date
    link = (f"https://us.gblnet.net/task_list?employee_id0={master}&filter_selector0="
            f"task_staff_wo_division&employee_find_input=&employee_id0={master}&"
            f"filter_selector1=task_state&task_state1_value=2&filter_selector2="
            f"date_finish&date_finish2_value2=3&date_finish2_date1={start_date}+00%3A00&"
            f"date_finish2_date2={end_date}+23%3A59&date_finish2_value=&filter_group_by=")
    print(link)
    # try:
    # Сразу подставим заголовок с токеном.
    HEADERS["_csrf"] = csrf[1:-3]
    html = session_users.get(link, headers=HEADERS)
    answer = []
    brand = "ЕТ"
    if html.status_code == 200:
        # print("Код ответа 200")
        soup = BeautifulSoup(html.text, 'lxml')
        # print(f"soup {soup}")
        table = soup.find_all('tr', class_="cursor_pointer")
        print(f"Количество карточек: {len(table)}")
        master_name = list_of_masters.dict_of_masters_user_id_name[master]
        print(f"master_name {master_name}")
        for card in table:
            # Бренд возьмем по порядковому номеру.
            # Находим строку таблицы
            brand_row = card.find_all('td')
            # print(f"row {brand_row[1].text.strip()}")
            brand = brand_row[1].text.strip()

            # Ищем ссылку с id задания.
            task_link = card.find('a', href=lambda href: href and "/task/" in href)
            task_num = task_link.text.strip()
            # print(f"task: {task_num}")

            # Ищем последний комментарий для определения Мастера.
            last_comment = card.find('td', id=f"td_{task_num}_comment_full_Id")
            # print(last_comment.text)
            match = re.search(r'[А-Яа-я]+\s[А-Яа-я]+\s[А-Яа-я]+', last_comment.text)
            fio = match.group(0).strip()
            # Добавляем если последний коммент от текущего мастера.
            if fio == master_name:
                answer.append([fio, brand, task_num])

    # Вернем в основную функцию, для объединения отчетов разных брендов.
    return answer


async def get_connections_athome(date, master=877):
    url_task = "https://us.gblnet.net/task/"
    start_date = date
    # start_date = "23.02.2025"
    end_date = start_date
    link = (f"https://us.gblnet.net/customer_list?billing0_value=1&filter_selector0="
            f"billing&billing0_value=1&filter_selector1=agreement_date&agreement_date1_value="
            f"{date}&filter_selector2=customer_type&customer_type2_value="
            f"1&filter_selector3=customer_mark&customer_mark3_value=53&filter_group_by=")
    print(link)
    # try:
    # Сразу подставим заголовок с токеном.
    HEADERS["_csrf"] = csrf[1:-3]
    html = session_users.get(link, headers=HEADERS)
    answer = []
    if html.status_code == 200:
        # print("Код ответа 200")
        soup = BeautifulSoup(html.text, 'lxml')
        # print(f"soup {soup}")
        table = soup.find_all('tr', class_="cursor_pointer")
        print(f"Количество карточек: {len(table)}")
        master_name = list_of_masters.dict_of_masters_user_id_name[master]
        print(f"master_name {master_name}")
        for cards in table:
            card = cards.find_all('td')
            # Мастера из карточек
            master_from_user = card[5].text.strip()
            master_from_user = master_from_user.split(" ")
            master_from_user = master_from_user[0]
            print(master_from_user)

            # Мастер которого ищем в карточках
            master_for_search = master_name.split(" ")
            master_for_search = master_for_search[0]

            if master_from_user == master_for_search:
                print(f"Найдено совпадение.")
                client_ls = card[7].text.strip()
                client_ls = client_ls[:-10]


                answer.append([client_ls, master_for_search])

    #
    #
    #
    # # Вернем в основную функцию, для объединения отчетов разных брендов.
    return answer


async def get_connections_et(date, master=877):
    url_task = "https://us.gblnet.net/task/"
    start_date = date
    # start_date = "23.02.2025"
    end_date = start_date
    link = (f"https://us.gblnet.net/customer_list?billing0_value=1&filter_selector0="
            f"billing&billing0_value=1&filter_selector1="
            f"agreement_date&agreement_date1_value={start_date}&filter_selector2="
            f"customer_type&customer_type2_value=1&filter_selector3=tariff&tariff3_value2="
            f"2&tariff3_value=-501&filter_selector4=tariff&tariff4_value2=2&tariff4_value="
            f"-500&filter_selector5=tariff&tariff5_value2=2&tariff5_value="
            f"1083&filter_selector6=customer_mark&customer_mark6_value="
            f"66&filter_selector7=tariff&tariff7_value2=2&tariff7_value="
            f"1088&filter_selector8=tariff&tariff8_value2=2&tariff8_value="
            f"5788&filter_selector9=tariff&tariff9_value2=2&tariff9_value="
            f"12676&filter_group_by=")
    print(link)
    # try:
    # Сразу подставим заголовок с токеном.
    HEADERS["_csrf"] = csrf[1:-3]
    html = session_users.get(link, headers=HEADERS)
    answer = []
    if html.status_code == 200:
        # print("Код ответа 200")
        soup = BeautifulSoup(html.text, 'lxml')
        # print(f"soup {soup}")
        table = soup.find_all('tr', class_="cursor_pointer")
        print(f"Количество карточек: {len(table)}")
        master_name = list_of_masters.dict_of_masters_user_id_name[master]
        print(f"master_name {master_name}")
        for cards in table:
            card = cards.find_all('td')
            # Мастера из карточек
            master_from_user = card[5].text.strip()
            master_from_user = master_from_user.split(" ")
            master_from_user = master_from_user[0]
            print(master_from_user)

            # Мастер которого ищем в карточках
            master_for_search = master_name.split(" ")
            master_for_search = master_for_search[0]

            if master_from_user == master_for_search:
                print(f"Найдено совпадение.")
                client_ls = card[7].text.strip()
                client_ls = client_ls[:-10]


                answer.append([client_ls, master_for_search])

    #
    #
    #
    # # Вернем в основную функцию, для объединения отчетов разных брендов.
    return answer
























































