import time
import traceback

from base_func import get_data, get_data_no_timeout
from price_table import fill_table_buses, fill_table_players, fill_table_robi
from datetime import datetime, timedelta


def get_prices():
    global buses, players, robies
    buses = {}
    players = {}
    robies = {}
    start = True
    page = -1
    while start:
        page += 1
        print(page)
        url = f"https://marketplace.biswap.org/back/transactions/market?partner=all&sortBy=newest&page={page}"
        try:
            history = get_data_no_timeout(url)['data']
        except KeyError:
            time.sleep(5)
            history = get_data_no_timeout(url)['data']
        datetime_object = datetime.strptime(history[0]['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if datetime_object < time_now:
            start = False
        for deal in history:
            try:
                if deal['type'] == "buy":
                    if "Bus" in deal['nft']['metadata']['name']:
                        bus_level = deal['nft']['metadata']['attributes'][1]['value']
                        bus_price = None
                        bus_id = None
                        for log in deal['logs']:
                            if log['name'] == "AcceptOffer":
                                bus_price = float(log['params']['price']) / price_coeff
                                bus_id = log['params']['id']
                        if not bus_price:
                            continue
                        buses = sort_buses(bus_id, bus_level, bus_price)
                    if "Player" in deal['nft']['metadata']['name']:
                        player_energy = None
                        player_level = None
                        player_price = None
                        player_id = None
                        for attribute in deal['nft']['metadata']['attributes']:
                            if attribute['key'] == 'SquidEnergy':
                                player_energy = int(attribute['value'].split('/')[0])
                            if attribute['key'] == 'Level':
                                player_level = int(attribute['value'][0])
                        for log in deal['logs']:
                            if log['name'] == "AcceptOffer":
                                player_price = float(log['params']['price']) / price_coeff
                                player_id = log['params']['id']
                        if not player_price or not player_energy or not player_level:
                            continue
                        players = sort_players(player_id, player_energy, player_level, player_price)
                    if "Robi" in deal['nft']['metadata']['name']:
                        robi_energy = int(deal['nft']['metadata']['attributes'][3]['value'].split('/')[0])
                        robi_level = int(deal['nft']['metadata']['attributes'][4]['value'])
                        robi_price = None
                        robi_id = None
                        for log in deal['logs']:
                            if log['name'] == "AcceptOffer":
                                robi_price = float(log['params']['price']) / price_coeff
                                robi_id = log['params']['id']
                        if not robi_price:
                            continue
                        robies = sort_robi(robi_id, robi_energy, robi_level, robi_price)
            except:
                traceback.print_exc()
                continue
    return buses, players, robies


def sort_buses(bus_id, bus_level, bus_price):
    global buses_id_list
    if bus_id in buses_id_list:
        return buses
    buses_id_list.append(bus_id)
    list_name = 'bus' + str(bus_level)
    if list_name in buses.keys():
        buses[list_name].append(bus_price)
    else:
        buses[list_name] = []
        buses[list_name].append(bus_price)
    return buses


def sort_players(player_id, player_energy, player_level, player_price):
    global player_id_list
    if player_id in player_id_list:
        return players
    player_id_list.append(player_id)
    list_index = player_energy // 100
    list_name = str(player_level) + 'player' + str(list_index)
    if list_name in players.keys():
        players[list_name].append(player_price)
    else:
        players[list_name] = []
        players[list_name].append(player_price)
    return players


def sort_robi(robi_id, robi_energy, robi_level, robi_price):
    global robi_id_list
    if robi_id in robi_id_list:
        return robies
    robi_id_list.append(robi_id)
    list_name = 'robi' + str(robi_level)
    if list_name in robies.keys():
        robies[list_name].append(f"{robi_price}/{robi_energy}")
    else:
        robies[list_name] = []
        robies[list_name].append(robi_price)
    return robies


def create_text_buses(buses):
    text = ""
    for level in range(0, 7):
        list_name = 'bus' + str(level)
        if list_name in buses.keys():
            text += f"Level {level}\n{buses[list_name]}\n{sorted(buses[list_name])}\n"
        else:
            continue
    return text


def create_text_players(players):
    text = ""
    for level in range(0, 40):
        list_name = 'player' + str(level)
        if list_name in players.keys():
            text += f"Energy {level}00-{level+1}00\n{players[list_name]}\n{sorted(players[list_name])}\n"
        else:
            continue
    return text


if __name__ == "__main__":
    buses_id_list = []
    player_id_list = []
    robi_id_list = []
    delta_hours = 8
    delta_minutes = 0
    time_now = datetime.now() - timedelta(hours=3+delta_hours, minutes=delta_minutes)
    price_coeff = 1000000000000000000
    buses, players, robies = get_prices()
    buses_text = create_text_buses(buses)
    players_text = create_text_players(players)
    fill_table_buses(buses)
    fill_table_players(players)
    fill_table_robi(robies)
