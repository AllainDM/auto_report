
def create_text_to_bot(master, service, connection_athome):
    # # Фамилию мастера возьмем из первой заявки
    # # TODO необходимо решить с однофамильцами, пока достается еще и имя, но его не читает report
    # master = text_list[0][0].split(" ")
    # master = f"{master[0]} {master[1]}"
    # print(f"Мастер: {master}")

    at_int = len(connection_athome)
    at_int_pri = 0      # Привлеченные. Не умеет извлекать, но в шаблон пишем.
    at_serv = 0         # Количество обычных сервисов.
    at_serv_list = []   # Список для номеров сервисов.

    et_int = 0
    et_int_pri = 0      # Привлеченные. Не умеет извлекать, но в шаблон пишем.
    et_tv = 0
    et_tv_pri = 0       # Привлеченные. Не умеет извлекать, но в шаблон пишем.
    et_dom = 0
    et_dom_pri = 0      # Привлеченные. Не умеет извлекать, но в шаблон пишем.
    et_serv = 0         # Количество обычных сервисов.
    et_serv_list = []   # Список для номеров сервисов.
    et_serv_tv = 0

    for i in service:
        if i[1] == 'Эт-Хоум':
            at_serv += 1
            at_serv_list.append(i[2])
        elif i[1] == 'ЭлектронТелеком':
            et_serv += 1
            et_serv_list.append(i[2])

    # Список ли подключений
    list_athome_connection = [i[0] for i in connection_athome]
    print(f"list_athome_connection {list_athome_connection}")

    at_serv_str = " ".join(at_serv_list)
    et_serv_str = " ".join(et_serv_list)
    athome_connection_ls_str =  " ".join(list_athome_connection)


    answer = (f"{master} \n\n"
              f"ЭХ: интернет {at_int}({at_int_pri} прив), сервис {at_serv} {at_serv_str}\n"
              f"ЕТ: интернет {et_int}({et_int_pri} прив), "
              f"ТВ {et_tv}({et_tv_pri} прив), \n"
              f"домофон {et_dom}({et_dom_pri} прив), "
              f"сервис интернет {et_serv} {et_serv_str}, "
              f"сервис ТВ {et_serv_tv} \n\n"
              f"Подключения ЛС: {athome_connection_ls_str} \n\n"
              )

    print(answer)
    return answer
