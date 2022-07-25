import json
from datetime import datetime, timedelta
from time import sleep

import telebot

from KEY import TOKEN

API_TOKEN = f'{TOKEN}'

bot = telebot.TeleBot(API_TOKEN)


def check_if_trail_ended():
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    text =''
    for server in data['data']['servers']:
        for user in server['users']:
            end_trail = datetime.strptime(user['end_trail'], '%d/%m/%Y')
            if end_trail < datetime.now():
                text += f'У {user["user_name"]} закончилась подписка на сервере {server["server_ip"]}\n'
    return text


def check_five_day_to_end_trail():
    with open('data_base.json', 'r') as f:
        data = json.load(f)
    text = ''
    for server in data['data']['servers']:
        for user in server['users']:
            end_trail = datetime.strptime(user['end_trail'], '%d/%m/%Y')
            # check if end_trail - datetime.now() < 5 days
            if end_trail - datetime.now() < timedelta(days=5) and end_trail - datetime.now() > timedelta(days=0):
                text += f'У {user["user_name"]} осталось {(end_trail - datetime.now()).days} дней до окончания подписки на сервере {server["server_ip"]}\n'
    return text

with open('data_base.json', 'r') as f:
    data = json.load(f)

while True:
    text = check_if_trail_ended()
    if text:
        for user in data['data']['users']:
            bot.send_message(user['user_id'], text)
    text = check_five_day_to_end_trail()
    if text:
        for user in data['data']['users']:
            bot.send_message(user['user_id'], text)
    print('Проверка завершена')
    sleep(60 * 60 * 24)  # Проверяем каждый день
    print('Проверка началась')

