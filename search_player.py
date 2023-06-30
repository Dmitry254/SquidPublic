import traceback
import time
import openpyxl
from threading import Thread, current_thread
from json import JSONDecodeError

from datetime import datetime, timedelta

import requests

from base_func import get_data, post_data_no_timeout
# from tg_bot import message, send_text_message
from web3_transactions import set_http_web3, send_accept_transaction


def get_players():
    global players_notice_list
    for page in range(0, 5):
        url = f"https://marketplace.biswap.org/back/offers/sellings?sortBy=newest" \
              f"&page={page}"
        players = post_data_no_timeout(url)['data']
        for player in players:
            try:
                player_energy = 0
                player_level = 0
                if player['currency'] == "BSW":
                    for attribute in player['nft']['metadata']['attributes']:
                        if attribute['key'] == 'SquidEnergy':
                            player_energy = int(attribute['value'].split('/')[0])
                        if attribute['key'] == 'Level':
                            player_level = int(attribute['value'][0])
                    player_price = float(player['price']) / price_coeff
                    notice_list = [player_energy, player_level, player_price]
                    if notice_list not in players_notice_list:
                        players_notice_list.append(notice_list)
                        if player_energy >= searching_player_energy and player_level >= searching_player_level \
                            and player_price <= searching_player_price:
                            link = f"https://marketplace.biswap.org/card/{player['nft']['token_address']}/{player['nft_id']}"
                            text = f"Energy {player_energy}, price {player_price}, level {player_level}, {link}"
                            print(text)
                            offer_id = f"00000000000000000000000000000000000000000000000000000000000{hex(player['offer_id'])[2:]}"
                            # buy_nft(web3, offer_id, 1)
                            # send_text_message(message, text)
            except KeyError:
                continue
            except:
                traceback.print_exc()
                continue


def buy_nft(web3, offer_id, gas_price):
    accept_text = send_accept_transaction(web3, offer_id, gas_price)
    return accept_text


if __name__ == "__main__":
    web3 = set_http_web3()
    players_notice_list = []
    price_coeff = 1000000000000000000
    searching_player_energy = 1000
    searching_player_level = 2
    searching_player_price = 25
    while True:
        get_players()
        time.sleep(5)
