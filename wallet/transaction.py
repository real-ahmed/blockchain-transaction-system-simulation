from pydantic import BaseModel


class Transaction(BaseModel):
    sender_public_key: str
    receiver_public_key: str
    amount: float
    signature: str
