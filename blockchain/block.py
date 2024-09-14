import time
import hashlib
from typing import List


class Block:
    def __init__(self, index: int, transactions: List[dict], timestamp: float, previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = str(self.index) + str(self.transactions) + str(self.timestamp) + \
                       str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()
