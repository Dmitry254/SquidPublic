import json
import traceback
import time
from json import JSONDecodeError
import random

import requests
import telebot  # pip install PyTelegramBotAPI
from threading import Thread
from datetime import datetime, timedelta

from web3_transactions import sell_nft

api_key_tg = ""
bot = telebot.TeleBot(api_key_tg)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        bot.send_message(message.chat.id, "Что делаем?")
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['test'])
def start_message(message):
    try:
        bot.send_message(message.chat.id, "Я жив")
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['close'])
def start_message(message):
    global closed
    try:
        if message.chat.id == admin:
            if closed:
                closed = False
                bot.send_message(message.chat.id, "Открыто")
            elif not closed:
                closed = True
                bot.send_message(message.chat.id, "Закрыто")
        else:
            bot.send_message(message.chat.id, "Нет доступа")
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['sell'])
def start_message(message):
    try:
        print(message.text)
        sell_text = sell_nft(message.text[6:])
        bot.send_message(message.chat.id, sell_text)
    except:
        traceback.print_exc()
        pass


def send_text_message(message, text):
    for mes in message:
        if not closed:
            bot.send_message(mes, text, parse_mode='Markdown')
        else:
            if mes == admin:
                bot.send_message(mes, text, parse_mode='Markdown')


def send_text_message_with_callback(message, text, nft_data, nft_price):
    side = "0000000000000000000000000000000000000000000000000000000000000000"
    dealToken = "000000000000000000000000965f527d9159dce6288a2219db51fc6eef120dd1"
    nft = f"000000000000000000000000{nft_data['token_address'][2:]}"
    token_id = hex(int(nft_data['token_id']))[2:]
    tokenId = f"{(64 - len(token_id)) * '0'}{token_id}"
    nft_price = hex(nft_price * 1000000000000000000)[2:]
    price = f"{(64 - len(nft_price)) * '0'}{nft_price}"
    data = "0x2f45f872" + side + dealToken + nft + tokenId + price
    print(type(data), data)
    key = telebot.types.InlineKeyboardMarkup()
    but_1 = telebot.types.InlineKeyboardButton(text="Продать", callback_data=data)
    key.add(but_1)
    for mes in message:
        if not closed:
            bot.send_message(mes, text, parse_mode='Markdown', reply_markup=key)
        else:
            if mes == admin:
                bot.send_message(mes, text, parse_mode='Markdown', reply_markup=key)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data:
        data = call.data
        print(data)
        # text = sell_nft(data)
        # print(text)
        # send_text_message(message, text)
    call.answer_callback_query()


def bot_polling():
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        traceback.print_exc()
        time.sleep(60)


op = Thread(target=bot_polling, args=())
op.start()

closed = True
message = []
admin = 0
