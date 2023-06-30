import traceback
import time
import openpyxl
from threading import Thread, current_thread
from json import JSONDecodeError

from datetime import datetime, timedelta

import requests
from web3.exceptions import TransactionNotFound

from google_sheets import get_google_sheet_data, spreadsheet_id, CREDENTIALS_FILE
from base_func import get_data
from web3_transactions import set_http_web3, get_transactions_list, get_transaction_data, get_nft_data, contract_address, \
    get_contract, get_offer_id, send_accept_transaction, get_bsw_balance


from tg_bot1 import message, send_text_message, send_text_message_with_callback


def get_pending_transactions(web3, contract):
    eventlist = myfilter.get_new_entries()
    from_func = "pending_trans"
    if eventlist:
        for event in eventlist:
            if event['args']['side'] == 0:
                if "b00ED7E367" in event['args']['nft'] or "6d57712416" in event['args']['nft']:
                    if event['args']['dealToken'] == "0x965F527D9159dCe6288a2219DB51fc6Eef120dD1":
                        offer_id = event['args']['id']
                        func_params = {'tokenId': event['args']['tokenId'], 'price': event['args']['price'],
                                       'nft': event['args']['nft'], 'offer_id': offer_id}
                        nft_data = {}
                        nft_data_collected = False
                        if func_params not in transactions_from_web3_list:
                            # nft_data = get_nft_data(func_params)
                            if func_params['nft'] == "0xb00ED7E3671Af2675c551a1C26Ffdcc5b425359b":
                                url = f"https://marketplace.biswap.org/back/metadata/fetch?url=https://squid-nft.io/back/metadata/player/{func_params['tokenId']}"
                            else:
                                url = f"https://marketplace.biswap.org/back/metadata/fetch?url=https://squid-nft.io/back/metadata/bus/{func_params['tokenId']}"
                            nft_metadata = get_data(url)
                            if nft_metadata:
                                nft_data['metadata'] = nft_metadata
                                nft_data['token_id'] = func_params['tokenId']
                                nft_data['token_address'] = func_params['nft']
                            nft_data_collected = True
                        if nft_data:
                            transactions_from_web3_list.append(func_params)
                            if len(transactions_from_web3_list) > 30:
                                transactions_from_web3_list.pop(0)
                            if func_params in null_transactions_from_web3_list:
                                null_transactions_from_web3_list.remove(func_params)
                            get_buses_and_players(nft_data, func_params, from_func)
                        else:
                            if nft_data_collected:
                                if func_params not in null_transactions_from_web3_list:
                                    null_transactions_from_web3_list.append(func_params)


def get_buses_and_players(nft, func_params, from_func):
    global buses_notice_list, players_notice_list, parsed_transactions_list
    offer_id = func_params['offer_id']
    try:
        if "Bus" in nft['metadata']['name']:
            bus_nft_id = func_params['tokenId']
            bus_level = nft['metadata']['attributes'][1]['value']
            bus_price = float(func_params['price']) / price_coeff
            text, buses_notice_list, gas_price, nft_price = sort_buses(bus_nft_id, bus_level, bus_price, buses_notice_list)
            if text:
                link = f"https://marketplace.biswap.org/card/{nft['token_address']}/{bus_nft_id}"
                text = f"{text}\n{link}"
                account_balance = get_bsw_balance(web3)
                if account_balance < bus_price:
                    text = f"{text}\nНа балансе только {account_balance}"
                    send_text_message(message, text)
                    print(text)
                    return text
                if from_func == "nulls_list":
                    gas_price = 0
                print(offer_id, accept_trans_list)
                if str(offer_id) not in accept_trans_list:
                    buy_nft_start(web3, offer_id, gas_price, text, nft, nft_price, from_func)
                else:
                    print("Уже была транзакция")
                print(web3.eth.blockNumber, datetime.now())
                print(from_func)
                print(text)
        if "Player" in nft['metadata']['name']:
            print(nft)
            player_energy = None
            player_level = None
            player_nft_id = func_params['tokenId']
            for attribute in nft['metadata']['attributes']:
                if attribute['key'] == 'SquidEnergy':
                    player_energy = int(attribute['value'].split('/')[0])
                if attribute['key'] == 'Level':
                    player_level = int(attribute['value'][0])
            player_price = float(func_params['price']) / price_coeff
            text, players_notice_list, gas_price, nft_price = sort_players(player_nft_id, player_energy, player_level, player_price,
                                                     players_notice_list)
            if text:
                link = f"https://marketplace.biswap.org/card/{nft['token_address']}/{player_nft_id}"
                text = f"{text}\n{link}"
                account_balance = get_bsw_balance(web3)
                if account_balance < player_price:
                    text = f"{text}\nНа балансе только {account_balance}"
                    send_text_message(message, text)
                    print(text)
                    return text
                if from_func == "nulls_list":
                    gas_price = 0
                print(offer_id, accept_trans_list)
                if str(offer_id) not in accept_trans_list:
                    buy_nft_start(web3, offer_id, gas_price, text, nft, nft_price, from_func)
                else:
                    print("Уже была транзакция")
                print(web3.eth.blockNumber, datetime.now())
                print(from_func)
                print(text)
    except KeyError:
        print("Неверные данные")


def buy_nft_start(web3, offer_id, gas_price, text, nft, nft_price, from_func):
    buy_nft_text = buy_nft(web3, offer_id, gas_price)
    text = f"{text}\n{buy_nft_text}\n"
    send_text_message(message, text)
    sell_data = create_sell_data(nft, nft_price)
    send_text_message(message, sell_data)


def create_sell_data(nft_data, nft_price):
    side = "0000000000000000000000000000000000000000000000000000000000000000"
    dealToken = "000000000000000000000000965f527d9159dce6288a2219db51fc6eef120dd1"
    nft = f"000000000000000000000000{nft_data['token_address'][2:]}"
    token_id = hex(int(nft_data['token_id']))[2:]
    tokenId = f"{(64 - len(token_id)) * '0'}{token_id}"
    nft_price = hex(nft_price * price_coeff)[2:]
    price = f"{(64 - len(nft_price)) * '0'}{nft_price}"
    sell_data = "0x2f45f872" + side + dealToken + nft + tokenId + price
    return sell_data


def buy_nft(web3, offer_id, gas_price):
    offer_id = f"00000000000000000000000000000000000000000000000000000000000{hex(offer_id)[2:]}"
    accept_text = send_accept_transaction(web3, offer_id, gas_price)
    return accept_text


def calculate_gas_price(dict_buy_price, nft_price):
    gas_price = 0
    additional_profit = dict_buy_price - nft_price
    if additional_profit > 12:
        gas_price = 30000000000
        return gas_price
    elif additional_profit > 10:
        gas_price = 25000000000
        return gas_price
    elif additional_profit > 8:
        gas_price = 20000000000
        return gas_price
    elif additional_profit > 6:
        gas_price = 15000000000
        return gas_price
    elif additional_profit > 4:
        gas_price = 10000000000
        return gas_price
    elif additional_profit > 2:
        gas_price = 5000000000
        return gas_price
    return gas_price


def get_nft_data_from_nulls_list():
    global null_transactions_from_web3_list
    from_func = "nulls_list"
    for func_params_in_list in null_transactions_from_web3_list:
        nft_data = get_nft_data(func_params_in_list)
        if nft_data:
            get_buses_and_players(nft_data, func_params_in_list, from_func)
            null_transactions_from_web3_list.remove(func_params_in_list)


def sort_buses(bus_nft_id, bus_level, bus_price, buses_notice_list):
    text = False
    gas_price = 0
    if bus_price <= buy_prices['Level ' + str(bus_level)]:
        text, buses_notice_list = create_text_buses(bus_nft_id, bus_level, bus_price, buses_notice_list)
        gas_price = calculate_gas_price(buy_prices['Level ' + str(bus_level)], bus_price)
    return text, buses_notice_list, gas_price, sell_prices['Level ' + str(bus_level)]


def sort_players(player_nft_id, player_energy, player_level, player_price, players_notice_list):
    text = False
    gas_price = 0
    if player_price <= buy_prices[f"Energy {player_energy // 100}00-{player_energy // 100 +1}00, level {player_level}"]:
        text, players_notice_list = create_text_players(player_nft_id, player_energy, player_level, player_price, players_notice_list)
        gas_price = calculate_gas_price(buy_prices[f"Energy {player_energy // 100}00-{player_energy // 100 +1}00, level {player_level}"], player_price)
    return text, players_notice_list, gas_price, sell_prices[f"Energy {player_energy // 100}00-{player_energy // 100 +1}00, level {player_level}"]


def create_text_buses(bus_nft_id, bus_level, bus_price, buses_notice_list):
    if bus_nft_id not in buses_notice_list:
        text = f"Level {bus_level}, price {bus_price} BSW"
        buses_notice_list.append(bus_nft_id)
        return text, buses_notice_list
    else:
        return False, buses_notice_list


def create_text_players(player_nft_id, player_energy, player_level, player_price, players_notice_list):
    if player_nft_id not in players_notice_list:
        text = f"Energy {player_energy}, level {player_level}, price {player_price} BSW"
        players_notice_list.append(player_nft_id)
        return text, players_notice_list
    else:
        return False, players_notice_list


def get_table_prices():
    buy_prices = {}
    sell_prices = {}
    bnb_price = float(get_google_sheet_data('B10')[0][0].replace(',', '.'))
    bsw_price = float(get_google_sheet_data('B11')[0][0].replace(',', '.'))
    taxes = float(get_google_sheet_data('B12')[0][0].replace(',', '.'))
    profit = float(get_google_sheet_data('B13')[0][0].replace(',', '.'))
    bus_range_data = 'A3:B7'
    bus_data = get_google_sheet_data(bus_range_data)
    player_range_data = 'E3:F57'
    player_data = get_google_sheet_data(player_range_data)
    for bus_price in bus_data:
        buy_prices[bus_price[0]] = float(bus_price[1].replace(',', '.')) * 0.98 - (
                    taxes * bnb_price / bsw_price + profit / bsw_price)
        sell_prices[bus_price[0]] = int(bus_price[1].replace(',', '.'))
    for player_price in player_data:
        buy_prices[player_price[0]] = float(player_price[1].replace(',', '.')) * 0.98 - (
                    taxes * bnb_price / bsw_price + profit / bsw_price)
        sell_prices[player_price[0]] = int(player_price[1].replace(',', '.'))
    return buy_prices, sell_prices


def get_accept_trans():
    global accept_trans_list
    counter = 0
    web3 = set_http_web3("https://bsc-dataseed2.binance.org:443")
    contract = get_contract(web3, contract_address)
    my_filter = contract.events.AcceptOffer.createFilter(fromBlock="latest")
    while True:
        time.sleep(0.1)
        try:
            counter += 1
            if counter > 500:
                my_filter = contract.events.AcceptOffer.createFilter(fromBlock='latest', toBlock='pending')
                counter = 0
            eventlist = my_filter.get_new_entries()
            if eventlist:
                for event in eventlist:
                    accept_id = event.args.id
                    if accept_id not in accept_trans_list:
                        accept_trans_list.append(str(accept_id))
                        if len(accept_trans_list) > 10:
                            accept_trans_list.pop(0)
        except ValueError:
            # my_filter = contract.events.AcceptOffer.createFilter(fromBlock='latest', toBlock='pending')
            traceback.print_exc()
            time.sleep(60)
            continue
        except requests.exceptions.HTTPError:
            print("requests.exceptions.HTTPError")
            traceback.print_exc()
            print(datetime.now())
            my_filter = contract.events.AcceptOffer.createFilter(fromBlock='latest', toBlock='pending')
            continue
        except KeyError:
            print("KeyError")
            continue
        except:
            my_filter = contract.events.AcceptOffer.createFilter(fromBlock='latest', toBlock='pending')
            traceback.print_exc()
            continue


if __name__ == "__main__":
    price_coeff = 1000000000000000000
    buses_notice_list = []
    players_notice_list = []
    parsed_transactions_list = []
    transactions_from_web3_list = []
    null_transactions_from_web3_list = []
    accept_trans_list = []
    buy_prices, sell_prices = get_table_prices()
    web3 = set_http_web3()
    contract = get_contract(web3, contract_address)
    myfilter = contract.events.NewOffer.createFilter(fromBlock='latest', toBlock='pending')
    print(web3, contract)
    print(sell_prices)
    print(buy_prices)
    print("Старт")
    counter = 0
    accept_trans_thread = Thread(target=get_accept_trans)
    accept_trans_thread.start()
    while True:
        try:
            counter += 1
            if counter > 400:
                myfilter = contract.events.NewOffer.createFilter(fromBlock='latest', toBlock='pending')
                counter = 0
            # start_time = datetime.now()
            get_pending_transactions(web3, contract)
            get_nft_data_from_nulls_list()
            # print(datetime.now() - start_time)
            time.sleep(0.1)
        except ValueError:
            # myfilter = contract.events.NewOffer.createFilter(fromBlock='latest', toBlock='pending')
            continue
        except requests.exceptions.HTTPError:
            print("requests.exceptions.HTTPError")
            myfilter = contract.events.NewOffer.createFilter(fromBlock='latest', toBlock='pending')
            continue
        except KeyError:
            print("KeyError")
            continue
        except:
            myfilter = contract.events.NewOffer.createFilter(fromBlock='latest', toBlock='pending')
            traceback.print_exc()
            continue
