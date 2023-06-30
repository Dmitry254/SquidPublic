from base_func import post_data_no_timeout
from datetime import datetime, timedelta


def get_current_prices():
    start = True
    page = -1
    while start:
        page += 1
        print(page)
        url = f"https://marketplace.biswap.org/back/offers/sellings?sortBy=newest" \
              f"&page={page}"
        players_data = post_data_no_timeout(url)['data']
        datetime_object = datetime.strptime(players_data[0]['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if datetime_object < time_now:
            print(players_data)
            start = False
        if start:
            for player in players_data:
                player_energy = 0
                player_level = 0
                if player['currency'] == "BSW":
                    for attribute in player['nft']['metadata']['attributes']:
                        if attribute['key'] == 'SquidEnergy':
                            player_energy = int(attribute['value'].split('/')[0])
                        if attribute['key'] == 'Level':
                            player_level = int(attribute['value'][0])
                    player_id = player['nft_id']
                    player_price = float(player['price']) / price_coeff
                    sort_players(player_id, player_energy, player_level, player_price)


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


if __name__ == "__main__":
    buses_id_list = []
    player_id_list = []
    buses = {}
    players = {}
    price_coeff = 1000000000000000000
    delta_days = 2
    delta_hours = 0
    delta_minutes = 0
    time_now = datetime.now() - timedelta(days=delta_days, hours=3 + delta_hours, minutes=delta_minutes)

    get_current_prices()
    print(players)
