from fastapi import FastAPI, Body
from wallet.wallet import generate_wallet, sign_transaction
from wallet.transaction import Transaction
from network.node import Node
from typing import List
from pydantic import BaseModel
from blockchain.block import Block


app = FastAPI()
node = Node()


@app.get("/wallet/")
def create_wallet():
    private_key, public_key = generate_wallet()
    return {
        "private_key": private_key,
        "public_key": public_key
    }


@app.post("/transaction/sign/")
def sign_transaction_endpoint(private_key: str = Body(...), transaction_data: dict = Body(...)):
    import json
    # Serialize transaction data consistently
    message = json.dumps(transaction_data, sort_keys=True, separators=(',', ':'))
    signature = sign_transaction(private_key, message)
    return {"signature": signature}


@app.post("/transaction/new/")
def new_transaction(transaction: Transaction):
    success = node.add_transaction(transaction)
    if success:
        return {"message": "Transaction added successfully."}
    else:
        return {"message": "Invalid transaction signature."}


class MineRequest(BaseModel):
    miner_address: str

@app.post("/mine/")
def mine(data: MineRequest):
    success = node.mine_block(data.miner_address)
    if success:
        return {"message": "Block mined successfully."}
    else:
        return {"message": "No transactions to mine."}


@app.get("/chain/")
def get_chain():
    chain_data = []
    for block in node.blockchain.chain:
        chain_data.append({
            "index": block.index,
            "transactions": block.transactions,
            "timestamp": block.timestamp,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })
    return {
        "length": len(chain_data),
        "chain": chain_data
    }


class PeersModel(BaseModel):
    peers: List[str]


@app.post("/peers/register/")
def register_peers(peers_model: PeersModel):
    for peer in peers_model.peers:
        node.register_peer(peer)
    return {"message": "Peers registered successfully.", "peers": node.peers}


@app.get("/consensus/")
def consensus():
    replaced = node.consensus()
    if replaced:
        return {"message": "Chain was replaced by the longest valid chain."}
    else:
        return {"message": "Chain is already the longest valid chain."}


@app.post("/block/receive/")
def receive_block(block_data: dict):
    block = Block(
        index=block_data['index'],
        transactions=block_data['transactions'],
        timestamp=block_data['timestamp'],
        previous_hash=block_data['previous_hash'],
        nonce=block_data['nonce']
    )
    proof = block_data['hash']
    added = node.blockchain.add_block(block, proof)
    if not added:
        node.consensus()
        return {"message": "Block discarded, triggered consensus"}
    else:
        return {"message": "Block added to the chain"}
