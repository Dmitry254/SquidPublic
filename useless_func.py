

def get_buses():
    global buses_notice_list
    for page in range(0, 5):
        url = f"https://marketplace.biswap.org/back/offers/sellings?" \
              f"sortBy=newest&page={page}&filter=none"
        data = get_data(url)['data']
        for nft in data:
            try:
                if nft['currency'] == 'BSW':
                    if "Bus" in nft['nft']['metadata']['name']:
                        bus_nft_id = nft['nft_id']
                        bus_level = nft['nft']['metadata']['attributes'][1]['value']
                        bus_price = float(nft['price']) / price_coeff
                        text, buses_notice_list = sort_buses(bus_nft_id, bus_level, bus_price, buses_notice_list)
                        if text:
                            link = f"https://marketplace.biswap.org/card/{nft['nft_contract']}/{bus_nft_id}"
                            text = f"{text}\n{link}"
                            # send_text_message(message, text)
                            print(text)
            except KeyError:
                continue


def get_players():
    global players_notice_list
    for page in range(0, 5):
        url = f"https://marketplace.biswap.org/back/offers/sellings?" \
              f"sortBy=newest&page={page}&filter=none"
        data = get_data(url)['data']
        for nft in data:
            try:
                if nft['currency'] == 'BSW':
                    if "Player" in nft['nft']['metadata']['name']:
                        player_nft_id = nft['nft_id']
                        player_energy = int(nft['nft']['metadata']['attributes'][1]['value'].split('/')[0])
                        player_price = float(nft['price']) / price_coeff
                        text, players_notice_list = sort_players(player_nft_id, player_energy, player_price, players_notice_list)
                        if text:
                            link = f"https://marketplace.biswap.org/card/{nft['nft_contract']}/{player_nft_id}"
                            text = f"{text}\n{link}"
                            # send_text_message(message, text)
                            print(text)
            except KeyError:
                continue


def get_transactions_web3(web3, contract, contract_address):
    global transactions_from_web3_list, null_transactions_from_web3_list
    latest_block = web3.eth.blockNumber
    block = web3.eth.getBlock(latest_block, True)
    for j in range(0, len(block.transactions)):
        if block.transactions[j].to == contract_address:
            if "b00ed7e367" in block.transactions[j].input\
            or "6d57712416" in block.transactions[j].input:
                if len(block.transactions[j].input) > 80:
                    if block.transactions[j].input[73] == "0":
                        func_obj, func_params = contract.decode_function_input(block.transactions[j].input)
                        tx_hash = block.transactions[j].hash.hex()
                        func_params['hash'] = tx_hash
                        nft_data = {}
                        nft_data_collected = False
                        if func_params not in transactions_from_web3_list:
                            nft_data = get_nft_data(func_params)
                            nft_data_collected = True
                        if nft_data:
                            transactions_from_web3_list.append(func_params)
                            if len(transactions_from_web3_list) > 30:
                                transactions_from_web3_list.pop(0)
                            if func_params in null_transactions_from_web3_list:
                                null_transactions_from_web3_list.remove(func_params)
                            get_buses_and_players(nft_data, func_params)
                        else:
                            if nft_data_collected:
                                if func_params not in null_transactions_from_web3_list:
                                    null_transactions_from_web3_list.append(func_params)
