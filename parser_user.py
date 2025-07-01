
import re
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import lxml


import config
import list_of_masters
# import address_filter

# Настройка логирования
logging.basicConfig(level=logging.INFO)

logging.debug("Это отладочное сообщение")
logging.info("Это информационное сообщение")
logging.warning("Это предупреждение")
logging.error("Это ошибка")
logging.critical("Это критическая ошибка")

logger = logging.getLogger(__name__)


# session = requests.Session()

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
# session_users = requests.Session()
#
# req = session_users.get(url_login_get)
#
# csrf = None
#
# def get_token():
#     global csrf
#     soup = BeautifulSoup(req.content, 'html.parser')
#     # logging.debug(soup)
#     logging.debug("###################")
#     scripts = soup.find_all('script')
#
#     for script in scripts:
#         if script.string is not None:
#             # logging.debug(script.string)
#             script_lst = script.string.split(" ")
#             # logging.debug(script_lst)
#             for num, val in enumerate(script_lst):
#                 if val == "_csrf:":
#                     csrf = script_lst[num+1]
#     logging.debug(f"csrf {csrf}")
#
# get_token()
#
#
# def create_users_sessions():
#     while True:
#         try:
#             data_users["_csrf"] = csrf[1:-3]
#             # logging.debug(f"data_users {data_users}")
#             response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
#             # logging.debug("Сессия Юзера создана 2")
#             # logging.debug(f"response_users2 {response_users2}")
#             return response_users2
#         except ConnectionError:
#             logging.debug("Ошибка создания сессии")
#             # TODO функция отправки тут отсутствует
#             # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
#             # time.sleep(300)
#
#
# response_users = create_users_sessions()

# Новый способ получения токена и авторизации.
def get_token(session_users):
    req = session_users.get(url_login_get)
    soup = BeautifulSoup(req.content, 'html.parser')
    # print(soup)
    # print("###################")
    scripts = soup.find_all('script')

    csrf = None
    for script in scripts:
        if script.string is not None:
            script_lst = script.string.split(" ")
            for num, val in enumerate(script_lst):
                if val == "_csrf:":
                    csrf = script_lst[num+1]
                    break
        if csrf:
            break
    print(f"csrf {csrf}")
    return csrf[1:-3] if csrf else None

def create_users_sessions():
    session_users = requests.Session()
    csrf = get_token(session_users)
    if not csrf:
        raise Exception("CSRF token not found")

    data_users["_csrf"] = csrf
    response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS)
    if response_users2.status_code != 200:
        raise Exception("Failed to create user session")
    return session_users


async def get_service(date, master=877):
    url_task = "https://us.gblnet.net/task/"
    start_date = date
    # start_date = "23.02.2025"
    end_date = start_date
    link2 = (f"https://us.gblnet.net/task_list?employee_id0={master}&filter_selector0="
            f"task_staff_wo_division&employee_find_input=&employee_id0={master}&"
            f"filter_selector1=task_state&task_state1_value=2&filter_selector2="
            f"date_finish&date_finish2_value2=3&date_finish2_date1={start_date}+00%3A00&"
            f"date_finish2_date2={end_date}+23%3A59&date_finish2_value=&filter_group_by=")

    link = (f"https://us.gblnet.net/task_list?employee_id0={master}&filter_selector0="
            f"task_staff_wo_division&employee_find_input=&employee_id0={master}&"
            f"filter_selector1=task_state&task_state1_value=2&filter_selector2="
            f"date_finish&date_finish2_value2=1&date_finish2_date1={start_date}+00%3A00&"
            f"date_finish2_date2={end_date}+23%3A59&date_finish2_value=&filter_group_by=")

    logging.info(link)
    # try:

    # Новый способ получения токена и авторизации.
    session_users = create_users_sessions()

    # Новый способ получения токена и авторизации.
    HEADERS["_csrf"] = data_users["_csrf"]
    # # Сразу подставим заголовок с токеном.
    # HEADERS["_csrf"] = csrf[1:-3]

    html = session_users.get(link, headers=HEADERS)
    answer = []
    brand = "ЕТ"
    if html.status_code == 200:
        # logging.debug("Код ответа 200")
        soup = BeautifulSoup(html.text, 'lxml')
        # logging.debug(f"soup {soup}")
        table = soup.find_all('tr', class_="cursor_pointer")
        logging.debug(f"Количество карточек: {len(table)}")
        master_name = list_of_masters.dict_of_masters_user_id_name[master]
        logging.debug(f"master_name {master_name}")
        for card in table:
            # Бренд возьмем по порядковому номеру.
            # Находим строку таблицы
            brand_row = card.find_all('td')
            # logging.debug(f"row {brand_row[1].text.strip()}")
            brand = brand_row[1].text.strip()

            # Ищем ссылку с id задания.
            task_link = card.find('a', href=lambda href: href and "/task/" in href)
            task_num = task_link.text.strip()
            # logging.debug(f"task: {task_num}")

            # Ищем тип задания
            task_type = card.find('td', id=f"td_{task_num}_description_full_Id")
            task_type = task_type.find('b')
            logging.debug(f"task_type {task_type.text.strip()}")
            task_type = task_type.text.strip()
            # Подключение интернета игнорируем.
            if task_type == "Подключение Интернет" or task_type == "Промоутер - Подключение Интернет":
                continue
            if task_type == "Подключение ТВ" or task_type == "Промоутер - Подключение ТВ":
                continue
            if task_type == "Подключить быстрее":
                continue
            if task_type == "Подключение домофона":

                # TODO нужна отдельная функция для домофонов
                continue

            # Ищем последний комментарий для определения Мастера.
            last_comment = card.find('td', id=f"td_{task_num}_comment_full_Id")
            # logging.debug(last_comment.text)
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
    link1 = (f"https://us.gblnet.net/customer_list?billing0_value=1&filter_selector0="
            f"billing&billing0_value=1&filter_selector1=agreement_date&agreement_date1_value="
            f"{date}&filter_selector2=customer_type&customer_type2_value="
            f"1&filter_selector3=customer_mark&customer_mark3_value=53&filter_group_by=")


    link = (f"https://us.gblnet.net/customer_list?billing0_value=1&filter_selector0="
            f"billing&billing0_value=1&filter_selector1="
            f"agreement_date&agreement_date1_value={date}&filter_selector2="
            f"customer_type&customer_type2_value=1&filter_selector3="
            f"tariff&tariff3_value2=2&tariff3_value=-501&filter_selector4="
            "tariff&tariff4_value2=2&tariff4_value=-500&filter_selector5="
            f"tariff&tariff5_value2=2&tariff5_value=1083&filter_selector7="
            f"tariff&tariff7_value2=2&tariff7_value=1088&filter_selector8="
            f"tariff&tariff8_value2=2&tariff8_value=5788&filter_selector9="
            f"tariff&tariff9_value2=2&tariff9_value=12676&filter_group_by=")

    logging.info(link)
    # Новый способ получения токена и авторизации.
    session_users = create_users_sessions()

    # Новый способ получения токена и авторизации.
    HEADERS["_csrf"] = data_users["_csrf"]
    # # Сразу подставим заголовок с токеном.
    # HEADERS["_csrf"] = csrf[1:-3]

    html = session_users.get(link, headers=HEADERS)
    answer = []
    if html.status_code == 200:
        # logging.debug("Код ответа 200")
        soup = BeautifulSoup(html.text, 'lxml')
        # logging.debug(f"soup {soup}")
        table = soup.find_all('tr', class_="cursor_pointer")
        logging.debug(f"Количество карточек: {len(table)}")
        master_name = list_of_masters.dict_of_masters_user_id_name[master]
        logging.debug(f"master_name {master_name}")
        for cards in table:
            card = cards.find_all('td')
            # Мастера из карточек
            master_from_user = card[5].text.strip()
            master_from_user = master_from_user.split(" ")
            master_from_user = master_from_user[0]
            # logging.debug(master_from_user)

            # Мастер которого ищем в карточках
            master_for_search = master_name.split(" ")
            master_for_search = master_for_search[0]

            if master_from_user == master_for_search:
                logging.debug(f"Найдено совпадение.")
                logging.debug(master_from_user)
                # client_ls = card[7].text.strip()
                # client_ls = client_ls[:-10]

                client_ls = card[6].text.strip()


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
    link = "https://us.gblnet.net/"
    link1 = (f"https://us.gblnet.net/customer_list?billing0_value=1&filter_selector0="
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

    link2 = (f"https://us.gblnet.net/customer_list?billing0_value=1&filter_selector0="
            f"billing&billing0_value=1&filter_selector1="
            f"agreement_date&agreement_date1_value={start_date}&filter_selector2="
            f"customer_type&customer_type2_value=1&filter_selector3="
            f"tariff&tariff3_value2=2&tariff3_value=-501&filter_selector4="
            "tariff&tariff4_value2=2&tariff4_value=-500&filter_selector5="
            f"tariff&tariff5_value2=2&tariff5_value=1083&filter_selector7="
            f"tariff&tariff7_value2=2&tariff7_value=1088&filter_selector8="
            f"tariff&tariff8_value2=2&tariff8_value=5788&filter_selector9="
            f"tariff&tariff9_value2=2&tariff9_value=12676&filter_group_by=")

    logging.info(link)
    # try:
    # Новый способ получения токена и авторизации.
    session_users = create_users_sessions()

    # Новый способ получения токена и авторизации.
    HEADERS["_csrf"] = data_users["_csrf"]
    # # Сразу подставим заголовок с токеном.
    # HEADERS["_csrf"] = csrf[1:-3]

    html = session_users.get(link, headers=HEADERS)
    answer = []
    if html.status_code == 200:
        # logging.debug("Код ответа 200")
        soup = BeautifulSoup(html.text, 'lxml')
        # logging.debug(f"soup {soup}")
        table = soup.find_all('tr', class_="cursor_pointer")
        logging.debug(f"Количество карточек: {len(table)}")
        master_name = list_of_masters.dict_of_masters_user_id_name[master]
        logging.debug(f"master_name {master_name}")
        for cards in table:
            card = cards.find_all('td')
            # Мастера из карточек
            master_from_user = card[5].text.strip()
            master_from_user = master_from_user.split(" ")
            master_from_user = master_from_user[0]
            # logging.debug(master_from_user)

            # Мастер которого ищем в карточках
            master_for_search = master_name.split(" ")
            master_for_search = master_for_search[0]

            if master_from_user == master_for_search:
                logging.debug(f"Найдено совпадение.")
                logging.debug(master_from_user)
                # client_ls = card[7].text.strip()
                # client_ls = client_ls[:-10]

                client_ls = card[6].text.strip()


                answer.append([client_ls, master_for_search])

    #
    #
    #
    # # Вернем в основную функцию, для объединения отчетов разных брендов.
    return answer
























































