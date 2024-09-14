from blockchain.blockchain import Blockchain
from wallet.transaction import Transaction
from wallet.wallet import verify_transaction
from typing import List
import requests
import json

from blockchain.block import Block


class Node:
    def __init__(self):
        self.blockchain = Blockchain()
        self.peers: List[str] = []

    def add_transaction(self, transaction: Transaction):
        transaction_data = {
            "sender_public_key": transaction.sender_public_key,
            "receiver_public_key": transaction.receiver_public_key,
            "amount": transaction.amount
        }
        message = json.dumps(transaction_data, sort_keys=True, separators=(',', ':'))
        is_valid = verify_transaction(
            transaction.sender_public_key,
            message,
            transaction.signature
        )
        if is_valid:
            self.blockchain.add_new_transaction(transaction.dict())
            return True
        else:
            return False

    def mine_block(self, miner_address: str):
        block = self.blockchain.mine(miner_address)
        if block:
            self.broadcast_block(block)
            return True
        else:
            return False

    def register_peer(self, peer_url: str):
        if peer_url not in self.peers:
            self.peers.append(peer_url)

    def consensus(self):
        longest_chain = None
        current_len = len(self.blockchain.chain)

        for peer in self.peers:
            try:
                response = requests.get(f'{peer}/chain/')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain_data = response.json()['chain']
                    chain = []

                    for block_data in chain_data:
                        block = Block(
                            index=block_data['index'],
                            transactions=block_data['transactions'],
                            timestamp=block_data['timestamp'],
                            previous_hash=block_data['previous_hash'],
                            nonce=block_data['nonce']
                        )
                        block.hash = block_data['hash']
                        chain.append(block)

                    if length > current_len and self.blockchain.is_valid_chain(chain):
                        current_len = length
                        longest_chain = chain
            except requests.exceptions.RequestException:
                continue

        if longest_chain:
            self.blockchain.chain = longest_chain
            return True

        return False

    def broadcast_block(self, block: Block):
        for peer in self.peers:
            url = f'{peer}/block/receive/'
            block_data = {
                "index": block.index,
                "transactions": block.transactions,
                "timestamp": block.timestamp,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "hash": block.hash
            }
            try:
                requests.post(url, json=block_data)
            except requests.exceptions.RequestException:
                continue
