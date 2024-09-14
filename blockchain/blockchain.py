from blockchain.block import Block
import time
from typing import List, Optional


class Blockchain:
    difficulty = 1

    def __init__(self):
        self.chain: List[Block] = []
        self.unconfirmed_transactions: List[dict] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_new_transaction(self, transaction: dict):
        self.unconfirmed_transactions.append(transaction)

    def proof_of_work(self, block: Block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block: Block, proof: str):
        previous_hash = self.get_last_block().hash
        if self.get_last_block().index != 0:
            if previous_hash != block.previous_hash:
                print("Previous hash does not match.")
                return False
        if self.get_last_block().index + 1 != block.index:
            print("Index does not match.")
            return False
        if not self.is_valid_proof(block, proof):
            print("Proof of work is invalid.")
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block: Block, block_hash: str):
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())

    def is_valid_chain(self, chain: List[Block]):
        previous_hash = "0"
        for block in chain:
            if block.previous_hash != previous_hash:
                return False
            if not self.is_valid_proof(block, block.hash):
                return False
            previous_hash = block.hash
        return True

    def replace_chain(self, new_chain: List[Block]):
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            self.chain = new_chain
            return True
        return False

    def mine(self, miner_address: str) -> Optional[Block]:
        if not self.unconfirmed_transactions:
            return None
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions.copy(),
            timestamp=time.time(),
            previous_hash=last_block.hash
        )
        proof = self.proof_of_work(new_block)
        added = self.add_block(new_block, proof)
        if added:
            self.unconfirmed_transactions = []
            reward_transaction = {
                "sender_public_key": "network",
                "receiver_public_key": miner_address,
                "amount": 25.0,
                "signature": ""
            }
            self.add_new_transaction(reward_transaction)
            return new_block
        else:
            return None
