import time
import traceback

import json
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware


private_key = ""
my_address = ""
contract_address = ""
bsc_scan_api = ""

quick_node = ""
infura = ""
bsc = ""
bsc_wss = ""
moralis = ""


def set_http_web3(bsc=bsc):
    web3 = Web3(Web3.HTTPProvider(bsc))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3


def set_wss_web3():
    web3 = Web3(Web3.WebsocketProvider(bsc_wss, websocket_timeout=360, websocket_kwargs={"max_size": 650000000}))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3


def get_transactions_list(contract_address):
    transactions_list = []
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={contract_address}&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey={bsc_scan_api}"
    transactions_info = get_data(url)['result']
    for trans in transactions_info:
        if len(trans['input']) > 80:
            transactions_list.append(trans['hash'])
    return transactions_list


def get_transaction_data(web3, contract, transaction_hash):
    transaction = web3.eth.getTransaction(transaction_hash)
    func_obj, func_params = contract.decode_function_input(transaction["input"])
    return func_obj, func_params


def get_nft_data(func_params):
    info_link = f"https://marketplace.biswap.org/back/card/{func_params['nft']}/{func_params['tokenId']}?userAddress=no"
    data = get_data(info_link)
    return data


def parse_contract():
    nft_data_list = []
    web3 = set_http_web3()
    transactions_list = get_transactions_list(contract_address)
    for transaction_hash in transactions_list:
        func_obj, func_params = get_transaction_data(web3, transaction_hash)
        nft_data = get_nft_data(func_params)
        nft_data['price'] = func_params['price']
        nft_data['nft_id'] = func_params['tokenId']
        nft_data_list.append(nft_data)
    return nft_data_list


def get_transactions_web3(web3, contract, contract_address):
    global transactions_from_web3_list, null_transactions_from_web3_list
    latest_block = web3.eth.blockNumber
    for i in range(0, 3):
        block = web3.eth.getBlock(latest_block - i, True)
        print(latest_block - i)
        for j in range(0, len(block.transactions)):
            if block.transactions[j].to == contract_address:
                if "b00ed7e367" in block.transactions[j].input \
                        or "6d57712416" in block.transactions[j].input:
                    if len(block.transactions[j].input) > 80:
                        func_obj, func_params = contract.decode_function_input(block.transactions[j].input)
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
                        else:
                            if nft_data_collected:
                                if func_params not in null_transactions_from_web3_list:
                                    null_transactions_from_web3_list.append(func_params)


def get_nft_data_from_nulls_list():
    global null_transactions_from_web3_list
    for func_params_in_list in null_transactions_from_web3_list:
        nft_data = get_nft_data(func_params_in_list)
        if nft_data:
            null_transactions_from_web3_list.remove(func_params_in_list)


def get_contract(web3, contract_address):
    abi_endpoint = f"https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={bsc_scan_api}"
    abi = json.loads(requests.get(abi_endpoint).text)
    contract = web3.eth.contract(contract_address, abi=abi["result"])
    return contract


def get_accept_transaction(web3, contract_address):
    latest_block = web3.eth.blockNumber
    block = web3.eth.getBlock(latest_block, True)
    for j in range(0, len(block.transactions)):
        if block.transactions[j].to == contract_address:
            if len(block.transactions[j].input) < 80:
                print(block.transactions[j].input)
                func_obj, func_params = contract.decode_function_input(block.transactions[j].input)
                print(func_obj)
                print(func_params)
                print("--------")


def get_offer_id(web3, transaction_hash):
    receipt = web3.eth.get_transaction_receipt(transaction_hash)
    offer_id = receipt.logs[0].data[-64:]
    # offer_id = decode_abi(['address', 'uint256', 'uint8', 'uint256'], decode_hex(receipt.logs[0].data))[3]
    return offer_id


def send_accept_transaction(web3, offer_id, gas_price):
    if web3.eth.gas_price > 10000000000:
        text = "Слишком высокая цена газа"
        return text
    try:
        tx_data = {'to': contract_address, 'from': my_address, 'data': f"0x19b05f49{offer_id}",
                   'gas': 500000, 'gasPrice': gas_price + 5500000000, 'nonce': web3.eth.get_transaction_count(my_address)}
        sign_tx = web3.eth.account.sign_transaction(tx_data, private_key=private_key)
        web3.eth.send_raw_transaction(sign_tx.rawTransaction)
        text = "Транзакция успешно отправлена"
        return text
    except:
        error = traceback.format_exc()
        return error


def send_sell_offer_transaction(web3, nft_data, nft_price):
    if nft_data:
        side = "0000000000000000000000000000000000000000000000000000000000000000"
        dealToken = "000000000000000000000000965f527d9159dce6288a2219db51fc6eef120dd1"
        nft = f"000000000000000000000000{nft_data['token_address'][2:]}"
        token_id = hex(int(nft_data['token_id']))[2:]
        tokenId = f"{(64 - len(token_id)) * '0'}{token_id}"
        nft_price = hex(nft_price * price_coeff)[2:]
        price = f"{(64 - len(nft_price)) * '0'}{nft_price}"
        if web3.eth.gas_price > 7000000000:
            text = "Слишком высокая цена газа"
            return text
        try:
            tx_data = {'to': contract_address, 'from': my_address, 'data': "0x2f45f872" + side + dealToken + nft + tokenId + price,
                       'gas': 300000, 'gasPrice': web3.eth.gas_price, 'nonce': web3.eth.get_transaction_count(my_address)}
            sign_tx = web3.eth.account.sign_transaction(tx_data, private_key=private_key)
            web3.eth.send_raw_transaction(sign_tx.rawTransaction)
            text = "Транзакция успешно отправлена"
            return text
        except:
            error = traceback.format_exc()
            return error
    else:
        text = "Попробуй позже"
        return text


def send_sell_offer_transaction_with_data(web3, data):
    if web3.eth.gas_price > 7000000000:
        text = "Слишком высокая цена газа"
        return text
    try:
        tx_data = {'to': contract_address, 'from': my_address, 'data': data,
                   'gas': 300000, 'gasPrice': web3.eth.gas_price, 'nonce': web3.eth.get_transaction_count(my_address)}
        sign_tx = web3.eth.account.sign_transaction(tx_data, private_key=private_key)
        web3.eth.send_raw_transaction(sign_tx.rawTransaction)
        text = "Транзакция успешно отправлена"
        return text
    except:
        error = traceback.format_exc()
        return error


def sell_nft(data):
    web3 = set_http_web3()
    text = send_sell_offer_transaction_with_data(web3, data)
    return text


def get_bsw_balance(web3):
    minABI = [{'constant': True, 'inputs': [{'name': "_owner", 'type': "address"}], 'name': "balanceOf",
               'outputs': [{'name': "balance", 'type': "uint256"}], 'type': "function"}]
    tokenAddress = Web3.toChecksumAddress("")
    bsw_contract = web3.eth.contract(tokenAddress, abi=minABI)
    result = bsw_contract.functions.balanceOf(my_address).call() / 1000000000000000000
    return result


def get_pending_transactions(web3, contract):
    myfilter = contract.events.NewOffer.createFilter(fromBlock="latest")
    eventlist = myfilter.get_all_entries()
    if eventlist:
        for event in eventlist:
            if event['args']['side'] == 0:
                hash = event['transactionHash'].hex()
                func_params = event['args']
                offer_id = f"00000000000000000000000000000000000000000000000000000000000{hex(event['args']['id'])[2:]}"
                nft_data = get_nft_data(func_params)
                text = f"https://bscscan.com/tx/{hash}"
                print(datetime.now(), hash, 1, web3.eth.get_block_number())
                # print(datetime.now(), web3.eth.get_block_number(), event['blockNumber'])


def get_not_confirmed_transactions(web3, contract):
    options = {'fromBlock': 'latest', 'toBlock': 'pending', 'address': contract_address}
    tx_filter = web3.eth.filter('pending')
    tx_filter = contract.events.NewOffer.createFilter(fromBlock='latest', toBlock='pending')
    print(web3.eth.is_mining())
    print(web3.eth.blockNumber)
    print(web3.eth.getBlock('latest'))
    print(web3.eth.getBlock('pending'))
    while True:
        event_list = tx_filter.get_new_entries()
        if event_list:
            print(event_list)
            for event in event_list:
                transaction_hash = event.transactionHash.hex()
                transaction = web3.eth.getTransaction(transaction_hash)
                print(datetime.now(), transaction_hash, 2, web3.eth.get_block_number())
            # print(web3.eth.get_block_number(), transaction.blockNumber)


def get_my_nft(web3):
    nft_list = []
    url = f"https://api.bscscan.com/api?module=account&action=tokennfttx" \
          f"&&address={my_address}&page=1&offset=100" \
          f"&startblock=0&endblock=999999999&sort=desc&apikey={bsc_scan_api}"
    data = get_data(url)
    print(data)
    for tx in data['result']:
        if tx['tokenID'] in nft_list:
            nft_list.remove(tx['tokenID'])
        else:
            nft_list.append(tx['tokenID'])
    print(nft_list)


def get_selling_nft():
    options = {'fromBlock': web3.eth.get_block_number()-4900, 'toBlock': 'latest', 'address': my_address}
    tx_filter = web3.eth.filter(options)
    print(tx_filter.get_all_entries())


def search_bot_transactions(web3, block_number, token_id):
    block = web3.eth.get_block(block_number, full_transactions=True)
    print(block)


def subscribe_pending_transactions():
    web3 = set_wss_web3()
    pool = web3.geth.admin.datadir()
    print(pool)


if __name__ == "__main__":
    # nft_data_list = []
    # transactions_from_web3_list = []
    # null_transactions_from_web3_list = []
    price_coeff = 1000000000000000000
    web3 = set_http_web3()
    contract = get_contract(web3, contract_address)
    get_not_confirmed_transactions(web3, contract)
    # subscribe_pending_transactions()
    # while True:
    #     get_not_confirmed_transactions(web3, contract)
    #     get_pending_transactions(web3, contract)
    # my_account = web3.eth.account.from_key(private_key)
    # start_time = datetime.now()
    # get_bsw_balance(web3)
    # end_time = datetime.now()
    # print(end_time-start_time)
    # transaction_hash = ""
    # offer_id = get_offer_id(web3, transaction_hash)
    # send_accept_transaction(web3, offer_id)
    # while True:
    #     get_accept_transaction(web3, contract_address)
