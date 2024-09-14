import random

import requests
import json
import time

def generate_wallets(num_nodes):
    wallets = []
    for i in range(0, num_nodes):
        response = requests.get(f"http://localhost:800{i}/wallet/")
        wallet = response.json()
        wallets.append(wallet)
    return wallets

def register_peers(num_nodes):
    for i in range(0, num_nodes ):
        peers = [f"http://localhost:800{j}" for j in range(0, num_nodes) if j != i]
        data = {"peers": peers}
        response = requests.post(f"http://localhost:800{i}/peers/register/", json=data)
        print(response.content)

def create_and_submit_transaction(sender_wallet, receiver_wallet):
    transaction_data = {
        "sender_public_key": sender_wallet["public_key"],
        "receiver_public_key": receiver_wallet["public_key"],
        "amount": 10.0
    }
    response = requests.post(f"http://localhost:8001/transaction/sign/", json={"private_key": sender_wallet["private_key"], "transaction_data": transaction_data})
    signature = response.json()["signature"]

    data = {
        "sender_public_key": sender_wallet["public_key"],
        "receiver_public_key": receiver_wallet["public_key"],
        "amount": random.randrange(1,50),
        "signature": signature
    }
    response = requests.post(f"http://localhost:8001/transaction/new/", json=data)
    print(response.content)

def mine_transaction(miner_wallet):
    data = {"miner_address": miner_wallet["public_key"]}
    response = requests.post(f"http://localhost:8001/mine/", json=data)
    print(response.content)


def trigger_consensus(num_nodes):
    for i in range(0, num_nodes ):
        response = requests.get(f"http://localhost:800{i}/consensus/")
        print(response.content)
    print("Consensus achieved. All chains are identical.")



num_nodes = 4
wallets = generate_wallets(num_nodes)
print(len(wallets))
register_peers(num_nodes)
create_and_submit_transaction(wallets[0], wallets[1])
mine_transaction(wallets[1])
trigger_consensus(num_nodes)
