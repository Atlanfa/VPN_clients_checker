import json

from telebot import types

from utils import chunks, decrement_month, increment_month, increment_year, decrement_year


def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_add_server = types.KeyboardButton('Добавить Сервер')
    btn_add_user = types.KeyboardButton('Добавить пользователя')
    btn_find_user = types.KeyboardButton('Найти Пользователя')
    btn_find_outdated_users = types.KeyboardButton('Показать Просроченых Пользователей')
    btn_servers_info = types.KeyboardButton('Информация О Серверах')
    markup.add(btn_add_server, btn_add_user, btn_find_user, btn_find_outdated_users, btn_servers_info)
    return markup


def cancel_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_cancel = types.KeyboardButton('ОТМЕНА')
    markup.add(btn_cancel)
    return markup


# Inline Keybord that shows buttons with names "Удалить Пользователя" and "Продлить Период" and callback data field with id of user
def inline_keyboard_delete_user(user_id, server_id):
    markup = types.InlineKeyboardMarkup()
    btn_delete_user = types.InlineKeyboardButton('Удалить Пользователя', callback_data='delete_user_' + str(user_id) + '_' + str(server_id))
    btn_extend_period = types.InlineKeyboardButton('Продлить Период', callback_data='extend_period_' + str(user_id) + '_' + str(server_id))
    markup.add(btn_delete_user, btn_extend_period)
    return markup


# Inline keyboard with calendar buttons and callback data with date and month and year that was chosen
def inline_keyboard_calendar(date, user_id, server_id):
    month = date.split('/')[1]
    year = date.split('/')[2]
    day = date.split('/')[0]
    markup = types.InlineKeyboardMarkup(row_width=2)
    prev_month = decrement_month(date)
    next_month = increment_month(date)
    next_year = increment_year(date)
    prev_year = decrement_year(date)
    btn_prev_month = types.InlineKeyboardButton(f'< {prev_month[1]} месяц', callback_data='prev_month_' + str(day) + '_' + str(prev_month[1]) + '_' + str(prev_month[2])+ '_' + str(user_id) + '_' + str(server_id))
    btn_next_month = types.InlineKeyboardButton(f' {next_month[1]} месяц >', callback_data='next_month_' + str(day) + '_' + str(next_month[1]) + '_' + str(next_month[2])+ '_' + str(user_id) + '_' + str(server_id))
    btn_prev_year = types.InlineKeyboardButton(f'<< {prev_year[2]} год ', callback_data='prev_year_' + str(day) + '_' + str(month) + '_' + str(prev_year[2])+ '_' + str(user_id) + '_' + str(server_id))
    btn_next_year = types.InlineKeyboardButton(f'{next_year[2]} год >>', callback_data='next_year_' + str(day) + '_' + str(month) + '_' + str(next_year[2])+ '_' + str(user_id) + '_' + str(server_id))
    btn_submit = types.InlineKeyboardButton('Подтвердить', callback_data='submit_calendar_' + str(day) + '_' + str(month) + '_' + str(year)+ '_' + str(user_id) + '_' + str(server_id))
    markup.add(btn_prev_month, btn_next_month, btn_prev_year, btn_next_year, btn_submit)
    return markup


# Inline Keyboard with buttons with names ips of server + amount of users on server and callback data with ip of server
def inline_keyboard_servers_info(page):
    markup = types.InlineKeyboardMarkup()
    # read data_base.json and get all ips and amount of users on server
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    servers_chunked = chunks(data['data']['servers'])

    def mini_keyboard():
        markup = types.InlineKeyboardMarkup()
        for server in servers_chunked[page]:
            print(server)
            btn_server = types.InlineKeyboardButton(server['server_ip'] + ' ' + str(len(server['users'])), callback_data=f"server_" + server['server_ip'])
            markup.add(btn_server)
        return markup
    if len(servers_chunked) == 1:
        markup = mini_keyboard()
    else:
        markup.add(mini_keyboard())
        if page == 0:
            btn_next_page = types.InlineKeyboardButton('Следующая страница', callback_data='next_page_' + str(page + 1))
            markup.add(btn_next_page)
        elif page == len(servers_chunked) - 1:
            btn_prev_page = types.InlineKeyboardButton('Предыдущая страница', callback_data='prev_page_' + str(page - 1))
            markup.add(btn_prev_page)
        else:
            btn_prev_page = types.InlineKeyboardButton('Предыдущая страница', callback_data='prev_page_' + str(page - 1))
            btn_next_page = types.InlineKeyboardButton('Следующая страница', callback_data='next_page_' + str(page + 1))
            markup.add(btn_prev_page, btn_next_page)
    return markup
