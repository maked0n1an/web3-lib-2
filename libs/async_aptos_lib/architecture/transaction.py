from typing import Optional, Union


class Transaction:
    def __init__(
            self,
            version: str,
            tx_hash: str,
            success: bool,
            changes: Optional[list] = None,
            sender: Optional[str] = None,
            nonce: Union[str, int, None] = None,
            max_gas_amount: Optional[int] = None,
            gas_unit_price: Optional[int] = None,
            payload: Optional[dict] = None,
            signature: Optional[dict] = None,
            events: Optional[list] = None,
            tx_type: Optional[str] = None,
    ):
        self.version = version
        self.tx_hash = tx_hash
        self.success = success
        self.changes = changes
        self.sender = sender
        self.nonce = nonce
        self.max_gas_amount = max_gas_amount
        self.gas_unit_price = gas_unit_price
        self.payload = payload
        self.signature = signature
        self.events = events
        self.tx_type = tx_type

        if self.nonce:
            self.nonce = int(self.nonce)
        if self.max_gas_amount:
            self.max_gas_amount = int(self.max_gas_amount)
        if self.gas_unit_price:
            self.gas_unit_price = int(self.gas_unit_price)

    def __str__(self):
        return f'{self.tx_hash}'