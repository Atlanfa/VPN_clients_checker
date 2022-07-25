import json
from datetime import datetime

import telebot

from keyboard import main_reply_keyboard, cancel_reply_keyboard, inline_keyboard_delete_user, inline_keyboard_calendar, \
    inline_keyboard_servers_info
from KEY import TOKEN

API_TOKEN = f'{TOKEN}'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, text='Привет! Я бот для учета пользователей ВПН. Для начала работы выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())
    add_user_chat_id_to_DB(message)


def add_user_chat_id_to_DB(message):
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    # check if user already exist in DB
    for user in data['data']['users']:
        if user['user_id'] == message.chat.id:
            bot.send_message(message.chat.id, text='Вы уже зарегистрированы в базе данных.')
            bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())
            return

    data['data']['users'].append({'user_name': message.chat.first_name, 'user_id': message.chat.id})
    with open('data_base.json', 'w') as f:
        json.dump(data, f)
    bot.send_message(message.chat.id, text='Пользователь добавлен в базу данных.')
    bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())


@bot.message_handler(content_types=['text'])
def reply_keyboard_handler(message):
    if message.text == '/start':
        send_welcome(message)
    # после получения сообщения "Добавить Сервер" пользователь должен ввести IP адрес сервера и нажать кнопку "Добавить" что бы сохранить данные о сервере
    if message.text == 'Добавить Сервер':
        bot.send_message(message.chat.id, text='Введите IP адрес сервера:', reply_markup=cancel_reply_keyboard())
        bot.register_next_step_handler(message, add_server)
    if message.text == 'Добавить пользователя':
        bot.send_message(message.chat.id, text='Выберите сервер:', reply_markup=inline_keyboard_servers_info(0))
        bot.register_next_step_handler(message, add_user)
    if message.text == 'Найти Пользователя':
        bot.send_message(message.chat.id, text='Введите имя пользователя:', reply_markup=cancel_reply_keyboard())
        bot.register_next_step_handler(message, find_user)
    if message.text == "Показать Просроченых Пользователей":
        bot.send_message(message.chat.id, text='Вот список пользователей у которых закончилась подписка')
        bot.send_message(message.chat.id, text=show_users_with_expired_subscription())
    if message.text == "Информация О Серверах":
        # send message with ip of every server and amount of usres on each server
        bot.send_message(message.chat.id, text='Вот информация о всех серверах:')
        bot.send_message(message.chat.id, text=show_servers_info())
    if message.text == "Отмена":
        bot.send_message(message.chat.id, text='Выберите действие:', reply_markup=main_reply_keyboard())


def show_servers_info():
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    text = ''
    for server in data['data']['servers']:
        text += str(server['server_ip']) + '\n'
        text += 'Количество пользователей: ' + str(len(server['users'])) + '\n'
    return text


def show_users_with_expired_subscription():
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    users_with_expired_subscription = []
    for server in data['data']['servers']:
        for user in server['users']:
            # tern user['end_trail'] that is in format 31/10/2010 into datetime object
            end_trail = datetime.strptime(user['end_trail'], '%d/%m/%Y')

            if end_trail < datetime.now():
                users_with_expired_subscription.append(user['user_name'])
    text = ''
    for user in users_with_expired_subscription:
        text += str(user) + '\n'
    return text


def find_user(message):
    name = message.text
    # tern data_base.json into dict in the variable data
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    # find user in data['data']['servers']['users'] and save it to user_index
    user_index = 0
    server_index = None
    for i in range(len(data['data']['servers'])):
        for j in range(len(data['data']['servers'][i]['users'])):
            if data['data']['servers'][i]['users'][j]['user_name'] == name:
                user_index = j
                server_index = i
                break
    if server_index is None:
        bot.send_message(message.chat.id, text='Пользователя с таким именем нет в базе данных.')
        bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())
    else:
        bot.send_message(message.chat.id, text='Пользователь найден!')
        bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())
        bot.send_message(message.chat.id, text='Дата начала подписки: ' + data['data']['servers'][server_index]['users'][user_index]['start_trail'])
        bot.send_message(message.chat.id, text='Дата конца подписки: ' + data['data']['servers'][server_index]['users'][user_index]['end_trail'])
        bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())
        bot.send_message(message.chat.id, text='Для удаления пользователя нажмите кнопку "Удалить пользователя", что бы изменить дату подписки нажмите "Продлить подписку"', reply_markup=inline_keyboard_delete_user(user_id=user_index, server_id=server_index))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # получаем id чата и id пользователя из callback_data
    user_id = call.from_user.id

    # tern data_base.json into dict in the variable data

    # если пользователь нажал кнопку "Удалить пользователя"
    if 'delete_user' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        # удаляем пользователя из базы данных
        with open('data_base.json', 'r') as f:
            data = json.load(f)
        data['data']['servers'][int(server_id)]['users'].pop(int(user_index))
        # сохраняем изменения в файле data_base.json
        with open('data_base.json', 'w') as f:
            json.dump(data, f)
        # отправляем пользователю сообщение об успешном удалении пользователя
        bot.send_message(user_id, text='Пользователь успешно удален!')
    if 'extend_period' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        with open('data_base.json', 'r') as f:
            data = json.load(f)
        bot.send_message(user_id, text=f"Введите новую дату конца подписки: новая дата {data['data']['servers'][int(server_id)]['users'][int(user_index)]['start_trail']}", reply_markup=inline_keyboard_calendar(date=data['data']['servers'][int(server_id)]['users'][int(user_index)]['start_trail'], user_id=user_index, server_id=server_id))
    if 'prev_month' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        year = call.data.split('_')[-3]
        month = call.data.split('_')[-4]
        day = call.data.split('_')[-5]
        #print(day, month, year)
        bot.send_message(user_id, text=f"Новая дата - {day}/{month}/{year}", reply_markup=inline_keyboard_calendar(date=f'{day}/{month}/{year}', user_id=user_index, server_id=server_id))
    if 'next_month' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        year = call.data.split('_')[-3]
        month = call.data.split('_')[-4]
        day = call.data.split('_')[-5]
        #print(day, month, year)
        bot.send_message(user_id, text=f"Новая дата - {day}/{month}/{year}", reply_markup=inline_keyboard_calendar(date=f'{day}/{month}/{year}', user_id=user_index, server_id=server_id))
    if 'prev_year' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        year = call.data.split('_')[-3]
        month = call.data.split('_')[-4]
        day = call.data.split('_')[-5]
        #print(day, month, year)
        bot.send_message(user_id, text=f"Новая дата - {day}/{month}/{year}", reply_markup=inline_keyboard_calendar(date=f'{day}/{month}/{year}', user_id=user_index, server_id=server_id))
    if 'next_year' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        year = call.data.split('_')[-3]
        month = call.data.split('_')[-4]
        day = call.data.split('_')[-5]
        bot.send_message(user_id, text=f"Новая дата - {day}/{month}/{year}", reply_markup=inline_keyboard_calendar(date=f'{day}/{month}/{year}', user_id=user_index, server_id=server_id))
    if 'submit' in call.data:
        server_id = call.data.split('_')[-1]
        user_index = call.data.split('_')[-2]
        year = call.data.split('_')[-3]
        month = call.data.split('_')[-4]
        day = call.data.split('_')[-5]
        #print(day, month, year)
        if check_if_date_is_real(f'{day}/{month}/{year}'):
            with open('data_base.json', 'r') as f:
                data = json.load(f)
            data['data']['servers'][int(server_id)]['users'][int(user_index)]['end_trail'] = f'{day}/{month}/{year}'
            with open('data_base.json', 'w') as f:
                json.dump(data, f)
            bot.send_message(call.message.chat.id, text=f"Дата окончания подписки изменена на {day}/{month}/{year}", reply_markup=main_reply_keyboard())
        else:
            with open('data_base.json', 'r') as f:
                data = json.load(f)
            day = 28
            data['data']['servers'][int(server_id)]['users'][int(user_index)]['end_trail'] = f'{day}/{month}/{year}'
            with open('data_base.json', 'w') as f:
                json.dump(data, f)
            bot.send_message(call.message.chat.id, text=f"Дата окончания подписки изменена на {day}/{month}/{year}", reply_markup=main_reply_keyboard())
    if 'server' in call.data:
        add_user(call)


def add_server(message):
    ip = message.text
    # tern data_base.json into dict in the variable data
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    data['data']['servers'].append({'server_ip': ip, 'users': []})
    # save data to data_base.json
    with open('data_base.json', 'w') as f:
        json.dump(data, f)
    bot.send_message(message.chat.id, text='Сервер добавлен!')
    bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())


# when user chose server from inline keyboard read the next message and split it into name and dates and write it into data_base.json
def add_user(call):
    server_ip = call.data.split('_')[1]
    #get chat id from call
    user_id = call.message.chat.id
    bot.send_message(user_id, text='Введите имя пользователя:', reply_markup=cancel_reply_keyboard())
    # tern data_base.json into dict in the variable data
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    # find server_id in data['data']['servers'] and save it to server_index
    server_index = 0
    for i in range(len(data['data']['servers'])):
        if data['data']['servers'][i]['server_ip'] == server_ip:
            server_index = i
    call.data = ""
    bot.register_next_step_handler(call.message, add_user_name, server_index)


def add_user_name(message, server_id):
    name = message.text
    bot.send_message(message.chat.id, text='Введите дату начала и конца подписки в формате "10/10/2010 10/11/2010"', reply_markup=cancel_reply_keyboard())
    bot.register_next_step_handler(message, add_user_date, name, server_id)


def add_user_date(message, name, server_id):
    date = message.text.split(' ')
    if check_if_date_is_real(date[0]) and check_if_date_is_real(date[1]):
        bot.send_message(message.chat.id, text='Дата добавлена!')
        bot.send_message(message.chat.id, text='Выберите одну из кнопок ниже.', reply_markup=main_reply_keyboard())
        # tern data_base.json into dict in the variable data
        with open('data_base.json', 'r') as f:
            data = json.load(f)
        data['data']['servers'][server_id]['users'].append({'user_name': name, 'start_trail': date[0], 'end_trail': date[1]})
        # save data to data_base.json
        with open('data_base.json', 'w') as f:
            json.dump(data, f)


# check if text could be terned into date
def check_if_date_is_real(text_date):
    try:
        datetime.strptime(text_date, '%d/%m/%Y')
        return True
    except ValueError:
        return False


bot.infinity_polling()










